import os
import sys
import requests
import csv
from datetime import datetime

API_KEY = os.getenv('OWM_API_KEY')
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_weather_data(city):
    params = {
        'q': city,
        'lang': 'zh_cn',
        'units': 'metric',
        'APPID': API_KEY
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {e}")
        return None

def save_to_csv(data, city):
    filename = f"{city}.csv"
    file_exists = os.path.isfile(filename)
    
    # 选择需要的字段
    fields = [
        'dt', 'name',
        ('main', 'temp'), ('main', 'humidity'),
        ('main', 'feels_like'), ('main', 'pressure'),
        ('wind', 'speed'), ('wind', 'deg'),
        ('weather', 0, 'description'), ('clouds', 'all')
    ]

    # 构建行数据
    row = {}
    for field in fields:
        if isinstance(field, tuple):
            value = data
            try:
                for part in field:
                    value = value[part] if isinstance(value, (dict, list)) else value
                row['_'.join(map(str, field))] = value
            except (KeyError, IndexError):
                row['_'.join(map(str, field))] = None
        else:
            row[field] = data.get(field)

    # 添加本地时间
    dt = datetime.fromtimestamp(row['dt'] + data['timezone'])
    row['local_time'] = dt.isoformat()

    # 写入CSV
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("请指定城市名称，例如: python weather_logger.py Foshan")
        sys.exit(1)
    
    city = sys.argv[1]
    for c in city:
      data = get_weather_data(c)
      if data and data.get('cod') == 200:
          save_to_csv(data, c)
          print(f"数据已保存到 {c}.csv")
      else:
          print("获取天气数据失败")
          sys.exit(1)
