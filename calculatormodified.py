# install_twisted_rector must be called before importing the reactor
from __future__ import unicode_literals

from kivy.support import install_twisted_reactor

install_twisted_reactor()

# A Simple Client that send messages to the Echo Server
from twisted.internet import reactor, protocol

import time
from kivy.app import App 
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, OptionProperty, StringProperty, NumericProperty, BoundedNumericProperty, AliasProperty
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


class PieceGridLayout(GridLayout):
    pass

class ButtonGridLayout(GridLayout):
    pass

class ColumnButton(Button):
    def set_disabled(self, value):
        return super().set_disabled(value)
    def add_color(self, column, columnNumber, sending):
        main = App.get_running_app()
        color = ''
        if sending == True:
            color = main.color
        else:
            if main.color == 'yellow':
                color = 'red'
            else:
                color = 'yellow'
        main.change_counters(columnNumber)
        prepareToDisable = False
        if main.counters[columnNumber-1] == 6:
            prepareToDisable = True
        if color == 'red':
            column.add_widget(Red())
            if sending == True:
                main.send_message('red',str(columnNumber))
        elif color == 'yellow':
            column.add_widget(Yellow())
            if sending == True:
                main.send_message('yel',str(columnNumber))

        if prepareToDisable == True:
            self.set_disabled(True)
    pass

class Red(Image):
    pass

class Yellow(Image):
    pass

class EmptyStackLayout(StackLayout):
    #column = 1
    #def get_column(self):
    #    return 
    #colToChange = AliasProperty()
    #def on_value_change(self, localColToChange):
    #    print("GOT HERE!!!")
    # def add_color(self, button, columnNumber):
    #     main = App.get_running_app()
    #     color = main.color
    #     main.change_counters(columnNumber)
    #     prepareToDisable = False
    #     if main.counters[columnNumber-1] == 6:
    #         prepareToDisable = True
    #     if color == 'red':
    #         self.add_widget(Red())
    #     elif color == 'yellow':
    #         self.add_widget(Yellow())

    #     if prepareToDisable == True:
    #         button.set_disabled(True)
    pass

class EchoClient(protocol.Protocol):
    def connectionMade(self):
        self.factory.app.on_connection(self.transport)

    def dataReceived(self, data):
        response = self.factory.app.handle_message(data.decode('utf-8'))


class EchoClientFactory(protocol.ClientFactory):
    protocol = EchoClient

    def __init__(self, app):
        self.app = app

    def startedConnecting(self, connector):
        self.app.print_message('Started to connect.')

    def clientConnectionLost(self, connector, reason):
        self.app.widget.clear_widgets()

        self.app.label = Label(text='Lost connection. \nRetrying to connect...\n')
        self.app.widget.add_widget(self.app.label)
        self.app.connect_to_server()

    def clientConnectionFailed(self, connector, reason):
        self.app.print_message('Connection failed. Retrying...')
        self.app.connect_to_server()
 
