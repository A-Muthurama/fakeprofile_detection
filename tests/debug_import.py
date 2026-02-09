
import sys
import os
import traceback

# Add app directory to path
sys.path.insert(0, os.path.join(os.getcwd(), 'app'))
sys.path.insert(0, os.getcwd())

print(f"Python executable: {sys.executable}")
print(f"Current working directory: {os.getcwd()}")
print(f"Path: {sys.path}")

try:
    print("Attempting to import AnalyzerService...")
    from services.analyzer_service import AnalyzerService
    print("Successfully imported AnalyzerService")
    
    print("Attempting to initialize AnalyzerService...")
    service = AnalyzerService()
    print("Successfully initialized AnalyzerService")
    
except ImportError as e:
    print(f"\nCRITICAL IMPORT ERROR: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"\nCRITICAL RUNTIME ERROR: {e}")
    traceback.print_exc()
