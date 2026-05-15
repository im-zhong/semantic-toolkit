from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

API_TITLE = "中图分类法科技文献自动分类API"
API_DESCRIPTION = "基于智谱AI和中图分类法的科技文献自动分类服务"
API_VERSION = "1.0.0"

API_FIXED_MODEL = "glm-4-flash"
API_FIXED_TOP_K = 80

DEFAULT_JSON_PATH = BASE_DIR / "data" / "clc_categories.json"