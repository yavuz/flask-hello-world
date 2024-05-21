from flask import Flask, jsonify
import requests
import json
import threading
import time
#from flask_cors import CORS  # CORS eklentisi

app = Flask(__name__)
#CORS(app)  # CORS eklentisini uygula
json_file = "doviz.json"

appHasRunBefore:bool = False

def download_and_save_json(url, file_path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"JSON dosyası başarıyla indirildi ve kaydedildi: {file_path}")
        else:
            print(f"Hata: HTTP {response.status_code} - {response.reason}")
    except Exception as e:
        print(f"Hata: {e}")

def update_json_periodically(url, file_path, interval):
    while True:
        download_and_save_json(url, file_path)
        time.sleep(interval)

@app.route('/doviz')
def get_doviz():
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
            return jsonify(data)
    except FileNotFoundError:
        return "Hata: JSON dosyası bulunamadı.", 404

@app.before_request
def start_update_thread():
    global appHasRunBefore
    if not appHasRunBefore:
        # İlk indirme ve ardından belirli aralıklarla güncelleme işlemi için bir thread başlatın
        download_thread = threading.Thread(target=update_json_periodically, args=("https://api.genelpara.com/embed/doviz.json", json_file, 300))
        download_thread.daemon = True
        download_thread.start()
        # Set the bool to True so this method isn't called again
        appHasRunBefore = True