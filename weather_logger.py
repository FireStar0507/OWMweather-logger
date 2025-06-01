import os
import csv
import requests
import argparse
from datetime import datetime

# 配置参数
API_KEY = os.getenv('OWM_API_KEY')  # 从环境变量获取API密钥
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
BASE_DIR = "weather_data"

def get_weather_data(city):
    """获取指定城市的天气数据"""
    params = {
        'q': city,
        'lang': 'zh_cn',
        'units': 'metric',
        'APPID': API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as e:
        print(f"API请求失败: {str(e)}")
        return None

def save_to_csv(data, city):
    """保存数据到CSV文件（自动去重）"""
    if not data or data.get('cod') != 200:
        return False
    
    # 确保目录存在
    os.makedirs(BASE_DIR, exist_ok=True)
    
    file_path = os.path.join(BASE_DIR, f"{city}.csv")
    file_exists = os.path.isfile(file_path)
    
    # 提取需要的数据
    record = {
        'dt': data['dt'],
        'timestamp': datetime.utcfromtimestamp(data['dt']).strftime('%Y-%m-%d %H:%M:%S'),
        'temp': data['main']['temp'],
        'feels_like': data['main']['feels_like'],
        'humidity': data['main']['humidity'],
        'pressure': data['main']['pressure'],
        'wind_speed': data['wind']['speed'],
        'weather': data['weather'][0]['description'],
        'clouds': data['clouds']['all'],
        'visibility': data.get('visibility', 'N/A')
    }
    
    # 检查重复记录
    if file_exists:
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            existing_dts = {row['dt'] for row in reader}
        
        if str(record['dt']) in existing_dts:
            print(f"跳过重复记录: {city} @ {record['timestamp']}")
            return False
    
    # 写入CSV
    with open(file_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=record.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(record)
    
    print(f"记录已保存: {city} @ {record['timestamp']}")
    return True

def main():
    parser = argparse.ArgumentParser(description='天气数据记录器')
    parser.add_argument('cities', nargs='+', help='城市名称列表（空格分隔）')
    args = parser.parse_args()
    
    if not API_KEY:
        raise ValueError("缺少OWM_API_KEY环境变量")
    
    for city in args.cities:
        data = get_weather_data(city)
        if data:
            save_to_csv(data, city)

if __name__ == "__main__":
    main()
