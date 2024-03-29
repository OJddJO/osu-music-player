class bc:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from os.path import exists
from os import mkdir
from plyer import notification

class Downloader:

    def __init__(self):
        self.app = QApplication([])

        self.view = QWebEngineView()

        def _downloadRequested(item):
            print(f"{bc.OKCYAN}[DOWNLOAD]{bc.ENDC} Download Started:", item.url().toString())
            notification.notify(
                title="osu!player - Song downloader",
                message=f"Download Started: {item.url().toString()}",
                app_icon="osu-icon-28.ico",
                timeout=2
            )
            item.setDownloadDirectory("temp")
            item.accept()

            try:
                item.finished.connect(lambda: _downloadFinished(item))
            except Exception as e:
                print(f"{bc.FAIL}[ERROR]{bc.ENDC}", e)

        def _downloadFinished(item):
            print(f"{bc.OKGREEN}[DOWNLOAD]{bc.ENDC} Download Finished:", item.url().toString())
            notification.notify(
                title="osu!player - Song downloader",
                message=f"Download Finished: {item.url().toString()}",
                app_icon="osu-icon-28.ico",
                timeout=2
            )

        self.view.page().profile().downloadRequested.connect(_downloadRequested)

    def run(self):
        
        if not exists("temp"):
            mkdir("temp")

        self.view.load(QUrl("https://osu.ppy.sh/beatmapsets"))

        self.view.setWindowTitle("osu!player - Song downloader")
        self.view.setWindowIcon(QIcon('osu-icon-28.ico'))
        self.view.show()

        self.app.exec()

        #extract all .osz files
        import os
        import zipfile

        if len(os.listdir("temp")) == 0:
            print(f"{bc.OKCYAN}[INFO]{bc.ENDC}", "No files to extract")
        else:
            print(f"{bc.OKCYAN}[INFO]{bc.ENDC}", "Extracting files...")
            for file in os.listdir("temp"):
                try:
                    #change extension to .zip
                    src = f"temp/{file.replace('.osz', '.zip')}"
                    os.rename(f"temp/{file}", src)
                    #extract
                    path = open("path.data").read()
                    dest = f"{path}/{file.replace('.osz', '')}"
                    os.mkdir(dest)
                    zipfile.ZipFile(src).extractall(dest)
                    #delete .zip
                    os.remove(src)
                    print(f"{bc.OKGREEN}[INFO]{bc.ENDC}", "Extracted", file)
                except Exception as e:
                    print(f"{bc.FAIL}[ERROR]{bc.ENDC}", "Failed to extraxt", file, ":", e)
                    try:
                        os.remove(src)
                    except Exception as e:
                        print(f"{bc.FAIL}[ERROR]{bc.ENDC}", "Failed to delete", src, ":", e)
            print(f"{bc.OKCYAN}[INFO]{bc.ENDC}", "Done extracting files")

if __name__ == "__main__":
    app = Downloader()
    app.run()
    app.run()