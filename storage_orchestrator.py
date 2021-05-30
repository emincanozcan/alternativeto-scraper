import json
import os


class StorageOrchestrator:
    @staticmethod
    def create_folders():
        if os.path.isdir('app-data') is False:
            os.mkdir('app-data')
        if os.path.isdir('images') is False:
            os.mkdir('images')

    @staticmethod
    def save_image(img_name, img_data):
        with open('images/' + img_name, 'wb') as img_file:
            img_file.write(img_data)
        return True

    @staticmethod
    def save_app_as_json(app):
        try:
            with open(f"app-data/{str(app['id'])}.json", 'w') as f:
                json.dump(app, f)
        except:
            print("ID ERROR:", app)
        return True

    @staticmethod
    def get_app_id_by_file_name(file_name):
        return file_name.replace('.json', '')

    @staticmethod
    def get_json_by_app_id(app_id):
        file_path = 'app-data/' + app_id + '.json'
        with open(file_path, 'r') as file:
            return json.loads(file.read())

    @staticmethod
    def is_app_exists(app_id):
        alternative_file = 'app-data/' + app_id + '.json'
        return os.path.exists(alternative_file)

    @staticmethod
    def get_app_files_list():
        return os.listdir('app-data')

    @staticmethod
    def remove_app(app):
        os.remove(f'app-data/{app["id"]}.json')
        os.remove(f'images/{app["img"]}')
