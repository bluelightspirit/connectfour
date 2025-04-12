from kivy.app import App 
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, OptionProperty, StringProperty
from kivy.uix.label import Label

class PieceGridLayout(GridLayout):
    pass

class ButtonGridLayout(GridLayout):
    pass

class ConnectFourBoxLayout(BoxLayout):
    pass

class Red(Image):
    pass

class Yellow(Image):
    pass

class EmptyStackLayout(StackLayout):
    def add_color(self, color):
        if color == 'red':
            self.add_widget(Red())
        elif color == 'yellow':
            self.add_widget(Yellow())
    pass
 
class CalculatormodifiedApp(App):
    color = 'red' # color switcher option is too complex to make, also not even in extra credit list anyway
    def build(self):
        return ConnectFourBoxLayout()
 
if __name__=='__main__':
    CalculatormodifiedApp().run()