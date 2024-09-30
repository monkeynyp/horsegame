import requests

# 設置API接口的URL和相關參數
url = 'https://api.hkjc.com/racing/info/v1/racecard'
params = {
    'date': '2024-09-28',
    'venue': 'ST'
}

# 發送GET請求獲取賽馬資訊
response = requests.get(url, params=params)

# 解析JSON格式的資料
data = response.json()

# 獲取相關的賽馬資訊
for race in data['racecard']['races']:
    race_number = race['raceNumber']
    race_name = race['raceName']
    print(f'Race {race_number}: {race_name}')
    for horse in race['raceEntries']:
        horse_number = horse['horseNumber']
        horse_name = horse['horseName']
        print(f'{horse_number}. {horse_name}')