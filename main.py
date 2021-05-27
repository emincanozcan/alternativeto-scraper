import json
import os
import threading

import requests
from bs4 import BeautifulSoup
import time

# TODO: concurrency of course..
# TODO: refactor... it needs sooooo fucking many refactor...

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.102 Safari/537.36'}
platforms = ["linux", "windows", "mac"]


def chunk_list(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out


def get_list_page(platform, page):
    return requests.get(f"https://alternativeto.net/platform/{platform}/?sort=likes&p={page}", headers=headers).content


def get_software_page(url_name):
    return requests.get(f"https://alternativeto.net/software/{url_name}/?platform=linux&sort=likes",
                        headers=headers).content


def get_image(img):
    return requests.get(f"https://d2.alternativeto.net/dist/icons/{img}?width=150&height=150", headers=headers).content


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
            if image['type'] == "Icon" and len(image['fileName']) > 0:
                data_obj['img'] = image['fileName']

        data.append(data_obj)

    return data


def generate_app_data_by_platform(platform):
    for i in range(150):
        print(f"Platform: {platform} PAGE: {i + 1}")
        app_list = get_list_data(platform, i + 1)
        for app in app_list:
            with open(get_app_data_path(app["id"]), 'w') as outfile:
                json.dump(app, outfile)


def generate_app_data():
    threads = []

    for platform in platforms:
        t = threading.Thread(target=generate_app_data_by_platform, args=(platform,))
        threads.append(t)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


def get_app_data_path(appId):
    return 'app-data/' + appId + '.json'


def get_alternatives_by_url_name(url_name):
    soup = BeautifulSoup(get_software_page(url_name), 'html.parser')
    script = soup.select_one('script#__NEXT_DATA__').contents[0]
    alternatives = json.loads(script)['props']['pageProps']['items']
    data = []
    for i in alternatives:
        data.append(i['id'])
    return data


def generate_alternatives_by_file_name(file_names, index):
    for i in range(len(file_names)):
        print(f'Thread: {index} - Process: {i} / {len(file_names)}')
        file_name = file_names[i]
        file_path = 'app-data/' + file_name
        with open(file_path, 'r') as file:
            json_data = json.loads(file.read())
            alternative_ids = []
            if json_data['linux'] is True:
                alternative_ids = [json_data['id']]
            else:
                fetched_alternative_ids = get_alternatives_by_url_name(json_data['urlName'])
                tmp = []
                for alternative_id in fetched_alternative_ids:
                    alternative_file = 'app-data/' + alternative_id + '.json'
                    if os.path.exists(alternative_file):
                        with open(alternative_file, 'r') as a_file:
                            a_file_data = json.loads(a_file.read())
                            if a_file_data['linux'] is True:
                                tmp.append({'id': a_file_data['id'], 'likes': a_file_data['likes']})
                tmp = sorted(tmp, key=lambda k: k['likes'], reverse=True)
                if len(tmp) > 3:
                    tmp = tmp[0:3]
                for t in tmp:
                    alternative_ids.append(t['id'])

            json_data['alternativeIds'] = alternative_ids

        with open(file_path, 'w') as file:
            json.dump(json_data, file)


def generate_alternatives_data():
    files = os.listdir('app-data')
    thread_count = 8
    threads = []
    file_groups = chunk_list(files, thread_count)
    for index in range(len(file_groups)):
        t = threading.Thread(target=generate_alternatives_by_file_name, args=(file_groups[index], index))
        threads.append(t)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


def save_images(file_list, index):
    for i in range(len(file_list)):
        print(f'Thread: {index} - Process: {i} / {len(file_list)}')
        file_name = file_list[i]
        path = 'app-data/' + file_name
        with open(path, 'r') as file:
            j = json.load(file)
            img_name = j['img']
            if j['img'] != 'not_found' and len(j['img']) > 0:
                fetched_img = get_image(img_name)
                with open('images/' + img_name, 'wb') as img_file:
                    img_file.write(fetched_img)


def fetch_images():
    files = os.listdir('app-data')
    thread_count = 8
    threads = []
    file_groups = chunk_list(files, thread_count)
    for index in range(len(file_groups)):
        t = threading.Thread(target=save_images, args=(file_groups[index], index))
        threads.append(t)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    start = time.time()

    if os.path.isdir('app-data') is False:
        os.mkdir('app-data')
    if os.path.isdir('images') is False:
        os.mkdir('images')

    generate_app_data()
    generate_alternatives_data()
    fetch_images()
    end = time.time()
    print(f"Runtime is {end - start}")
