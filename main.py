import time

from data_generator import DataGenerator
from storage_orchestrator import StorageOrchestrator

if __name__ == '__main__':
    start = time.time()

    StorageOrchestrator.create_folders()
    DataGenerator.generate_app_data_multi_thread(start_page=1, end_page=10)
    DataGenerator.generate_alternatives_data_multi_thread(8)
    DataGenerator.generate_images_multi_thread(8)

    end = time.time()
    print(f"Runtime is {end - start}")
