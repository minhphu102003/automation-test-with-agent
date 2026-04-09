import sys
import os

# Add current directory to path (simulation of project root in path)
sys.path.insert(0, os.getcwd())

try:
    from src.presentation.schemas.automation import TestCase
    print("Runtime import successful!")
except ImportError as e:
    print(f"Runtime import failed: {e}")
except Exception as e:
    print(f"Other error: {e}")
