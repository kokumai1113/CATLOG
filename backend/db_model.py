from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

# ---------------------------------------------------------
# ↓ここをあなたのSupabaseのURLに書き換えてください
# 注意: 先頭が "postgres://" なら "postgresql://" に直してください (qlを足す)
# ---------------------------------------------------------
DATABASE_URL = "postgresql://postgres.bomxhhphdvnumiqoquob:CATLOG-Siraisilab2025@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

# Supabase(PostgreSQL)用の設定
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# 1. 猫の状態テーブル
class CatStatus(Base):
    __tablename__ = "cat_status"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String) 
    battery_level = Column(Integer, default=100)
    last_updated = Column(DateTime, default=datetime.now)

# 2. 動画テーブル
class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    duration = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)

if __name__ == "__main__":
    try:
        # テーブルを作成する命令
        Base.metadata.create_all(bind=engine)
        print("--------------------------------------------------")
        print("【成功】Supabase(クラウド)にテーブルを作成しました！")
        print("Supabaseの管理画面をリロードして確認してください。")
        print("--------------------------------------------------")
    except Exception as e:
        print("【エラー】接続に失敗しました...")
        print(e)