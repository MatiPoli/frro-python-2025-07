from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown


class CustomDropdown(DropDown):
    pass


class MainButton(Button):
    def __init__(self, **kwargs):
        super(MainButton, self).__init__(**kwargs)
        self.dropdown = CustomDropdown()
        self.dropdown.bind(on_select=self.update_text)

    def update_text(self, dropdown, selection):
        self.text = selection

    def on_release(self):
        self.dropdown.open(self)


class DropDownApp(App):
    def build(self):
        return MainButton()


if __name__ == '__main__':
    DropDownApp().run()