from kivy.app import App
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

# Configura el tamaño de la ventana
Window.size = (720, 400)

# Define la clase principal de la aplicación
class Drop_down_app(App):
    def build(self):
        # Crea un contenedor vertical para organizar los widgets
        box = BoxLayout(orientation='vertical')

        # Crea el botón principal que abrirá el menú
        mainbutton = Button(
            text='Lista Desplegable',
            size_hint=(None, None),  # Desactiva el ajuste automático de tamaño
            size=(250, 75),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        box.add_widget(mainbutton)

        # Crea el menú desplegable
        dropdown = DropDown()
        for index in range(1, 11):  # Crea 10 botones para el menú desplegable
            btn = Button(
                text='Botoncito ' + str(index),
                size_hint_y=None,  # Desactiva el ajuste automático de altura
                height=40  # Altura fija para cada botón
            )
            # Vincula cada botón para que seleccione su texto al ser presionado
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)  # Agrega el botón al menú desplegable

        # Vincula el botón principal para abrir el menú desplegable al ser presionado
        mainbutton.bind(on_release=lambda instance: print("Dropdown opened") or dropdown.open(instance))

        # Vincula el menú desplegable para actualizar el texto del botón principal al seleccionar una opción
        dropdown.bind(on_select=lambda instance, x: setattr(mainbutton, 'text', x))

        return box  # Devuelve el contenedor principal como la raíz de la interfaz

# Ejecuta la aplicación
Drop_down_app().run()