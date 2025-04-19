# -----------------------------------------------------------------------------------------------------------------------------------
# names: gary young, colin chu
# program name (official): calculatormodified.py
# program name (unofficial): connectfour, on the clients end
# purpose of the program: to play connect four with the server as a client, using a kivy GUI
# We pledge
# -----------------------------------------------------------------------------------------------------------------------------------

# install_twisted_rector must be called before importing the reactor
from __future__ import unicode_literals

from kivy.support import install_twisted_reactor

install_twisted_reactor()

# A Simple Client that send messages to the Echo Server
from twisted.internet import reactor, protocol

#import time
from kivy.app import App 
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.properties import NumericProperty #ObjectProperty, OptionProperty, StringProperty, BoundedNumericProperty, AliasProperty
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

# setup a gridlayout for the red and yellow pieces server/client put down, done in calculatormodified.kv
class PieceGridLayout(GridLayout):
    pass

# setup a gridlayout for the buttons client presses, done in calculatormodified.kv
class ButtonGridLayout(GridLayout):
    pass

# setup the column buttons to become disabled when set_disabled is called, add a certain colored piece to a column with add_color(), partially done in calculatormodified.kv
class ColumnButton(Button):
    # this sets the button to disabled when you set it to true, so you can't click on it anymore - or enables when you put False
    def set_disabled(self, value):
        return super().set_disabled(value)
    # this in general adds a piece to a column, and disables a button if necessary (particularly when a column is full or when waiting for the server to send back a move)
    # if you are a client calling this, all the buttons would be disabled temporarily until the server sends back their response
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

# setup a red piece to put on PieceGridLayout, done in calculator_modified.kv
class Red(Image):
    pass

# setup a yellow piece to put on PieceGridLayout, done in calculator_modified.kv
class Yellow(Image):
    pass

# setup a empty stack layout for the columns within PieceGridLayout, so that when images are added it stacks on top of eachother, done in calculator_modified.kv
class EmptyStackLayout(StackLayout):
    pass

# setup client twisted app to connect with the server (part 1 of 2), the essentials are taken from https://github.com/kivy/kivy/blob/master/examples/frameworks/twisted/echo_client_app.py
# also found on their official website, https://kivy.org/doc/stable/guide/other-frameworks.html
class EchoClient(protocol.Protocol):
    # when a connection is made successfully the running app will take that variable to send messages easier
    def connectionMade(self):
        self.factory.app.on_connection(self.transport)
    # when data is received the running app will process that message
    def dataReceived(self, data):
        response = self.factory.app.handle_message(data.decode('utf-8'))


# setup client twisted app to connect with the server (part 2 of 2), the essentials are taken from https://github.com/kivy/kivy/blob/master/examples/frameworks/twisted/echo_client_app.py
# also found on their official website, https://kivy.org/doc/stable/guide/other-frameworks.html
class EchoClientFactory(protocol.ClientFactory):
    protocol = EchoClient

    # this makes it easier and cleaner to access the running app instead of doing App.get_running_app() constantly
    def __init__(self, app):
        self.app = app

    # when you try to connect to server print started to connect
    def startedConnecting(self, connector):
        self.app.print_message('Started to connect.')

    # when connection is lost, either say you won/lost/tied earlier if that happened, or try to retry to connect to the server if that did not happen and tell client you lost connection and are retrying to connect
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

    # when the connection fails (typically when server isn't running), this will be called to try to reconnect to the server and print to client connect failed
    def clientConnectionFailed(self, connector, reason):
        self.app.print_message('Connection failed. Retrying...')
        self.app.connect_to_server()
 
