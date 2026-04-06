import pandas as pd
import json
import re
import io
from typing import List, Dict, Any, Optional
from src.presentation.schemas.automation import TestCase

class GPTBridgeService:
    def __init__(self):
        self.super_prompt_template = """
Bạn là một Kỹ sư Kiểm thử Tự động (Senior QA Automation Engineer) chuyên nghiệp. 
Nhiệm vụ của bạn là thiết kế bộ Test Case cho một Agent Browser tự hành.

### 📐 ĐỊNH DẠNG ĐẦU RA (13 CỘT):
Bạn phải xuất kết quả dưới dạng BẢNG (Table) MD hoặc JSON array với các cột sau:
1. Test Case ID | 2. URL | 3. Module / Feature | 4. Test Scenario | 5. Test Case Title | 6. Description | 7. Preconditions | 8. Test Data | 9. Test Steps | 10. Expected Result | 11. Actual Result (Để trống) | 12. Status (Để trống) | 13. Comments / Notes (Để trống)

### 🧠 QUY TẮC VIẾT STEPS (TỐI ƯU CHO AGENT):
1. SỬ DỤNG TỪ KHÓA TRỰC TIẾP: click, type_text, scroll_to, extract_content, hover, press_key.
2. ĐÁNH SỐ THỨ TỰ: Các bước 1, 2, 3...
3. ĐƠN BIẾN (ATOMIC): Mỗi bước chỉ thực hiện một hành động duy nhất.
4. ĐỊNH DANH NHÃN: Gọi tên các nút theo nội dung hiển thị (ví dụ: Click "Đăng nhập").

Dưới đây là dữ liệu thô (raw data) tôi cung cấp. Hãy phân tích và trả về bộ Test Case hoàn chỉnh:
---
{raw_data}
---
"""

    def prepare_prompt(self, df: pd.DataFrame) -> str:
        """Converts a raw dataframe into a GPT prompt."""
        # Convert df to a simple string representation
        raw_data_str = df.to_string(index=False)
        return self.super_prompt_template.format(raw_data=raw_data_str)

    def parse_gpt_output(self, text: str) -> List[TestCase]:
        """Parses GPT output (Markdown Table or JSON) into a list of TestCases."""
        
        # 1. Try parsing as JSON first
        json_match = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                return [TestCase(**item) for item in data]
            except Exception as e:
                print(f"JSON Parse Error: {e}")

        # 2. Try parsing as Markdown Table
        try:
            # Simple Markdown table parser
            lines = [line.strip() for line in text.split('\n') if '|' in line]
            if len(lines) < 2:
                return []
            
            # Extract headers (removing leading/trailing pipes and whitespace)
            headers = [h.strip() for h in lines[0].split('|') if h.strip()]
            
            # Skip the separator line (e.g., |---|---|)
            rows = []
            for line in lines[2:]:
                cells = [c.strip() for c in line.split('|')]
                # Remove empty first/last elements if they exist due to leading/trailing pipes
                if line.startswith('|'): cells = cells[1:]
                if line.endswith('|'): cells = cells[:-1]
                
                if len(cells) >= len(headers):
                    row_dict = {headers[i]: cells[i] for i in range(len(headers))}
                    rows.append(TestCase(**row_dict))
            return rows
        except Exception as e:
            print(f"Markdown Parse Error: {e}")
            return []

    def export_to_excel(self, test_cases: List[TestCase]) -> bytes:
        """Converts test cases back to an Excel file."""
        data = [tc.model_dump(by_alias=True) for tc in test_cases]
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return output.getvalue()
