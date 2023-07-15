from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from os.path import exists
from os import mkdir

class Downloader:

    def __init__(self):

        self.app = QApplication([])

        self.view = QWebEngineView()
        
        if not exists("temp"):
            mkdir("temp")

        def _downloadRequested(item):
            print("[DOWNLOAD] Download Started:", item.url().toString())
            item.setDownloadDirectory("temp")
            item.accept()

            try:
                item.finished.connect(lambda: _downloadFinished(item))
            except Exception as e:
                print("[ERROR]", e)

        def _downloadFinished(item):
            print("[DOWNLOAD] Download Finished:", item.url().toString())

        self.view.page().profile().downloadRequested.connect(_downloadRequested)

        self.view.load(QUrl("https://osu.ppy.sh/beatmapsets"))

        self.view.setWindowTitle("osu!player - Song downloader")
        self.view.setWindowIcon(QIcon('osu-icon-28.ico'))
        self.view.show()

    def run(self):

        self.app.exec_()

        #extract all .osz files
        import os
        import zipfile

        if len(os.listdir("temp")) == 0:
            print("[INFO] No files to extract")
        else:
            print("[INFO] Extracting files...")
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
                except Exception as e:
                    print("[ERROR]", "Failed to extraxt", file, ":", e)
            print("[INFO] Done extracting files")

if __name__ == '__main__':
    downloader = Downloader()
    downloader.run()
