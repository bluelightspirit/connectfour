# install_twisted_rector must be called before importing and using the reactor
from kivy.support import install_twisted_reactor

install_twisted_reactor()

from twisted.internet import reactor
from twisted.internet import protocol
import random


# setup server to listen for data in a port (part 1 of 2), the essentials are taken from https://github.com/kivy/kivy/blob/master/examples/frameworks/twisted/echo_server_app.py
# also found on their official website, https://kivy.org/doc/stable/guide/other-frameworks.html
class EchoServer(protocol.Protocol):
    def dataReceived(self, data):
        response = self.factory.app.handle_message(data)
        if response:
            self.transport.write(response)


# setup server to listen for data in a port (part 2 of 2), the essentials are taken from https://github.com/kivy/kivy/blob/master/examples/frameworks/twisted/echo_server_app.py
# also found on their official website, https://kivy.org/doc/stable/guide/other-frameworks.html
class EchoServerFactory(protocol.Factory):
    protocol = EchoServer

    def __init__(self, app):
        self.app = app


from kivy.app import App
from kivy.uix.label import Label

# setup a class to represent board objects attributed to id's of clients, so multiple clients can play different connect 4 games
class BoardToClient:
    # initialize with an emtpy connect four board, all 7 cols enabled, and an empty good columns array
    def __init__(self, id=-1):
        self.id = id
        # 2d by columns
        self.connect_four_board= [
        ['','','','','',''], #col1
        ['','','','','',''], #col2
        ['','','','','',''], #col3
        ['','','','','',''], #col4
        ['','','','','',''], #col5
        ['','','','','',''], #col6
        ['','','','','','']  #col7
        ]
        self.cols_enabled= [1,2,3,4,5,6,7]
        self.good_columns= []
    # method to show id
    def show_id(self):
        print(self.id)
    # method to insert a piece to a board at a certain column, at a spot on top of a piece in which that spot is empty
    def insert_to_board(self, columnNumber, color):
        for x in range(len(self.connect_four_board[columnNumber-1])):
            if self.connect_four_board[columnNumber-1][x] == '':
                self.connect_four_board[columnNumber-1][x] = color
                # print('-----')
                # print('col # ' + str(columnNumber))
                # print('color ' + color)
                # print('-----')
                break
    # method to choose a random column
    def choose_column(self):
        if len(self.cols_enabled) == 0:
            return 0
        print('current cols enabled: ' + str(self.cols_enabled))
        return random.choice(self.cols_enabled) 
    # method to determine a tie
    def determine_tie(self):
        print(len(self.cols_enabled))
        if len(self.cols_enabled) == 0:
            return True
        else:
            return False
        
    # ai check for almost matching rows (3 in a row)
    def ai_check_almost_matching_rows(self):
        board = self.connect_four_board
        # store good columns to choose from. keep duplicates as increasing odds of choosing a column in the end is intended
        goodColumns = self.good_columns
        for col in range(5):
            for row in range(6):
                # this can be aggressive or defensive since it's seraching for non-empty string.
                if board[col][row] != '' and board[col+1][row] == board[col][row] and board[col+2][row] == board[col][row]:
                    # check for empty good spots in columns
                    # check for empty column left
                    if col-1 >= 0:
                        if board[col-1][row] == '':
                            # special checking if there's a piece under the good spot to place
                            if row-1 >= 0:
                                if board[col-1][row-1] != '':        
                                    goodColumns.append(col-1)
                            # if row-1 is negative then the column spot in question is at the bottom and it's available
                            else:
                                goodColumns.append(col-1)
                    # check for empty column right
                    if col+3 <=6 and board[col+3][row] == '':
                        # special checking if there's a piece under the good spot to place
                            if row-1 >= 0:
                                if board[col+3][row-1] != '':        
                                    goodColumns.append(col+3)
                            # if row-1 is negative then the column spot in question is at the bottom and it's available
                            else:
                                goodColumns.append(col+3)
        # always return goodColumns array and set good_columns back to goodColumns
        self.good_columns = goodColumns
        return goodColumns
    
    # ai check for almost matching columns (3 in a column)
    # this will always be fine it seems
    def ai_check_almost_matching_columns(self):
        board = self.connect_four_board
        # store good columns to choose from. keep duplicates as increasing odds of choosing a column in the end is intended
        goodColumns = self.good_columns
        for col in range(7):
            for row in range(3):
                # this can be aggressive or defensive since it's searching for non-empty string
                if board[col][row] != '' and board[col][row+1] == board[col][row] and board[col][row+2] == board[col][row]:
                    # check for empty spot in column
                    if board[col][row+3] == '':
                        goodColumns.append(col)
        # always return goodColumns array and set good_columns back to goodColumns
        self.good_columns = goodColumns
        return goodColumns
    
    # these matching diagonal AI's may be off for the negative checks, but seems good to me at a glance
    #TODO check again

    # ai check for almost matching positive diagonal (3 in a positive diagonal)
    def ai_check_almost_matching_positive_diagonal(self):
        board = self.connect_four_board
        # store good columns to choose from. keep duplicates as increasing odds of choosing a column in the end is intended
        goodColumns = self.good_columns
        for col in range(5):
            for row in range(4):
                if board[col][row] != '' and board[col+1][row+1] == board[col][row] and board[col+2][row+2] == board[col][row]:
                    # check for empty column up and right
                    if col+3 <= 6 and row+3 <= 5 and board[col+3][row+3] == '':
                        # special checking if there's a piece under the good spot to place
                            if row+2 <= 5:
                                if board[col+3][row+2] != '':        
                                    goodColumns.append(col+3)
                            # if row-1 is negative then the column spot in question is at the bottom and it's available
                            else:
                                goodColumns.append(col+3)
                    # check for empty column down and left, both col and row there must exist
                    if col-1 >= 0 and row-1 >= 0:
                        if board[col-1][row-1] == '':
                            if row-2 >= 0:
                                if board[col-1][row-2] != '':        
                                    goodColumns.append(col-1)
                            # if row-2 is negative then the column spot in question is at the bottom and it's available
                            else:
                                goodColumns.append(col-1)
        # always return goodColumns array and set good_columns back to goodColumns
        self.good_columns = goodColumns
        return goodColumns
    
    # ai check for almost matching negative diagonal (3 in a negative diagonal)
    def ai_check_almost_matching_negative_diagonal(self):
        board = self.connect_four_board
        # store good columns to choose from. keep duplicates as increasing odds of choosing a column in the end is intended
        goodColumns = self.good_columns
        for col in range(5):
            for row in range(2, 6):
                if board[col][row] != '' and board[col+1][row-1] == board[col][row] and board[col+2][row-2] == board[col][row]:
                    # check for empty column right and down
                    if col+3 <= 6 and row-3 >= 0 and board[col+3][row-3] == '':
                        # special checking if there's a piece under the good spot to place
                            if row-4 >= 0:
                                if board[col+3][row-4] != '':        
                                    goodColumns.append(col+3)
                            # if row-1 is negative then the column spot in question is at the bottom and it's available
                            else:
                                goodColumns.append(col+3)
                    # check for empty column left and up, both col and row there must exist
                    if col-1 >= 0 and row+1 <= 5:
                        if row >= 0:
                            if board[col-1][row] != '':
                                goodColumns.append(col-1)
                            # if row-2 is negative then the column spot in question is at the bottom and it's available
                            else:
                                goodColumns.append(col-1)
        # always return goodColumns array and set good_columns back to goodColumns
        self.good_columns = goodColumns
        return goodColumns

    def remove_disabled_columns_from_good_columns(self):
        goodColumns = self.good_columns
        values_to_remove = []
        # adjust cols enabled to be indexed
        indexed_cols_enabled = []
        for x in self.cols_enabled:
            indexed_cols_enabled.append(x-1)
        print(indexed_cols_enabled)
        print(self.cols_enabled)
        # get values to remove
        for x in goodColumns:
            if x not in indexed_cols_enabled:
                values_to_remove.append(x)
        print('removing from good_columns: ' + str(values_to_remove))
        # remove those values
        for x in values_to_remove:
            goodColumns.remove(x)
        self.good_columns = goodColumns

    # choose a random column based on AI results 
    # (it searches for matches of 3 - 
    # it could be better by searching for something like red-red-empty-red but it is intended to search for red-red-red-empty in all directions, if written right)
    def ai_choose_column(self):
        self.ai_check_almost_matching_columns()
        self.ai_check_almost_matching_negative_diagonal()
        self.ai_check_almost_matching_positive_diagonal()
        self.ai_check_almost_matching_rows()
        self.remove_disabled_columns_from_good_columns()
        goodColumns = self.good_columns
        randomNumber = -1
        print('good columns (by index, so +1 for actual column): ' + str(goodColumns))
        # randomize based on goodColumns
        if len(goodColumns) > 0:
            # add 1 since the goodColumns are based on index
            randomNumber = random.choice(goodColumns)+1
        # else choose random from open columns
        else:
            randomNumber = self.choose_column()
        # reset good_columns to empty
        self.good_columns.clear()
        # return random result
        return randomNumber
    
    # check rows starts at col 1 row 1, then searches col 2 row 1, col 3 row 1, and col 4 row 1
    # have col be limited by 6-3 because beyond col 7 does not exist, and you add up to 3 for col
    def check_matching_rows(self):
        board = self.connect_four_board
        for col in range(4):
            for row in range(6):
                if board[col][row] != '' and board[col+1][row] == board[col][row] and board[col+2][row] == board[col][row] and board[col+3][row] == board[col][row]:
                    return board[col][row]
        return ''
    
    # check cols starts at col 1 row 1, then searches col 1 row 2, col 1 row 3, and col 1 row 4
    # have row be limited by 6-3 because beyond row 6 does not exist, and you add up to 3 for row
    def check_matching_columns(self):
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

    # determine winner checking matching columns/rows/diagonals - print result non empty string if thats found else print empty string
    def determine_winner(self):
        winner_array = [self.check_matching_columns(), self.check_matching_rows(), self.check_matching_positive_diagonal(), self.check_matching_negative_diagonal()]
        for winner_result in winner_array:
            if winner_result != '':
                return winner_result
        return ''
    
    # construct a move message to send to a client, giving the current result of the game, the server's color, a column, and an id
    # the column is given by AI choosing a random column
    def construct_message(self, msg, color, id):
        #col = self.ai_choose_column()
        col = self.ai_choose_column()
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
        return f"{res}|yel|{col}|{id}"
    
