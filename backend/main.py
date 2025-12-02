from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session, sessionmaker
from db_model import engine, CatStatus # さっき作ったファイルを読み込んでいます
import shutil
import os
from fastapi import File, UploadFile

# データベースに接続するための設定（呪文のようなもの）
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

# データベースを使うための便利機能
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ここからが「窓口」の設計です ---

# 1. 動作確認用
@app.get("/")
def index():
    return {"message": "Cat Monitor System is Running!"}

# 2. 【ラズパイ役】猫の状態を書き込む窓口
# ブラウザで /update_status?status=脱走 とアクセスすると記録されます
@app.post("/update_status")
def update_status(status: str, db: Session = Depends(get_db)):
    # 新しい状態データを作成
    new_data = CatStatus(status=status)
    # DBに追加して保存
    db.add(new_data)
    db.commit()
    return {"message": f"状態を「{status}」に更新しました！"}

# 3. 【アプリ役】最新の状態を見る窓口
@app.get("/current_status")
def get_status(db: Session = Depends(get_db)):
    # IDが一番大きい（＝最新の）データを1つ取ってくる
    latest_data = db.query(CatStatus).order_by(CatStatus.id.desc()).first()
    return latest_data

# 動画を保存するフォルダを作成
UPLOAD_DIR = "uploaded_videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload_video")
async def upload_video(file: UploadFile = File(...)):
    """
    ラズパイから動画を受け取って保存するAPI
    """
    # 1. 保存するファイルパスを決める
    # 重複しないように日時にするとベストですが、一旦ファイル名そのまま使います
    save_path = f"{UPLOAD_DIR}/{file.filename}"
    
    # 2. サーバーの中にファイルを保存する
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 3. 本来はここで「DBへの記録」もやりますが、まずは保存まで
    
    return {"filename": file.filename, "message": "動画を受け取りました！"}