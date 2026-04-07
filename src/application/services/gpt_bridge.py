import pandas as pd
import json
import re
import io
from typing import List, Dict, Any, Optional
from src.presentation.schemas.automation import TestCase
from src.prompts.gpt_bridge_prompts import GPT_BRIDGE_SUPER_PROMPT

class GPTBridgeService:
    # Standard 13-column order as specified in the super prompt
    EXPECTED_COLUMNS = [
        "Test Case ID", "URL", "Module / Feature", "Test Scenario", "Test Case Title", 
        "Description", "Preconditions", "Test Data", "Test Steps", "Expected Result", 
        "Actual Result", "Status", "Comments / Notes"
    ]

    def __init__(self):
        self.super_prompt_template = GPT_BRIDGE_SUPER_PROMPT

    def prepare_prompt(self, df: pd.DataFrame) -> str:
        """Converts a raw dataframe into a GPT prompt."""
        # Convert df to a simple string representation
        raw_data_str = df.to_string(index=False)
        return self.super_prompt_template.format(raw_data=raw_data_str)

    def _clean_markdown(self, value: str) -> str:
        """Removes Markdown links [text](url) and other formatting like <br>."""
        if not isinstance(value, str):
            return value
        # 1. Handle Markdown links: [text](url) -> prefer URL if it starts with http
        value = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: m.group(2) if m.group(2).startswith('http') else m.group(1), value)
        # 2. Convert <br> or <br/> to newlines
        value = re.sub(r'<br\s*/?>', '\n', value, flags=re.IGNORECASE)
        # 3. Re-insert newlines before numbered steps if they got concatenated (e.g. "1. click2. type")
        # Pattern: a digit+dot+space that follows a non-newline character
        value = re.sub(r'(?<!\n)(\d+\.\s)', r'\n\1', value)
        # Remove the leading newline added to step 1 if any
        value = value.lstrip('\n')
        # 4. Strip leading/trailing whitespaces
        return value.strip()

    def _split_by_pipe_count(self, text: str, num_cols: int) -> list:
        """Split a flattened single-line Markdown table into rows by counting pipes.
        
        In a valid Markdown table with N columns, each row has exactly N+1 pipes:
        | col1 | col2 | ... | colN |
        So every N+1 pipes encountered marks the end of one row.
        
        This handles the case where the user copies from a rendered Markdown view
        and pastes into a form, losing all newline characters.
        """
        pipes_per_row = num_cols + 1
        rows = []
        current_start = 0
        pipe_count = 0

        for i, ch in enumerate(text):
            if ch == '|':
                pipe_count += 1
                if pipe_count == pipes_per_row:
                    row = text[current_start:i + 1].strip()
                    if row:
                        rows.append(row)
                    current_start = i + 1
                    pipe_count = 0

        # Handle any remaining text that didn't reach a full row boundary
        remaining = text[current_start:].strip()
        if remaining and '|' in remaining:
            rows.append(remaining)

        return rows

    def parse_gpt_output(self, text: str) -> List[TestCase]:
        """Parses GPT output (Markdown Table or JSON) into a list of TestCases."""
        if not text:
            return []
            
        # 0. Pre-cleaning: handle literal '\n' strings if sent via API/curl
        text = text.replace('\\n', '\n')
            
        # 1. Try parsing as JSON first
        json_match = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                print(f"--- [GPT Bridge] Parsed {len(data)} items from JSON ---")
                return [TestCase(**item) for item in data]
            except Exception as e:
                print(f"--- [GPT Bridge] JSON Parse Error: {e} ---")

        # 2. Try parsing as Markdown Table
        try:
            # Normalize line endings
            text = text.replace('\r\n', '\n')

            # FLATTENED TABLE DETECTION:
            # When user copies from a rendered Markdown view (GitHub, chat, VS Code preview),
            # newlines between rows get stripped. The entire table becomes ONE long line.
            # Solution: count pipes — each row of a 13-col table has exactly 14 pipes.
            stripped = text.strip()
            if '\n' not in stripped and stripped.count('|') > len(self.EXPECTED_COLUMNS):
                print(f"--- [GPT Bridge] Detected flattened table ({stripped.count('|')} pipes). Splitting by pipe count ({len(self.EXPECTED_COLUMNS)+1} pipes/row). ---")
                lines = self._split_by_pipe_count(stripped, len(self.EXPECTED_COLUMNS))
            else:
                lines = [line.strip() for line in text.split('\n') if line.strip() and '|' in line]

            
            if len(lines) < 2:
                print(f"--- [GPT Bridge] Not enough table lines found: {len(lines)} ---")
                return []
            
            # Detect header row
            header_line = lines[0]
            raw_headers = [h.strip() for h in header_line.split('|') if h.strip()]
            print(f"--- [GPT Bridge] Detected Headers: {raw_headers} ---")
            
            # Skip separator line (---)
            start_row_idx = 1
            if start_row_idx < len(lines) and '---' in lines[start_row_idx]:
                start_row_idx += 1
                
            rows = []
            for line in lines[start_row_idx:]:
                # ROBUST STRIPPING: ensure we handle leading/trailing pipes correctly
                line = line.strip()
                if not line: continue
                
                # Split and normalize cells
                raw_cells = line.split('|')
                
                # If the line starts/ends with |, split() adds empty strings at the ends
                if line.startswith('|'): raw_cells = raw_cells[1:]
                if line.endswith('|'): raw_cells = raw_cells[:-1]
                
                # Strip each cell
                cells = [self._clean_markdown(c.strip()) for c in raw_cells]
                
                # MAPPING LOGIC: Prioritize INDEX-BASED mapping for 13 columns
                row_dict = {}
                
                # Map by index using our fixed expected order
                for i, field_alias in enumerate(self.EXPECTED_COLUMNS):
                    if i < len(cells):
                        row_dict[field_alias] = cells[i]
                
                # FALLBACK: If we have captured headers, check if they map to any fields 
                # (in case GPT reordered columns but kept correct names)
                if len(cells) != len(self.EXPECTED_COLUMNS):
                    print(f"--- [GPT Bridge] Column count mismatch: {len(cells)} vs 13. Using header fallback. ---")
                    for i, header in enumerate(raw_headers):
                        if i < len(cells):
                            cleaned_header = header.lower().strip()
                            # Find the matching alias in our expected list
                            for expected in self.EXPECTED_COLUMNS:
                                if expected.lower() in cleaned_header or cleaned_header in expected.lower():
                                    row_dict[expected] = cells[i]
                                    break

                if row_dict:
                    try:
                        rows.append(TestCase(**row_dict))
                    except Exception as ve:
                        print(f"--- [GPT Bridge] Validation Error for row: {ve} ---")

            print(f"--- [GPT Bridge] Successfully parsed {len(rows)} test cases from Table ---")
            return rows
        except Exception as e:
            print(f"--- [GPT Bridge] Table Parse Error: {e} ---")
            import traceback
            traceback.print_exc()
            return []

    def export_to_excel(self, test_cases: List[TestCase]) -> bytes:
        """Converts test cases back to an Excel file."""
        data = [tc.model_dump(by_alias=True) for tc in test_cases]
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return output.getvalue()