# setup running app GUI, this is basically the main class for the app
class CalculatormodifiedApp(App):
    # initalize variables
    color = 'red'
    # variable for the connection properly assigned by the EchoClient class when a successful connection happens
    connection = None
    # variable to hold current label in the center, to display text to the client on results of the game or results about the connection
    label = None
    # variable for the connector to officially attempt a connection to a certain IP address and port or disconnect from it
    connector = None
    # variable for if a result has been found in the game
    global result_found
    result_found = False
    # variables for if a client or server won the game
    client_win = False
    server_win = False
    # count how many times a piece has been put in a certain column- where index 0 is the first column, index 1 is the second column, and so on
    counters = [0,0,0,0,0,0,0]
    # this holds the current result of the game
    global result
    result = ''
    # this holds the actual id the client has (when negotiating with the server unsuccessfully this is inaccurate, often temporarily)
    global id
    id = -1
    # this holds the boolean if a successful id has been found by negotiating w/ the server
    global id_found
    id_found = False
    # this is used to change opacity of the red/yellow pieces
    # kivy NumericProperty use: https://www.youtube.com/watch?v=OkW-1uzP5Og
    # see the video author is a official Kivy author: https://blog.kivy.org/author/alexander-taylor/
    opacity = NumericProperty(1)

    # https://kivy.org/doc/stable/api-kivy.uix.label.html
    # these get_x / get_y / show_mark methods basically add a green highlight around the text of the label

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

    #  this disables all of the buttons
    def disable_all_buttons(self):
        button_one.set_disabled(True)
        button_two.set_disabled(True)
        button_three.set_disabled(True)
        button_four.set_disabled(True)
        button_five.set_disabled(True)
        button_six.set_disabled(True)
        button_seven.set_disabled(True)

    # this cautiously reenables all of the buttons - if the counters array of a column is 6 or greater it would keep the button of that column disabled though
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

    # this increases the count of rows by 1 in a column given a column number
    def change_counters(self, index):
        self.counters[index-1] += 1

    # this is where the gui is setup and the connection to server is attempted
    def build(self):
        root = self.setup_gui()
        self.connect_to_server()
        return root
    
    # this is where the gui is setup, initally trying to connect to the server - though this is used more for the initial connecting / id negotiation phases (not the game itself)
    def setup_gui(self):
        root_widget = FloatLayout()
        self.label = Label(text='Connecting...\n')
        root_widget.add_widget(self.label)
        self.widget = root_widget
        return self.widget

    # this is where the client attempts to connect to the server
    def connect_to_server(self):
        self.connector = reactor.connectTCP('localhost', 8000, EchoClientFactory(self))

    # this is called when the EchoClient class successfully connected to the server, and tells client connected successfuly / negotiating id with server OR removes the label if negotiated already
    def on_connection(self, connection):
        self.connection = connection
        global id_found
        if id_found == False:
            self.print_message("Connected successfully! Negotiating id with server...")
            self.send_message_to_receive_id()
        else:
            self.widget.remove_widget(self.label)

    # this sets up the gui for the actual connect 4 game
    def setup_new_gui(self):
        # clear all widgets first in self.widget
        self.widget.clear_widgets()
        # consider this the root layout of the connect 4 game that would have all the layouts on top of it
        connect_four_box_layout = BoxLayout(orientation='vertical')
        # consider this the layout where pieces are shown
        piece_grid_layout = GridLayout(cols=7)
        # setup columns as EmptyStackLayouts and add them to piece_grid_layout
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
        # consider this the layout where buttons are shown
        button_layout = GridLayout(cols=7,size_hint_y=.25)
        # setup buttons as ColumnButtons with text respective to their columns, colored black for more readability
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
        # bind buttons to add colors to the columns within piece_grid_layout when the buttons are released
        button_one.bind(on_release=lambda instance: instance.add_color(column_one,1,True))
        button_two.bind(on_release=lambda instance: instance.add_color(column_two,2,True))
        button_three.bind(on_release=lambda instance: instance.add_color(column_three,3,True))
        button_four.bind(on_release=lambda instance: instance.add_color(column_four,4,True))
        button_five.bind(on_release=lambda instance: instance.add_color(column_five,5,True))
        button_six.bind(on_release=lambda instance: instance.add_color(column_six,6,True))
        button_seven.bind(on_release=lambda instance: instance.add_color(column_seven,7,True))
        # add the buttons to button_layout
        button_layout.add_widget(button_one)
        button_layout.add_widget(button_two)
        button_layout.add_widget(button_three)
        button_layout.add_widget(button_four)
        button_layout.add_widget(button_five)
        button_layout.add_widget(button_six)
        button_layout.add_widget(button_seven)
        # add piece_grid_layout and button_layout to the root layout of the connect 4 game
        connect_four_box_layout.add_widget(piece_grid_layout)
        connect_four_box_layout.add_widget(button_layout)
        # then add that as a widget to the classes widget (which should've been currently empty beforehand called at the beginning of this method)
        self.widget.add_widget(connect_four_box_layout)
        print('success?')

    # adds 1 to current id then tries to send it to the server
    def send_message_to_receive_id(self):
        global id
        id+=1
        msg = f"id|{id}"
        self.print_message("Sending id: " + str(id))
        if msg and self.connection:
            self.connection.write(msg.encode('utf-8'))

    # handles the message on server result if id was accepted or not - if so, set up new connect 4 GUI, else, call send_message_to_receive_id() again
    # also print to client the current result of the id acceptance and if trying new id / setting up new gui
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

    # send message to the server - this is a move that has a color, column, and id associated with it
    def send_message(self, color, column):
        global id
        msg = color + '|' + column + '|' + str(id) + '\n'
        print(msg)
        if msg and self.connection:
            print('reach')
            self.connection.write(msg.encode('utf-8'))

    # this sends disconnect message to the server, essentially to ask the server to remove the clients board object
    def send_disconnect_message(self):
        global id
        msg = f"rdc|{id}\n"
        if msg and self.connection:
            self.connection.write(msg.encode('utf-8'))

    # this adds to the label text a message
    def print_message(self, msg):
        self.label.text += "{}\n".format(msg)

    # this handles a message given by the server
    def handle_message(self, msg):
        print("MESSAGE '" + msg + "' RECEIVED")
        global result
        global result_found
        global id
        # TODO ask professor about this
        # if the first 3 chars indicate server is responding with an id message, have handle_message_for_receiving_id() handle it
        # note: for multi-connection for clients and the server to work, clients should ideally NEVER connect at the same exact time as then they would possibly both receive the same id
        # even in that case, this still satisfies the extra credit requirement anyway if that happens - just both clients would be playing the same board and >= 1 of the clients would have issues receiving the other clients data as the server is setup to also send results
        # i don't call the requirements specific enough for that scenario to be perfect
        if msg[0:3] == "id_":
            self.handle_message_for_receiving_id(msg)
            # return to exit this method
            return
        # if the first character is "t" with no move result after
        if msg[0:1] == "t" and msg.count('|') == 1:
            # and if the id matches what the client has
            if int(msg[2:]) == id:
                # change opacity of the pieces to 50%
                self.opacity = 0.5
                # change result to tie
                result = "tie"
                # say a result was found
                result_found = True
                # send dc msg to server
                self.send_disconnect_message()
                # actually disconnect
                self.connector.disconnect()
                # disable all buttons
                self.disable_all_buttons()
                # return the result
                print(result)
                return result
            # if id does not match, just return to exit this method
            else:
                return
        # if the first character is "w" with no move result after
        if msg[0:1] == "w" and msg.count('|') == 1:
            # and if the id matches what the client has
            if int(msg[2:]) == id:
                # change opacity of the pieces to 50%
                self.opacity = 0.5
                # change result to win
                result = "win"
                # set result_found and client_win to true
                result_found = True
                self.client_win = True
                # send dc msg to server
                self.send_disconnect_message()
                # actually disconnect
                self.connector.disconnect()
                # disable all buttons
                self.disable_all_buttons()
                # return the result
                print(result)
                return result
            # if id does not match, just return to exit this method
            else:
                return
        # if the first character is "l" with no move result after
        if msg[0:1] == "l" and msg.count('|') == 1:
            # and if the id matches what the client has
            if int(msg[2:]) == id:
                # change opacity of the pieces to 50%
                self.opacity = 0.5
                # change result to lose
                result = "lose"
                # set result_found and server_win to true
                result_found = True
                self.server_win = True
                # send dc msg to server
                self.send_disconnect_message()
                # actually disconnect
                self.connector.disconnect()
                # disable all buttons
                self.disable_all_buttons()
                # return the result
                print(result)
                return result
            # if id does not match, just return to exit this method
            else:
                return
        # set colToChange to a certain part of the message given
        self.colToChange = int(msg[6:7])
        # match the column to add a piece to a column, calling a buttons add_color method
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
        # if first part of message, there is a move, and the last part of the message matches this clients id,
        if msg[0:1] == "t" and int(msg[8:]) == id:
            # change opacity of the pieces to 50%
            self.opacity = 0.5
            # change result to tie
            result = "tie"
            # change result found to true
            result_found = True
            # send dc msg to server
            self.send_disconnect_message()
            # actually disconnect
            self.connector.disconnect()
            # disable all buttons
            self.disable_all_buttons()
            # return the result
            print(result)
            return result
        if msg[0:1] == "w" and int(msg[8:]) == id:
            # change opacity of the pieces to 50%
            self.opacity = 0.5
            # change result to win
            result = "win"
            # change result found to true
            result_found = True
            # change client win to true
            self.client_win = True
            # send dc msg to server
            self.send_disconnect_message()
            # actually disconnect
            self.connector.disconnect()
            # disable all buttons
            self.disable_all_buttons()
            # return the result
            print(result)
            return result
        if msg[0:1] == "l" and int(msg[8:]) == id:
            # change opacity of the pieces to 50%
            self.opacity = 0.5
            # change result to lose
            result = "lose"
            # change result found to true
            result_found = True
            # change server win to true
            self.server_win = True
            # send dc msg to server
            self.send_disconnect_message()
            # actually disconnect
            self.connector.disconnect()
            # disable all buttons
            self.disable_all_buttons()
            # return the result
            print(result)
            return result
        # return result if all the if's with returns were skipped
        print(result)
        return result

# run the app
if __name__=='__main__':
    CalculatormodifiedApp().run()