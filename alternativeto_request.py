import json

import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.102 Safari/537.36'}
platforms = ["linux", "windows", "mac"]


class AlternativetoRequest:

    @staticmethod
    def get_list_page(platform, page):
        return requests.get(f"https://alternativeto.net/platform/{platform}/?sort=likes&p={page}",
                            headers=headers).content

    @staticmethod
    def get_software_page(url_name):
        return requests.get(f"https://alternativeto.net/software/{url_name}/?platform=linux&sort=likes",
                            headers=headers).content

    @staticmethod
    def get_image(img):
        return requests.get(f"https://d2.alternativeto.net/dist/icons/{img}?width=150&height=150",
                            headers=headers).content

    @staticmethod
    def get_alternatives_by_url_name(url_name):
        soup = BeautifulSoup(AlternativetoRequest.get_software_page(url_name), 'html.parser')
        script = soup.select_one('script#__NEXT_DATA__').contents[0]
        alternatives = json.loads(script)['props']['pageProps']['items']
        data = []
        for i in alternatives:
            data.append(i['id'])
        return data

    def get_list_data(self, platform, page):
        data = []
        page_content = self.get_list_page(platform, page)
        soup = BeautifulSoup(page_content, 'html.parser')
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
