import requests
import json

user_name = 'GeekBrainsTutorial'
main_url = f'https://api.github.com/users/{user_name}/repos'
header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
          'Accept':'application/vnd.github.v3+json'}

response = requests.get(main_url, headers=header)


if response.ok:
    data = json.loads(response.text)


repos = []
for i in data:
    repos.append(i['name'])

print(f'У пользователя {user_name} имеется {len(repos)} репозиториев. Список репозиториев: ', *repos, sep='\n')

