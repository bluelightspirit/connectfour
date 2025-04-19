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
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

opacity = NumericProperty(1)

class PieceGridLayout(GridLayout):
    pass

class ButtonGridLayout(GridLayout):
    pass

class ColumnButton(Button):
    def set_disabled(self, value):
        return super().set_disabled(value)
    def add_color(self, column, columnNumber, sending):
        global result_found
        main = App.get_running_app()
        color = ''
        if sending == True:
            main.disable_all_buttons()
            color = main.color
        else:
            if main.color == 'yellow':
                color = 'red'
            else:
                color = 'yellow'
        print('col number changing: ' + str(columnNumber))
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
            main.send_message('dis',str(columnNumber))
            self.set_disabled(True)
        if sending == False and result_found == False:
            print('reenabling')
            main.reenable_all_buttons()
    pass

class Red(Image):
    def on_opacity(*args):
        Image.color = [1,1,1,App.opacity]
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
        global result_found
        if result_found == False:
            #self.app.widget.clear_widgets()
            self.app.label = Label(text='[ref=myref]Lost connection. \nRetrying to connect...\n[/ref]',markup=True)
            Clock.schedule_once(lambda dt: self.app.show_marks(self.app.label), 0.1)
            self.app.widget.add_widget(self.app.label)
            self.app.connect_to_server()
        else:
            result_text = ""
            if self.app.client_win == True:
                result_text = "You won earlier though.\n"
            elif self.app.server_win == True:
                result_text = "You lost earlier.\n"
            else:
                result_text = "You tied earlier.\n"
            self.app.label = Label(text='[ref=myref]Disconnected. \nYou\'re stuck here.\n' + result_text + '[/ref]',markup=True)
            Clock.schedule_once(lambda dt: self.app.show_marks(self.app.label), 0.5)
            self.app.widget.add_widget(self.app.label)

    def clientConnectionFailed(self, connector, reason):
        self.app.print_message('Connection failed. Retrying...')
        self.app.connect_to_server()
 
