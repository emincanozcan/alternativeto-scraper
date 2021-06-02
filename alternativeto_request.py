import json
import time

import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.102 Safari/537.36'}
platforms = ["linux", "windows", "mac"]

pardus_ignore_list = ['Ekiga', "Xfce", 'Freelancer.com', 'Zent.io', 'Cloudron', 'Awes.io', 'Ubuntu Update Manager',
                      'AddThis', 'Chrome PDF Viewer Plug-in', 'Nylas Mail', 'Vesta Control Panel', 'Solus',
                      'Self-Destructing Cookies', 'Ruby on Rails', 'Tomboy', 'Video DownloadHelper', 'Agar.io',
                      'Dolphin File Manager', 'GnuPG', 'gnome-disk-utility', 'trolCommander', 'LastPass',
                      'Grafana', 'django CMS', 'Comix', 'Tree Style Tab', 'xournal', 'Google Desktop', 'Tribler',
                      'HumHub', 'React', 'MultiBootUSB', 'Salesflare', 'Pencil', 'Phoenix OS', 'Zorin OS',
                      'BlueGriffon', 'CodeIgniter', 'recordMyDesktop', 'PS3 Media Server', 'OneTab', 'ClearOS',
                      "Shaarli", 'KeepNote', 'pandoc', 'Mame', 'Synkron', 'CoffeeScript', 'LÖVE', "7-Zip", "µTorrent",
                      "Ubuntu", "Inkscape", "WordPress", "Foxit Reader", "JDownloader", "WinRAR", 'Magento', 'NameCoin',
                      'Peercoin', "Debian", "Google Earth", "Linux Mint", "f.lux", "TrueCrypt", "DownThemAll",
                      "Google Keep", "diagrams.net", "UNetbootin", "Spideroak One Backup", "Arch Linux", "GitLab",
                      "Dogecoin", 'IssueHunt', 'DigitalOcean', 'Vultr', 'FVD Speed Dial', 'Linode', 'Heroku', 'grep',
                      "GOG.com", "Bitcoin", 'LXDE', 'BitMeter OS', 'Update Manager', 'Firefox PDF Viewer (PDF.js)',
                      "FreeMind", "Fedora", "JavaScript", "Litecoin", "elementary OS", 'KDE Plasma', 'React Native',
                      "Apache Cordova", "SoftMaker FreeOffice", 'Greasemonkey', "Remember The Milk", 'Diaspora',
                      'Hotspot Shield', 'Chrome Remote Desktop', 'MediaFire',
                      "openSUSE", "Humble Bundle", "Xubuntu", "phpMyAdmin", "Manjaro Linux", "Vuze", "Firefox Sync",
                      "Kubuntu", "Maxthon Cloud Browser", "Hiren’s BootCD", "Linux kernel", "Miro", "Lubuntu", "Webmin",
                      "Kali Linux", "Firefox Nightly", "GNU Bourne Again SHell", "Cinnamon", "Gnome Do", "GNOME",
                      "Ubuntu Touch", "RankHacker.com", "Konsole", "GNOME Terminal", "Guake terminal", "Terminator",
                      "Konqueror", "GNOME Web", "GNU nano", "Kate", "BitNami Application Stacks",
                      "GRUB", "Android-x86", "uMatrix", "SimilarSites", "Desura", "Empathy", 'pacman (package manager)',
                      'PrestaShop', "Google Chrome Developer Tools", "Cheat Engine", "Markdown", "VisualBoyAdvance",
                      "CentOS", "Zend Studio", "tcpdump", "netcat", "cURL", "Neofetch",
                      "Gentoo", "MATE", "SteamOS", "Google Workspace", "Docky", "KompoZer", "Google Chrome OS",
                      "FrostWire", "Chrome Web Store", "Jenkins", "MinGW", "itch.io", "Ungoogled Chromium", "Tomahawk",
                      "GIMPshop", "FreeRapid Downloader", "UMPlayer", "AngularJS", "Red Hat Enterprise Linux", "cPanel",
                      "Aegisub", "XChat for Linux", "SimilarWeb", "Django", "Reveal.js", "Gwibber", "Electron", "Plesk",
                      "RedshiftGUI", "Scrapy", "OpenShift", "Ethereum", "Ubuntu MATE", "Puppy Linux", "Tesseract",
                      "MediCat USB", "Joli OS", "phpBB", "Qubes OS", "VMmanager", "Raspberry Pi OS", 'Invidious',
                      "Snap Store", "Puppet", 'Visual Understanding Environment', 'Laravel', 'aTunes', 'dd', 'Dukto R6',
                      'YunoHost', 'Electrum', 'aptitude', 'TED', 'Lightning Calendar', 'Yandex.Disk', 'Yandex.Browser',
                      'ImageMagick', ]


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
    def get_app_data_by_url_name(url_name):
        soup = BeautifulSoup(AlternativetoRequest.get_software_page(url_name), 'html.parser')
        category = soup.select_one('div#mainContent nav ol li:nth-of-type(2) a span').text
        script = soup.select_one('script#__NEXT_DATA__').contents[0]
        alternatives = json.loads(script)['props']['pageProps']['items']
        data = {"alternatives": [], "category": category}

        for i in alternatives:
            data['alternatives'].append(i['id'])
        return data

    def get_list_data(self, platform, page):
        try:
            data = []
            page_content = self.get_list_page(platform, page)
            soup = BeautifulSoup(page_content, 'html.parser')
            script = soup.select_one('script#__NEXT_DATA__').contents[0]
            items = json.loads(script)['props']['pageProps']['items']
            for item in items:

                data_obj = {'name': item['name'].strip(), 'likes': item['likes'], 'img': 'not_found',
                            'urlName': item['urlName'],
                            'id': item['id'], 'alternativeIds': [], 'category': 'not_found'}

                if data_obj['likes'] < 30:
                    continue

                for platform in platforms:
                    data_obj[platform] = False

                for item_platform in item['platforms']:
                    for platform in platforms:
                        if item_platform['name'].lower() == platform:
                            data_obj[platform] = True

                if data_obj['name'].strip() in pardus_ignore_list and data_obj['linux'] is True:
                    continue

                for image in item['images']:
                    if image['type'] == "Icon" and len(image['fileName']) > 0:
                        data_obj['img'] = image['fileName']

                data.append(data_obj)

            return data
        except:
            print("Retry: ", platform, " ", page)
            time.sleep(3)
            return AlternativetoRequest.get_list_page(platform, page)
