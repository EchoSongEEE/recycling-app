from pathlib import Path
from dotenv import load_dotenv

# 패키지 import 될 때 .env 환경변수 올리기
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")