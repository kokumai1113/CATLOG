import cv2
import time
import datetime
from ultralytics import YOLO

# --- [ダミー/プレースホルダー] Bluetooth制御クラス ---
# 実際には bleak や pybluez などのライブラリを使って実装します
class BluetoothManager:
    def __init__(self):
        self.connected = True
        self.rssi = -60  # ダミーの電波強度

    def check_connection(self):
        # TODO: 実際にBluetoothモジュールと通信を行うコードを書く
        # 返り値: (接続状態bool, 距離メートルfloat)
        
        # --- テスト用のダミーロジック ---
        # 実際にはRSSI(電波強度)から距離を推定します
        # 例: 10m以上離れたシチュエーションを作るための仮コード
        # self.rssi = -90 (遠い) / -50 (近い)
        
        is_connected = True   # 通信が切れたら False にする
        estimated_distance = 5.0 # メートル (テスト用: 5m)
        
        return is_connected, estimated_distance

# --- [ダミー/プレースホルダー] データベース制御クラス ---
class DatabaseHandler:
    def send_escape_alert(self):
        # TODO: SQLやAPIを叩いて「脱走」を送信する
        print("【DB送信】警告：通信断絶！脱走の可能性があります。")

    def upload_video(self, file_path):
        # TODO: 録画したファイルをサーバーやクラウドにアップロードする
        print(f"【DB送信】録画データをアップロードしました: {file_path}")

# ==========================================
# メイン処理
# ==========================================

def main():
    # 1. 初期設定
    model = YOLO("yolov8n.pt")
    bt_manager = BluetoothManager()
    db_handler = DatabaseHandler()

    cap = None            # カメラオブジェクト
    video_writer = None   # 録画用オブジェクト
    recording_file = None # 現在録画中のファイル名
    
    is_camera_on = False
    
    print("システム監視を開始します (終了は Ctrl+C)")

    try:
        while True:
            # --- Bluetoothの状態確認 ---
            connected, distance = bt_manager.check_connection()

            # A. 通信が切れた場合 (脱走)
            if not connected:
                db_handler.send_escape_alert()
                # カメラなどが動いていれば停止処理へ
                if is_camera_on:
                    print("通信断絶のためシステムを停止します。")
                    if video_writer:
                        video_writer.release()
                        db_handler.upload_video(recording_file)
                        video_writer = None
                    if cap:
                        cap.release()
                        cap = None
                    is_camera_on = False
                
                time.sleep(1) # 連打防止
                continue

            # B. 通信中：距離判定
            # 10m以上離れている -> カメラOFF
            if distance > 10.0:
                if is_camera_on:
                    print(f"距離が離れました({distance}m)。カメラをOFFにします。")
                    
                    # 録画終了処理
                    if video_writer:
                        video_writer.release()
                        video_writer = None
                        print("録画を停止しました。")
                        # カメラOFFと同時にアップロード
                        if recording_file:
                            db_handler.upload_video(recording_file)
                            recording_file = None

                    # カメラ停止
                    cap.release()
                    cv2.destroyAllWindows()
                    cap = None
                    is_camera_on = False
                
                # 待機 (CPU使用率を下げる)
                time.sleep(1)

            # 10m以内 -> カメラON
            else: # distance <= 10.0
                if not is_camera_on:
                    print(f"接近を検知({distance}m)。カメラを起動します。")
                    cap = cv2.VideoCapture(0)
                    if not cap.isOpened():
                        print("カメラが見つかりません。")
                        time.sleep(1)
                        continue
                    is_camera_on = True

                # --- 映像処理ループ (1フレーム処理) ---
                success, frame = cap.read()
                if not success:
                    continue

                # YOLOで猫検出 (class 15 = cat)
                results = model(frame, classes=[15], conf=0.3, verbose=False)
                annotated_frame = results[0].plot()

                # 猫がいるかチェック
                cat_detected = len(results[0].boxes) > 0

                if cat_detected:
                    print("猫を検知中...録画します")
                    
                    # 録画開始処理 (まだ始まっていない場合)
                    if video_writer is None:
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        recording_file = f"cat_evidence_{timestamp}.mp4"
                        
                        # 動画フォーマット設定 (mp4v)
                        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                        fps = 20.0 # カメラのFPSに合わせる
                        h, w = frame.shape[:2]
                        video_writer = cv2.VideoWriter(recording_file, fourcc, fps, (w, h))
                    
                    # フレームを書き込む
                    video_writer.write(annotated_frame)
                
                # (オプション) 猫がいなくなったら即録画を切るか、
                # あるいは「カメラOFF」までファイルを開きっぱなしにするか。
                # 要件「カメラがoffになると同時に送信」なので、
                # ここではファイルは開きっぱなし（追記モード）にしておきます。

                # 画面表示
                cv2.imshow("Monitoring System", annotated_frame)
                
                # 'q'で強制終了
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    except KeyboardInterrupt:
        print("プログラムを終了します。")

    finally:
        # 終了処理
        if video_writer:
            video_writer.release()
        if cap and cap.isOpened():
            cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()