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
from kivy.properties import ObjectProperty, OptionProperty, StringProperty
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

class PieceGridLayout(GridLayout):
    pass

class ButtonGridLayout(GridLayout):
    pass

class ColumnButton(Button):
    def set_disabled(self, value):
        return super().set_disabled(value)
    pass

class ConnectFourBoxLayout(BoxLayout):
    pass

class Red(Image):
    pass

class Yellow(Image):
    pass

class EmptyStackLayout(StackLayout):
    def add_color(self, column):
        main = App.get_running_app()
        color = main.color
        main.change_counters(column-1)
        prepareToDisable = False
        if main.counters[column-1] == 6:
            prepareToDisable = True
        if color == 'red':
            self.add_widget(Red())
        elif color == 'yellow':
            self.add_widget(Yellow())

        return prepareToDisable
    pass

class EchoClient(protocol.Protocol):
    def connectionMade(self):
        self.factory.app.on_connection(self.transport)

    def dataReceived(self, data):
        response = self.factory.app.handle_message(data.decode('utf-8'))
        if response:
            self.transport.write(response)
            print(response)


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
        self.counters[index] += 1

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
        self.widget.clear_widgets()
        self.widget.add_widget(ConnectFourBoxLayout())
        self.connection = connection

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
        global result
        handle_message_called = True
        handle_message_text = msg
        if msg[0:1] == "w":
            client_win = True
            self.widget.clear_widgets()
            self.label = Label(text='You won!\n')
            self.widget.add_widget(self.label)
            result = "win"
        elif msg[0:1] == "l":
            server_win = True
            self.widget.clear_widgets()
            self.label = Label(text='You lost!\n')
            self.widget.add_widget(self.label)
            result = "lose"
        return result

 
if __name__=='__main__':
    CalculatormodifiedApp().run()