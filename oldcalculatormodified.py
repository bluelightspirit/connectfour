from kivy.app import App 
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, OptionProperty
from kivy.uix.label import Label

class PieceGridLayout(GridLayout):
    pass

class ButtonGridLayout(GridLayout):
    pass

class Red(Image):
    pass

class Button(Button):
    def add_red(self):
        self.parent.ids.one.add_widget(Red())
 
class OldcalculatormodifiedApp(App):
    def build(self):
        root_widget = BoxLayout(orientation='vertical')
        root_widget.add_widget(PieceGridLayout())
        root_widget.add_widget(ButtonGridLayout())
        return root_widget
 
if __name__=='__main__':
    OldcalculatormodifiedApp().run()