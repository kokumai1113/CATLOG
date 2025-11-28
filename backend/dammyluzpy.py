import requests
import time
import random
import datetime

# サーバーのURL（ローカルで動かしている場合）
# ※もしスマホや別のPCから繋ぐなら、ここはPCのIPアドレスに変える必要があります
API_URL = "http://127.0.0.1:8000/update_status"

# 送信する状態のパターン
STATUS_LIST = ["在宅", "在宅", "睡眠中", "食事中", "トイレ", "脱走疑い！"]

def send_data():
    print(f"--- 監視システム起動: {API_URL} に送信します ---")
    
    while True:
        # 1. ランダムに状態を決める（本番ではセンサーの値を使う）
        current_status = random.choice(STATUS_LIST)
        
        # 2. クエリパラメータとしてURLにくっつける
        # 例: http://.../update_status?status=在宅
        url = f"{API_URL}?status={current_status}"
        
        try:
            # 3. データを送信（POST）
            response = requests.post(url)
            
            # 現在時刻
            now = datetime.datetime.now().strftime("%H:%M:%S")

            if response.status_code == 200:
                print(f"[{now}] 送信成功: {current_status}")
            else:
                print(f"[{now}] エラー: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"サーバーに繋がりません... (サーバーは起動していますか？): {e}")

        # 4. 5秒待つ
        time.sleep(5)

if __name__ == "__main__":
    send_data()