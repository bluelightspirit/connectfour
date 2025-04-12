import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.uix.image import Image

class GridButton(Button):
    pass

class TestGridLayout(GridLayout):
    pass

class YourApp(App):
     def build(self):
        root_widget = BoxLayout(orientation='vertical')

        output_label = Label(size_hint_y=1)

        piece_grid = GridLayout(cols=7,rows=6,spacing=5)
        for x in range(piece_grid.rows*piece_grid.cols):
            piece_grid.add_widget(Image(source='yellow.png'))

        button_symbols = ('Column 1', 'Column 2', 'Column 3', 'Column 4', 'Column 5', 'Column 6', 'Column 7')

        button_grid = GridLayout(cols=7, size_hint_y=.25)
        for symbol in button_symbols:
            button_grid.add_widget(Button(text=symbol))

        root_widget.add_widget(piece_grid)
        root_widget.add_widget(button_grid)

        return root_widget


if __name__ == '__main__':
    YourApp().run()