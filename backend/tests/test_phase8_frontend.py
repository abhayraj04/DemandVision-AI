"""
Phase 8 Test Suite: Frontend Production Build Verification
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")


def test_frontend_dist_exists():
    assert os.path.exists(FRONTEND_DIST), "frontend/dist directory missing"
    index_html = os.path.join(FRONTEND_DIST, "index.html")
    assert os.path.exists(index_html), "dist/index.html missing"
    assert os.path.getsize(index_html) > 100, "dist/index.html is suspiciously empty"


def test_frontend_assets_generated():
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    assert os.path.exists(assets_dir), "dist/assets directory missing"
    files = os.listdir(assets_dir)
    js_files = [f for f in files if f.endswith(".js")]
    css_files = [f for f in files if f.endswith(".css")]
    assert len(js_files) >= 1, "Compiled JS bundle missing"
    assert len(css_files) >= 1, "Compiled CSS bundle missing"