class CalculatormodifiedApp(App):
    color = 'red' # color switcher option is too complex to make, also not even in extra credit list anyway
    connection = None
    label = None
    textbox = None
    client_win = False
    server_win = False
    counters = [0,0,0,0,0,0,0]
    global result
    result = ''
    handle_message_called = False
    handle_message_text = ''

    def change_counters(self, index):
        self.counters[index-1] += 1

    def build(self):
        # root_widget = FloatLayout()
        # connectfour_widget = BoxLayout(orientation = 'vertical')
        # board_widget = GridLayout(cols=7)
        # for x in range(7):
        #     board_widget.add_widget(EmptyStackLayout)
        # button_widget = GridLayout(cols=7,size_hint_y=.25)
        # button_widget.add_widget(ColumnButton)
        # connectfour_widget.add_widget()
        # root_widget.add_widget(connectfour_widget)
        # return ConnectFourBoxLayout()
        root = self.setup_gui()
        self.connect_to_server()
        return root
    
    def setup_gui(self):
        self.textbox = TextInput(size_hint_y=.1, multiline=False)
        self.textbox.bind(on_text_validate=self.send_message)
        root_widget = FloatLayout()
        self.label = Label(text='Connecting...\n')
        root_widget.add_widget(self.label)
        self.widget = root_widget
        return self.widget

    #@classmethod
    def connect_to_server(self):
        reactor.connectTCP('localhost', 8000, EchoClientFactory(self))

    def on_connection(self, connection):
        self.print_message("Connected successfully!")
        self.connection = connection
        self.setup_new_gui()

    def setup_new_gui(self):
        self.widget.clear_widgets()
        connect_four_box_layout = BoxLayout(orientation='vertical')
        piece_grid_layout = GridLayout(cols=7)
        global column_one
        global column_two
        global column_three
        global column_four
        global column_five
        global column_six
        global column_seven
        column_one = EmptyStackLayout()
        column_two = EmptyStackLayout()
        column_three = EmptyStackLayout()
        column_four = EmptyStackLayout()
        column_five = EmptyStackLayout()
        column_six = EmptyStackLayout()
        column_seven = EmptyStackLayout()
        piece_grid_layout.add_widget(column_one)
        piece_grid_layout.add_widget(column_two)
        piece_grid_layout.add_widget(column_three)
        piece_grid_layout.add_widget(column_four)
        piece_grid_layout.add_widget(column_five)
        piece_grid_layout.add_widget(column_six)
        piece_grid_layout.add_widget(column_seven)
        button_layout = GridLayout(cols=7,size_hint_y=.25)
        global button_one
        global button_two
        global button_three
        global button_four
        global button_five
        global button_six
        global button_seven
        button_one = ColumnButton(text='[color=000000]Column 1[/color]')
        button_two = ColumnButton(text='[color=000000]Column 2[/color]')
        button_three = ColumnButton(text='[color=000000]Column 3[/color]')
        button_four = ColumnButton(text='[color=000000]Column 4[/color]')
        button_five = ColumnButton(text='[color=000000]Column 5[/color]')
        button_six = ColumnButton(text='[color=000000]Column 6[/color]')
        button_seven = ColumnButton(text='[color=000000]Column 7[/color]')
        button_one.bind(on_release=lambda instance: instance.add_color(column_one,1,True))
        button_two.bind(on_release=lambda instance: instance.add_color(column_two,2,True))
        button_three.bind(on_release=lambda instance: instance.add_color(column_three,3,True))
        button_four.bind(on_release=lambda instance: instance.add_color(column_four,4,True))
        button_five.bind(on_release=lambda instance: instance.add_color(column_five,5,True))
        button_six.bind(on_release=lambda instance: instance.add_color(column_six,6,True))
        button_seven.bind(on_release=lambda instance: instance.add_color(column_seven,7,True))
        button_layout.add_widget(button_one)
        button_layout.add_widget(button_two)
        button_layout.add_widget(button_three)
        button_layout.add_widget(button_four)
        button_layout.add_widget(button_five)
        button_layout.add_widget(button_six)
        button_layout.add_widget(button_seven)
        connect_four_box_layout.add_widget(piece_grid_layout)
        connect_four_box_layout.add_widget(button_layout)
        self.widget.add_widget(connect_four_box_layout)

    def send_message(self, color, column):
        msg = color + '|' + column
        print(msg)
        if msg and self.connection:
            print('reach')
            self.connection.write(msg.encode('utf-8'))
            self.textbox.text = ""

    def print_message(self, msg):
        self.label.text += "{}\n".format(msg)

    def handle_message(self, msg):
        print("MESSAGE '" + msg + "' RECEIVED")
        global result
        self.colToChange = int(msg[6:7])
        match self.colToChange:
            case 1:
                button_one.add_color(column_one,1,False)
            case 2:
                button_two.add_color(column_two,2,False)
            case 3:
                button_three.add_color(column_three,3,False)
            case 4:
                button_four.add_color(column_four,4,False)
            case 5:
                button_five.add_color(column_five,5,False)
            case 6:
                button_six.add_color(column_six,6,False)
            case 7:
                button_seven.add_color(column_seven,7,False)
        if msg[0:1] == "w":
            self.label = Label(text='You won!\n')
            self.widget.add_widget(self.label)
            result = "win"
        elif msg[0:1] == "l":
            self.label = Label(text='You lost!\n')
            self.widget.add_widget(self.label)
            result = "lose"
        print(result)
        return result

 
if __name__=='__main__':
    CalculatormodifiedApp().run()