# install_twisted_rector must be called before importing and using the reactor
from kivy.support import install_twisted_reactor

install_twisted_reactor()

from twisted.internet import reactor
from twisted.internet import protocol
import random


class EchoServer(protocol.Protocol):
    def dataReceived(self, data):
        response = self.factory.app.handle_message(data)
        if response:
            self.transport.write(response)


class EchoServerFactory(protocol.Factory):
    protocol = EchoServer

    def __init__(self, app):
        self.app = app


from kivy.app import App
from kivy.uix.label import Label


class TwistedServerApp(App):
    label = None
    cols_enabled= [1,2,3,4,5,6,7]
    # 2d by columns
    connect_four_board= [
        ['','','','','',''], #col1
        ['','','','','',''], #col2
        ['','','','','',''], #col3
        ['','','','','',''], #col4
        ['','','','','',''], #col5
        ['','','','','',''], #col6
        ['','','','','','']  #col7
        ]
    
    def insert_to_board(self, columnNumber, color):
        for x in range(len(self.connect_four_board[columnNumber-1])):
            if self.connect_four_board[columnNumber-1][x] == '':
                self.connect_four_board[columnNumber-1][x] = color
                # print('-----')
                # print('col # ' + str(columnNumber))
                # print('color ' + color)
                # print('-----')
                break

    def build(self):
        self.label = Label(text="server started\n")
        reactor.listenTCP(8000, EchoServerFactory(self))
        return self.label
    
    def choose_column(self):
        if len(self.cols_enabled) == 0:
            return 0
        return random.choice(self.cols_enabled) 
    
    def determine_tie(self):
        print(len(self.cols_enabled))
        if len(self.cols_enabled) == 0:
            return True
        else:
            return False
        
    # check cols starts at col 1 row 1, then searches col 2 row 1, col 3 row 1, and col 4 row 1
    # have col be limited by 6-3 because beyond col 7 does not exist, and you add up to 3 for col
    def check_matching_columns(self):
        board = self.connect_four_board
        for col in range(4):
            for row in range(6):
                if board[col][row] != '' and board[col+1][row] == board[col][row] and board[col+2][row] == board[col][row] and board[col+3][row] == board[col][row]:
                    return board[col][row]
        return ''
    
    # check rows starts at col 1 row 1, then searches col 1 row 2, col 1 row 3, and col 1 row 4
    # have row be limited by 6-3 because beyond row 6 does not exist, and you add up to 3 for row
    def check_matching_rows(self):
        board = self.connect_four_board
        for col in range(7):
            for row in range(3):
                if board[col][row] != '' and board[col][row+1] == board[col][row] and board[col][row+2] == board[col][row] and board[col][row+3] == board[col][row]:
                    return board[col][row]
        return ''
    
    # positive slope diagonal starts at col 1, row 1, then searches col 2, row 2, col 3 row 3, and col 4 row 4
    # have row be limited by 6-3 because beyond row 6 does not exist, and you add up to 3 for row
    def check_matching_positive_diagonal(self):
        board = self.connect_four_board
        for col in range(4):
            for row in range(3):
                if board[col][row] != '' and board[col+1][row+1] == board[col][row] and board[col+2][row+2] == board[col][row] and board[col+3][row+3] == board[col][row]:
                    return board[col][row]
        return ''
    
    # negative slope diagonal starts at col 1, row 4 then searches col 2, row 3 and col 3, row 2 and col 4, row 1
    # no point of searching col 1 row 3 or less row, as you subtract up to 3 for row
    # no point of searching for col 5+, as you add up to 3 for col
    def check_matching_negative_diagonal(self):
        board = self.connect_four_board
        for col in range(4):
            for row in range(3, 6):
                if board[col][row] != '' and board[col+1][row-1] == board[col][row] and board[col+2][row-2] == board[col][row] and board[col+3][row-3] == board[col][row]:
                    return board[col][row]
        return ''

    def determine_winner(self):
        winner_array = [self.check_matching_columns(), self.check_matching_rows(), self.check_matching_positive_diagonal(), self.check_matching_negative_diagonal()]
        for winner_result in winner_array:
            if winner_result != '':
                return winner_result
        return ''
    
    def construct_message(self, msg, color):
        col = self.choose_column()
        self.insert_to_board(col, color)
        #print('tie result: ' + str(tie))
        res = 'n'
        if msg == 'l':
            res = 'l'
        elif msg == 'w':
            res = 'w'
        elif self.determine_winner() != color and self.determine_winner() != '':
            print('winner: ' + self.determine_winner())
            res = 'w'
        elif self.determine_winner() == color:
            print('winner: ' + self.determine_winner())
            res= 'l'
        return f"{res}|yel|{col}"
    

    def handle_message(self, msg):
        color = ''
        msg = msg.decode('utf-8')
        self.label.text = "received:  {}\n".format(msg)
        msg_array = msg.split("\n")
        msg = ''
        for x in msg_array:
            # case of receiving dis (handle this before trying to add colors for less problems)
            if x == '':
                pass
            elif x[0:3] == 'dis':
                self.cols_enabled.remove(int(x[4:5]))
                print('cols enabled: ' + str(self.cols_enabled))
                #print("receive dis successful")
        for x in msg_array:
            # case of receiving a color
            if x == '':
                pass
            elif x[0:3] != 'dis':
                # get color and insert to board
                color = x[0:3]
                colToInsertStr = x[4:5]
                colToInsert = int(colToInsertStr)
                self.insert_to_board(colToInsert,color)
                if self.determine_winner() == color:
                    print('winner: ' + self.determine_winner())
                    msg = 'w'
                    break
                elif self.determine_winner() != color and self.determine_winner() != '':
                    print('winner: ' + self.determine_winner())
                    msg = 'l'
                    break

                #print("receive color succsesful")
                # switch colors to send
                if x[0:3] == "yel":
                    color = 'red'
                else:
                    color = 'yel'
                msg = self.construct_message(msg, color)
                print('connect 4 board: ' + str(self.connect_four_board))
                self.label.text += "responded: {}\n".format(msg)
                return msg.encode('utf-8')
        # msg options to send back
        # msg = "w|non|0"
        # msg = "l|non|0"
        # msg = "w|yel|1"
        # msg = "l|yel|1"
        # msg = "n|yel|1"
        
        # case of sole disable, just send empty string over
        # except if there is a tie
        if self.determine_tie() == True:
            msg = 't'
        return msg.encode('utf-8')


if __name__ == '__main__':
    TwistedServerApp().run()
