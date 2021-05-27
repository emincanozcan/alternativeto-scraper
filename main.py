import json
import os
import requests
from bs4 import BeautifulSoup
import time
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.102 Safari/537.36'}
platforms = ["linux", "windows", "mac"]


def get_list_page(platform, page):
    return requests.get(f"https://alternativeto.net/platform/{platform}/?sort=likes&p={page}", headers=headers).content


def get_software_page(url_name):
    return requests.get(f"https://alternativeto.net/software/{url_name}/", headers=headers).content


def get_list_data(platform, page):
    data = []
    soup = BeautifulSoup(get_list_page(platform, page), 'html.parser')
    script = soup.select_one('script#__NEXT_DATA__').contents[0]
    items = json.loads(script)['props']['pageProps']['items']

    for item in items:
        data_obj = {'name': item['name'], 'likes': item['likes'], 'img': 'not_found', 'urlName': item['urlName'],
                    'id': item['id']}

        for platform in platforms:
            data_obj[platform] = False

        for item_platform in item['platforms']:
            for platform in platforms:
                if item_platform['name'].lower() == platform:
                    data_obj[platform] = True

        for image in item['images']:
            if image['type'] == "Icon":
                data_obj['img'] = image['fileName']

        data.append(data_obj)

    return data


def generate_app_list_data():
    result = []
    for i in range(3):  # 350
        for p in platforms:
            print(f"Platform: {p} PAGE: {i + 1}")
            result.extend(get_list_data(p, i + 1))

    for app in result:
        with open(get_app_data_path(app['id']), 'w') as outfile:
            json.dump(app, outfile)


def get_app_data_path(appId):
    return 'data-app-list/' + appId + '.json'


def get_alternatives_by_url_name(url_name):
    soup = BeautifulSoup(get_software_page(url_name), 'html.parser')
    script = soup.select_one('script#__NEXT_DATA__').contents[0]
    alternatives = json.loads(script)['props']['pageProps']['items']
    data = []
    for i in alternatives:
        data.append(i['alternativeId'])
    return data


def add_alternatives_data():
    files = os.listdir('data-app-list')

    i = 0
    for file_name in files:
        i += 1
        print(f'Fetching alternatives data of: {i}/{len(files)}')
        file_path = 'data-app-list/' + file_name
        with open(file_path, 'r') as file:
            json_data = json.loads(file.read())
            json_data['alternativeIds'] = get_alternatives_by_url_name(json_data['urlName'])

        with open(file_path, 'w') as file:
            json.dump(json_data, file)


if __name__ == '__main__':
    start = time.time()
    if os.path.isdir('data-app-list') is False:
        os.mkdir('data-app-list')

    generate_app_list_data()
    add_alternatives_data()
    end = time.time()
    print(f"Runtime is {end - start}")