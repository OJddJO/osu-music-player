from kivy.app import *
from kivy.uix.label import Label

class osuplayer(App):

    def build(self):
        self.label = Label(text="Hello world")
        return self.label


app = osuplayer()
app.run()