class CalculatormodifiedApp(App):
    color = 'red' # color switcher option is too complex to make, also not even in extra credit list anyway
    connection = None
    label = None
    textbox = None
    connector = None
    global result_found
    result_found = False
    client_win = False
    server_win = False
    counters = [0,0,0,0,0,0,0]
    global result
    result = ''
    global id
    id = -1
    global id_found
    id_found = False
    opacity = NumericProperty(1)

    # https://kivy.org/doc/stable/api-kivy.uix.label.html

    @staticmethod
    def get_x(label, ref_x):
        """ Return the x value of the ref/anchor relative to the canvas """
        return label.center_x - label.texture_size[0] * 0.5 + ref_x

    @staticmethod
    def get_y(label, ref_y):
        """ Return the y value of the ref/anchor relative to the canvas """
        # Note the inversion of direction, as y values start at the top of
        # the texture and increase downwards
        return label.center_y + label.texture_size[1] * 0.5 - ref_y
    
    def show_marks(self, label):

        # Indicate the position of the anchors with a red top marker
        for name, anc in label.anchors.items():
            with label.canvas:
                Color(1, 0, 0)
                Rectangle(pos=(self.get_x(label, anc[0]),
                                self.get_y(label, anc[1])),
                            size=(3, 3))

        # Draw a green surround around the refs. Note the sizes y inversion
        for name, boxes in label.refs.items():
            for box in boxes:
                with label.canvas:
                    Color(0, 1, 0, 0.25)
                    Rectangle(pos=(self.get_x(label, box[0]),
                                    self.get_y(label, box[1])),
                                size=(box[2] - box[0],
                                    box[1] - box[3]))

    def disable_all_buttons(self):
        button_one.set_disabled(True)
        button_two.set_disabled(True)
        button_three.set_disabled(True)
        button_four.set_disabled(True)
        button_five.set_disabled(True)
        button_six.set_disabled(True)
        button_seven.set_disabled(True)

    def reenable_all_buttons(self):
        if self.counters[0] < 6:
            button_one.set_disabled(False)
        if self.counters[1] < 6:
            button_two.set_disabled(False)
        if self.counters[2] < 6:
            button_three.set_disabled(False)
        if self.counters[3] < 6:
            button_four.set_disabled(False)
        if self.counters[4] < 6:
            button_five.set_disabled(False)
        if self.counters[5] < 6:
            button_six.set_disabled(False)
        if self.counters[6] < 6:
            button_seven.set_disabled(False)

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
        self.connector = reactor.connectTCP('localhost', 8000, EchoClientFactory(self))

    def on_connection(self, connection):
        self.connection = connection
        global id_found
        if id_found == False:
            self.print_message("Connected successfully! Negotiating id with server...")
            self.send_message_to_receive_id()
        else:
            self.widget.remove_widget(self.label)

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
        print('success?')

    def send_message_to_receive_id(self):
        global id
        id+=1
        msg = f"id|{id}"
        self.print_message("Sending id: " + str(id))
        if msg and self.connection:
            self.connection.write(msg.encode('utf-8'))
            self.textbox.text = ""

    def handle_message_for_receiving_id(self, msg):
        global id
        global id_found
        print(msg)
        if msg[3:6] == "val":
            self.print_message("Our id was accepted! Setting up new GUI...")
            print("successs.............?")
            id_found = True
            self.setup_new_gui()
        else:
            self.print_message("Our id was denied... Trying new id...")
            self.send_message_to_receive_id()

    def send_message(self, color, column):
        global id
        msg = color + '|' + column + '|' + str(id) + '\n'
        print(msg)
        if msg and self.connection:
            print('reach')
            self.connection.write(msg.encode('utf-8'))
            self.textbox.text = ""

    def send_disconnect_message(self):
        global id
        msg = f"rdc|{id}\n"
        if msg and self.connection:
            self.connection.write(msg.encode('utf-8'))
            self.textbox.text = ""

    def print_message(self, msg):
        self.label.text += "{}\n".format(msg)

    def handle_message(self, msg):
        print("MESSAGE '" + msg + "' RECEIVED")
        global result
        global result_found
        global id
        if msg[0:3] == "id_":
            self.handle_message_for_receiving_id(msg)
            return
        if msg[0:1] == "t" and msg.count('|') == 1:
            if int(msg[2:]) == id:
                self.opacity = 0.5
                result = "tie"
                result_found = True
                self.send_disconnect_message()
                self.connector.disconnect()
                self.disable_all_buttons()
                print(result)
                return result
            else:
                return
        if msg[0:1] == "w" and msg.count('|') == 1:
            if int(msg[2:]) == id:
                self.opacity = 0.5
                result = "win"
                result_found = True
                self.client_win = True
                self.send_disconnect_message()
                self.connector.disconnect()
                self.disable_all_buttons()
                print(result)
                return result
            else:
                return
        if msg[0:1] == "l" and msg.count('|') == 1:
            if int(msg[2:]) == id:
                self.opacity = 0.5
                result = "lose"
                result_found = True
                self.server_win = True
                self.send_disconnect_message()
                self.connector.disconnect()
                self.disable_all_buttons()
                print(result)
                return result
            else:
                return
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
        if msg[0:1] == "t" and int(msg[8:]) == id:
            self.opacity = 0.5
            result = "tie"
            result_found = True
            self.send_disconnect_message()
            self.connector.disconnect()
            self.disable_all_buttons()
            print(result)
            return result
        if msg[0:1] == "w" and int(msg[8:]) == id:
            self.opacity = 0.5
            result = "win"
            result_found = True
            self.client_win = True
            self.send_disconnect_message()
            self.connector.disconnect()
            self.disable_all_buttons()
            print(result)
            return result
        if msg[0:1] == "l" and int(msg[8:]) == id:
            self.opacity = 0.5
            result = "lose"
            result_found = True
            self.server_win = True
            self.send_disconnect_message()
            self.connector.disconnect()
            self.disable_all_buttons()
            print(result)
            return result
        print(result)
        return result

 
if __name__=='__main__':
    CalculatormodifiedApp().run()