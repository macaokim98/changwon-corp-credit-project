"""
Streamlit app entry point for Streamlit Community Cloud deployment.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import and run the main app
from changwon_credit.streamlit_mobile_app_light import main

if __name__ == "__main__":
    main()
