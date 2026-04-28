import requests
import xml.etree.ElementTree as ET

def fetch_river_data():
    try:
        response = requests.get("https://poskobanjir.dsdadki.web.id/xmldata.xml", timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        for station in root.findall('.//SP_GET_LAST_STATUS_PINTU_AIR'):
            nama = station.find('NAMA_PINTU_AIR')
            if nama is not None and "P.A. KARET 1" in nama.text.upper():
                tinggi = station.find('TINGGI_AIR')
                if tinggi is not None:
                    return float(tinggi.text)
    except Exception:
        pass
    return 0.0

def fetch_rainfall_data():
    try:
        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            "?lat=-6.198&lon=106.810"
            "&appid=57b9c70d05ecc12593cc199c9a2fa4ef"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if 'rain' in data and '1h' in data['rain']:
            return float(data['rain']['1h'])
    except Exception:
        pass
    return 0.0
