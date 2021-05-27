import threading

from alternativeto_request import AlternativetoRequest
from chunk_list import chunk_list
from storage_orchestrator import StorageOrchestrator

platforms = ["linux", "windows", "mac"]


class DataGenerator:

    @staticmethod
    def generate_app_data(platform, start_page, end_page):
        for i in range(start_page, end_page):
            print(f"Platform: {platform} PAGE: {i}")
            app_list = AlternativetoRequest().get_list_data(platform, i)
            for app in app_list:
                StorageOrchestrator.save_app_as_json(app=app)

    @staticmethod
    def generate_alternatives_data(file_names, index=0):
        for i in range(len(file_names)):
            print(f'Thread: {index} - Process: {i} / {len(file_names)}')
            app_id = StorageOrchestrator.get_app_id_by_file_name(file_name=file_names[i])
            app = StorageOrchestrator.get_json_by_app_id(app_id=app_id)

            alternative_ids = []
            if app['linux'] is True:
                alternative_ids = [app['id']]
            else:
                fetched_alternative_ids = AlternativetoRequest.get_alternatives_by_url_name(app['urlName'])
                tmp = []
                for alternative_id in fetched_alternative_ids:
                    if StorageOrchestrator.is_app_exists(app_id=alternative_id):
                        alternative_app = StorageOrchestrator.get_json_by_app_id(app_id=alternative_id)
                        if alternative_app['linux'] is True:
                            tmp.append({'id': alternative_app['id'], 'likes': alternative_app['likes']})

                tmp = sorted(tmp, key=lambda k: k['likes'], reverse=True)
                if len(tmp) > 3:
                    tmp = tmp[0:3]
                for t in tmp:
                    alternative_ids.append(t['id'])

            app['alternativeIds'] = alternative_ids
            StorageOrchestrator.save_app_as_json(app=app)

    @staticmethod
    def generate_alternatives_data_multi_thread(thread_count):
        files = StorageOrchestrator.get_app_files_list()
        threads = []
        file_groups = chunk_list(files, thread_count)
        for index in range(len(file_groups)):
            t = threading.Thread(target=DataGenerator.generate_alternatives_data, args=(file_groups[index], index))
            threads.append(t)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    @staticmethod
    def generate_app_data_multi_thread(start_page, end_page):
        threads = []

        for platform in platforms:
            t = threading.Thread(target=DataGenerator.generate_app_data,
                                 args=(platform, start_page, end_page))
            threads.append(t)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    @staticmethod
    def generate_images(file_list, index):
        for i in range(len(file_list)):
            print(f'Thread: {index} - Process: {i} / {len(file_list)}')
            file_name = file_list[i]
            app_id = StorageOrchestrator.get_app_id_by_file_name(file_name=file_name)
            app = StorageOrchestrator.get_json_by_app_id(app_id=app_id)
            img = app['img']
            if img != 'not_found' and len(img) > 0:
                fetched_img = AlternativetoRequest.get_image(img)
                StorageOrchestrator.save_image(img_data=fetched_img, img_name=img)

    @staticmethod
    def generate_images_multi_thread(thread_count):
        files = StorageOrchestrator.get_app_files_list()
        threads = []
        file_groups = chunk_list(files, thread_count)
        for index in range(len(file_groups)):
            t = threading.Thread(target=DataGenerator.generate_images, args=(file_groups[index], index))
            threads.append(t)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
