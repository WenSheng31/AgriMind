import shutil
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session
from .config import settings
from .database import engine, Base, SessionLocal
from ..models.user import User
from ..models.agriculture import Farm, SensorData, Operation, ImageRecord, ImageRecordFile
from ..models.knowledge import KnowledgeDocument
from ..models.chat_log import ChatLog

SEED_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "db" / "seed_data.sql"
SEED_UPLOADS_PATH = Path(__file__).resolve().parent.parent.parent / "db" / "seed_uploads"


def init_db():
    """初始化資料庫：建立資料表"""
    # 0. 啟用 pgvector 擴充
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    # 1. 建立所有資料表
    Base.metadata.create_all(bind=engine)

    # 2. 全新資料庫（farms 表為空）時，自動匯入範例資料
    _seed_demo_data_if_empty()

    print("Database initialized. Admin will be assigned via ADMIN_EMAILS env var on first Google login.")


def _seed_demo_data_if_empty():
    """僅在 farms 表尚無資料時匯入 seed_data.sql，避免覆蓋既有資料"""
    if not SEED_DATA_PATH.exists():
        return

    with SessionLocal() as db:
        if db.query(Farm.id).first() is not None:
            return

    # 用原生 DBAPI cursor 執行：seed 內文含有 '%'（如「濕度 90%」），
    # 經 SQLAlchemy 的 exec_driver_sql 執行會被 psycopg2 當成參數佔位符而報錯；
    # cursor.execute() 不帶參數時不做任何 '%' 解析。
    sql = SEED_DATA_PATH.read_text(encoding="utf-8")
    raw_conn = engine.raw_connection()
    try:
        with raw_conn.cursor() as cursor:
            cursor.execute(sql)
            # seed_data.sql（pg_dump 輸出）會把 session 層級的 search_path 清空成
            # 空字串，交易結束後這個連線會被放回連線池；若不還原，之後任何
            # 請求若剛好拿到這條連線，未加 schema 前綴的查詢（如 SQLAlchemy
            # ORM 產生的 `FROM users`）會找不到表。這裡在歸還連線前還原設定。
            cursor.execute("SET search_path TO public")
        raw_conn.commit()
    finally:
        raw_conn.close()

    _copy_seed_uploads()

    print(f"Seeded demo data from {SEED_DATA_PATH.name}")


def _copy_seed_uploads():
    """把範例影像檔複製到 uploads 目錄，讓 seed 的 image_records 圖片連結有效"""
    if not SEED_UPLOADS_PATH.exists():
        return
    shutil.copytree(SEED_UPLOADS_PATH, settings.UPLOAD_DIR, dirs_exist_ok=True)


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialization completed!")
