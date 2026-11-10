"""
MarketVision AI - Streamlit Application Entrypoint
Ready for 1-click deployment on Streamlit Community Cloud (share.streamlit.io).
"""
import os
import runpy
import sys

# Ensure current working directory is on path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Delegate directly to streamlit_app.py
target_script = os.path.join(BASE_DIR, "streamlit_app.py")
runpy.run_path(target_script, run_name="__main__")
