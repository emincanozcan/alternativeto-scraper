import os
import time

from data_generator import DataGenerator
from storage_orchestrator import StorageOrchestrator
from PIL import Image

if __name__ == '__main__':
    start = time.time()

    StorageOrchestrator.create_folders()
    DataGenerator.generate_app_data_multi_thread(start_page=1, end_page=150, thread_count=16)  # thread_count / 3
    DataGenerator.add_fields_to_apps_multi_thread(42)
    DataGenerator.generate_images_multi_thread(42)

    # CLEAR GAMES AND APPS THAT HAS NO ALTERNATIVES
    for file in StorageOrchestrator.get_app_files_list():
        app_id = StorageOrchestrator.get_app_id_by_file_name(file_name=file)
        app = StorageOrchestrator.get_json_by_app_id(app_id=app_id)
        try:
            if (len(app['alternativeIds']) < 1 and app['linux'] is False) or app['category'].lower() == 'games':
                StorageOrchestrator.remove_app(app=app)
        except:
            continue

    # SCALE IMAGES

    images = os.listdir('images')
    for img_name in images:
        img = Image.open('images/' + img_name)
        img = img.resize((72, 72), Image.ANTIALIAS)
        if ".jpg" in img_name or ".jpeg" in img_name:
            img = img.convert('RGB')
        img.save('images/' + img_name)
    end = time.time()
    print(f"Runtime is {end - start}")
