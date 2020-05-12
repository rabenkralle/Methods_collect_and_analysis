from pprint import pprint
import requests
import json

main_url = 'https://api.vk.com/method/video.get'
token = 'deleted' # токен удален. можно подставить свой.
header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
          'Accept':'*/*'}
params = {'access_token': token,
          'v':'5.103',
          'owner_id': '1'
}
response = requests.get(main_url, headers=header, params=params)

if response.ok:
    data = json.loads(response.text)

with open('response_headers.json', 'w', encoding='utf8') as f:
    json.dump(data, f, ensure_ascii=False)

with open('response_headers.json') as f:
    pprint(f.read())