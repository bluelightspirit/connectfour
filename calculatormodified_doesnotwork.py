from kivy.app import App 
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, OptionProperty, StringProperty
from kivy.uix.label import Label

global color
color = ''

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
    def build(self):
        global color
        root_widget = FloatLayout()
        if color == '':
            print('reached')
            color_box_layout = BoxLayout(orientation = 'vertical')
            color_box_layout.add_widget(Label(text = 'What color do you want?', size_hint_y = .25))
            global color_option_layout
            color_option_layout = GridLayout(rows = 2)

    # ColorChooserButton:
    #   background_color: (255/88, 200/88, 0/88, 1)
    #   text: '[color=FFFFE0]Yellow[/color]'
    #   on_release:
    #     app.color = 'yellow'
    #     print(app.color)
    # ColorChooserButton:
    #   background_color: (144/98, 93/98, 93/98, 1)
    #   text: '[color=F4C2C2]Red[/color]'
    #   on_release:
    #     app.color = 'red'
    #     print(app.color)


            yellow_button = Button(markup = True, background_color = (255/88,200/88,0/88,1), text = '[color=FFFFE0]Yellow[/color]')
            yellow_button.bind(on_release = self.change_color)
            color_option_layout.add_widget(yellow_button)
            print('new color: ' + color)
            color_box_layout.add_widget(color_option_layout)
            root_widget.add_widget(color_box_layout)
        else:
            print('test2')
            # root_widget.remove_widget(color_box_layout)
            root_widget.add_widget(ConnectFourBoxLayout)
        return root_widget
    
    def change_color(self, event):
        global color
        color = 'red'
        print(color)
        self.build
 
if __name__=='__main__':
    CalculatormodifiedApp().run()