# setup running app GUI, this is basically the main class for the app
class TwistedServerApp(App):
    # setup label boolean that goes in center of screen
    label = None
    # setup boards array to store board objects of clients (linkedlist would be better but arrays are done to avoid needing collections library or manual node changing)
    boards = []

    # method to build the app - this sets label to server started, listens for tcp on port 800, then returns the label
    def build(self):
        self.label = Label(text="server started\n")
        reactor.listenTCP(8000, EchoServerFactory(self))
        return self.label
    
    # method to handle messages from clients - id would mean go to handle_message_before_id_setup() while if not id message and not empty go to handle_message_after_id_setup()
    def handle_message(self, msg):
        msg = msg.decode('utf-8')
        self.label.text = "received:  {}\n".format(msg)
        msg_array = msg.split("\n")
        id = None
        for x in msg_array:
            if x == '':
                pass
            elif x[0:2] == 'id':
                id = x[3:]
                return self.handle_message_before_id_setup(id)
            elif x != '':
                print('MSG: ' + x)
                return self.handle_message_after_id_setup(msg)
        
    # find a board given an id, using the boards array
    def find_board(self, id):
        for board in self.boards:
            if board.id == id:
                return board
        return None
    
    # remove a board given a id in the boards array
    def remove_board(self, id):
        board = self.find_board(id)
        if board == None:
            return None
        else:
            self.boards.remove(board)

    # handle message before id setup - try to find a board with the id, if it's found say invalid, if not found make a new board, add it to boards array, and say it's valid
    def handle_message_before_id_setup(self, id):
        board = self.find_board(int(id))
        if board != None:
            msg = 'id_inv: ' + id
            self.label.text += "responded: {}\n".format(msg)
            return msg.encode('utf-8')
        else: 
            id = int(id)
            new_board = BoardToClient(id)
            # for some reason this is needed
            # new_board.reset_variables()
            self.boards.append(new_board)
            #print(self.boards)
            print(self.find_board(id))
            msg = "id_val: " + str(id)
            self.label.text += "responded: {}\n".format(msg)
            return msg.encode('utf-8')

    # handle message after id setup - basically processing moves or if columns are disabled or if client sent a disconnect message
    def handle_message_after_id_setup(self,msg):
        color = ''
        print(msg)
        self.label.text = "received:  {}\n".format(msg)
        msg_array = msg.split("\n")
        msg = ''
        # process if a column is disabled - prioritize this over finding moves just in-case
        # this removes a column from the cols_enalbed variable of a board 
        # this tells the server if there is a tie (if all cols are disabled) then sends that to the client
        for x in msg_array:
            print('> msg: ' + x + " <")
            # case of receiving dis (handle this before trying to add colors for less problems)
            if x[0:3] == 'dis':
                print('reach???')
                idGivenStr = x[6:7]
                idGiven = int(idGivenStr)
                boardGiven = self.find_board(idGiven)
                boardGiven.cols_enabled.remove(int(x[4:5]))
                print('cols enabled: ' + str(boardGiven.cols_enabled))
                if boardGiven.determine_tie() == True:
                    msg = f't|{idGivenStr}'
                    print('connect 4 board: ' + str(boardGiven.connect_four_board))
                    self.label.text += "responded: {}\n".format(msg)
                    return msg.encode('utf-8')
        # process command that is not dis
        for x in msg_array:
            if x == '':
                pass
            # case of receiving a color
            elif x[0:3] != 'dis' and x[0:3] != 'rdc':
                # get color, column, and id and insert to board
                color = x[0:3]
                colToInsertStr = x[4:5]
                colToInsert = int(colToInsertStr)
                idGivenStr = x[6:7]
                print(idGivenStr)
                idGiven = int(idGivenStr)
                print(self.boards)
                boardGiven = self.find_board(idGiven)
                print(boardGiven)
                print(type(boardGiven))
                print(boardGiven.id)
                boardGiven.insert_to_board(colToInsert,color)
                print(boardGiven.connect_four_board)
                # if a winner is determined to be the color of the client, set msg to w| with their id
                if boardGiven.determine_winner() == color:
                    print('winner: ' + boardGiven.determine_winner())
                    msg = f'w|{idGivenStr}'
                    break
                # else if winner is determined to not be the color of the client and isn't empty, set msg to l| with their id
                elif boardGiven.determine_winner() != color and boardGiven.determine_winner() != '':
                    print('winner: ' + boardGiven.determine_winner())
                    msg = f'l|{idGivenStr}'
                    break
                # else if there is a tie, set msg to t| with their id
                elif boardGiven.determine_tie() == True:
                    msg = f't|{idGivenStr}'
                    break

                # switch colors to send (using opposite of client color)
                if x[0:3] == "yel":
                    color = 'red'
                else:
                    color = 'yel'
                # construct a message given the client id, the color, and the msg - this pretty much chooses a column then checks if choosing that column is a winner then constructs the message with the result/id/color/column
                msg = boardGiven.construct_message(msg, color, idGiven)
                print('connect 4 board: ' + str(boardGiven.connect_four_board))
                # add to label text what response is
                self.label.text += "responded: {}\n".format(msg)
                # return msg encoded
                return msg.encode('utf-8')
            # if message is rdc, remove that id given from the boards array
            elif x[0:3] == 'rdc':
                idGivenStr = x[4:5]
                idGiven = int(idGivenStr)
                self.remove_board(idGiven)
                self.label.text += f"removed board id {idGivenStr} from boards\n"
        
        # case of sole disable, just send empty string over, returning msg encoded here
        # except if there is a tie
        return msg.encode('utf-8')

# run the app
if __name__ == '__main__':
    TwistedServerApp().run()
