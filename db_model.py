from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

# 最初は手軽な SQLite（ファイル保存）を使います
DATABASE_URL = "sqlite:///./cat_system.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()

# 1. 猫の状態テーブル
class CatStatus(Base):
    __tablename__ = "cat_status"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="在宅") # "在宅", "脱走疑い", "散歩中"
    battery_level = Column(Integer, default=100) # 電池残量も追加してみました
    last_updated = Column(DateTime, default=datetime.now)

# 2. 動画テーブル
class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)         # 動画の保存場所
    duration = Column(Integer)   # 動画の長さ(秒)
    created_at = Column(DateTime, default=datetime.now)

# これを実行するとDBファイルが作られます
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("成功！データベースファイル(cat_system.db)を作成しました。")