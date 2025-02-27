import subprocess
import time

while True:
    # file1.py を実行
    subprocess.run(["python", "/app/app/url_acquisition.py"], check=True)
    print("url_acuisition.pyを実行しました。")
    # file2.py を実行
    subprocess.run(["python", "/app/app/embedd.py"], check=True)
    print("embedd.pyを実行しました。")
    print("今日の記事をすべて取得しました。")
    # 24時間待機（86400秒）
    time.sleep(86400)
