import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from flask import Flask, jsonify
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
DATA_FILE = 'prices.json'
UPDATE_INTERVAL = timedelta(minutes=5)

# Döviz fiyatlarını çekme fonksiyonu
def get_currency_prices():
    url = "https://kur.altin.in/banka"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    #print(soup)
    
    # Döviz fiyatlarını çekeceğimiz tabloyu bulma
    currency_data = {
        "Euro": {"Alis": None, "Satis": None},
        "Dolar": {"Alis": None, "Satis": None}
    }

    euro = soup.find("div", {"title": "Euro"})
    print(euro)
    currency_data["Euro"]["Alis"] = euro.find("li", {"class": "midrow alis"}).text
    currency_data["Euro"]["Satis"] = euro.find("li", {"class": "midrow satis"}).text

    usd = soup.find("div", {"title": "Amerikan Doları"})
    currency_data["Dolar"]["Alis"] = usd.find("li", {"class": "midrow alis"}).text
    currency_data["Dolar"]["Satis"] = usd.find("li", {"class": "midrow satis"}).text
            
    return currency_data

# Altın fiyatlarını çekme fonksiyonu
def get_gold_prices():
    url = "https://altin.in/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Verileri saklamak için boş bir dictionary oluştur
    altin_fiyatlari = {
        "Gram Altın": {"Alis": None, "Satis": None},
        "Çeyrek Altın": {"Alis": None, "Satis": None},
        "Cumhuriyet Altını": {"Alis": None, "Satis": None},
        "22 Ayar Bilezik": {"Alis": None, "Satis": None},
        "Tam Altın": {"Alis": None, "Satis": None}
    }

    # Altın türlerini ve CSS sınıflarını eşleştir
    altin_turleri = {
        "Gram Altın": 'Gram Altın',
        "Çeyrek Altın": 'Çeyrek Altın',
        "Cumhuriyet Altını": 'Cumhuriyet Altını',
        "22 Ayar Bilezik": '22 Ayar Bilezik',
        "Tam Altın": 'Tam Altın'
    }

    # Her altın türü için alış ve satış fiyatlarını al
    for altin_turu, title in altin_turleri.items():
        div = soup.find('div', {'title': title})
        if div:
            alis_fiyati = div.find('li', {'class': 'midrow alis'}).text.strip()
            satis_fiyati = div.find('li', {'class': 'midrow satis'}).text.strip()
            altin_fiyatlari[altin_turu]["Alis"] = alis_fiyati
            altin_fiyatlari[altin_turu]["Satis"] = satis_fiyati

                
    return altin_fiyatlari

def read_prices():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_prices(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def update_prices_if_needed():
    print("Updating prices if needed...")
    data = read_prices()
    last_update = datetime.strptime(data.get('last_update', '1970-01-01T00:00:00'), '%Y-%m-%dT%H:%M:%S')
    if datetime.utcnow() - last_update > UPDATE_INTERVAL:
        print("Updating prices...")
        currency_prices = get_currency_prices()
        gold_prices = get_gold_prices()
        data.update(currency_prices)
        data.update(gold_prices)
        data['last_update'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        save_prices(data)
    return data

@app.route('/prices', methods=['GET'])
def get_prices():
    data = update_prices_if_needed()
    return jsonify(data)

@app.route('/')
def hello_world():
    return 'Today is today!'

if __name__ == '__main__':
    app.run(debug=True)