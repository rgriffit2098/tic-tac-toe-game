from queue import Queue
from tic_tac_toe.message.event_type import EventType
import logging

#singleton class to handle messages sent from the server
class ClientSynchronizer:
    def __init__(self):
        self.logger = logging.getLogger('app')
        #track if the player has successfully registered
        self.successfully_registered = False
        #track that server responded to let player know if they need to choose a different name
        self.register_response_received_from_server = False
        #keeps track of the game state for the client
        #will update to true when ORDER has been received
        #will update to false when FIN has been received
        self.game_has_started = False
        #saves the player's game symbol sent from the server (either X or O)
        self.player_game_symbol = None
        #current player's turn to make a move in the game
        self.current_turn = False
        #queue all server responses to be retrieved by output thread
        self.server_responses = Queue()
        #game state updated (lets menu know that it may need to refresh itself)
        self.state_updated = False
        #keep state of tic-tac-toe board
        self.tic_tac_toe_board = None
        #game can be started when another player has joined
        self.game_can_be_started = False
        #keeps track if player has sent exit game request
        self.exit_game = False

    #checks to see if the player has successfully registered
    def is_registered(self):
        return self.successfully_registered

    def register_response_received(self):
        return self.register_response_received_from_server

    #gets a list of valid commands that can be output to the player
    def get_valid_commands(self):
        valid_commands = []

        if self.successfully_registered:
            if self.game_has_started:
                if self.tic_tac_toe_board is not None and self.current_turn:
                    valid_commands.append(EventType.MOVE.name)

                valid_commands.append(EventType.STOP.name)
            elif self.game_can_be_started and not self.game_has_started:
                valid_commands.append(EventType.START.name)

            valid_commands.append(EventType.DEREGISTER.name)
        else:
            valid_commands.append(EventType.REGISTER.name)

        return valid_commands

    #reads from server response queue and returns any responses that need to be
    #print out to the player
    def get_server_output(self):
        if not self.server_responses.empty():
            return self.server_responses.get()
        else:
            return None

    #method to detect if anything has changed the state of the game to display the most
    #accurate menu information to the user since the input/output is multithreaded
    def new_state_detected(self):
        new_state_detected = self.state_updated

        #update state updated now that it has been queried
        if self.state_updated:
            self.state_updated = False

        return new_state_detected

    #retrieves if the player has exited the game or not
    def player_has_exit_game(self):
        return self.exit_game

    #determines the possible moves that a player can make on the board
    def get_possible_moves_list(self):
        possible_moves_list = self.tic_tac_toe_board

        # replace empty board entries with indexes to show the player what valid
        # moves they can choose from
        for index, item in enumerate(possible_moves_list):
            if item == " ":
                possible_moves_list[index] = index

        return possible_moves_list

    #formats board with data provided
    def format_board(self, data):
        formatted_board = ""

        for i in range(9):
            formatted_board += "| {} |".format(data[i])

            if (i + 1) % 3 == 0:
                formatted_board += "\n"

        return formatted_board

    #parses server responses and makes updates on client side accordingly
    def process_server_message(self, response):
        self.logger.info(f"Received server message: {response}")
        success = bool(response.get("success"))
        action = int(response.get("action"))
        data = response.get("data")

        if EventType.REGISTER.value == action:
            self._handle_register_msg(success, data)
        elif EventType.START.value == action:
            self._handle_start_msg(success, data)
        elif EventType.BOARD_UPDATE.value == action:
            self._handle_board_update_msg(data)
        elif EventType.FIN.value == action:
            self._handle_fin_msg(data)
        elif EventType.ORDER.value == action:
            self._handle_order_msg(data)
        elif EventType.DEREGISTER.value == action:
            self._handle_deregister_msg(success, data)
        elif EventType.PLAYER_JOINED.value == action:
            self._handle_player_joined_msg(data)
        elif EventType.PLAYER_LEFT.value == action:
            self._handle_player_left_msg(data)
        else:
            self.logger.error(f'Error: invalid action "{action}".')

    def _handle_register_msg(self, success, data):
        if success:
            self.successfully_registered = True
        else:
            self.successfully_registered = False
            self.server_responses.put(data)

        self.register_response_received_from_server = True
        self.state_updated = True

    #game has started but do not update menu options until order
    # and board_update msg has been received
    def _handle_start_msg(self, success, data):
        if success:
            self.game_has_started = True
        else:
            self.server_responses.put(data + "\n")
            self.game_can_be_started = False
            self.state_updated = True

    def _handle_fin_msg(self, data):
        #reset client game state
        self.game_has_started = False
        self.player_game_symbol = None
        self.current_turn = False
        self.tic_tac_toe_board = None
        self.state_updated = True
        self.server_responses.put(data + "\n")

    #format new board update for player
    def _handle_board_update_msg(self, data):
        #if the board has already been initialized then a board update means
        # we need to update whose turn it is
        if self.tic_tac_toe_board is not None:
            #if board is not fully taken up, display MOVE option to user
            if " " in self.tic_tac_toe_board:
                if self.current_turn:
                    self.current_turn = False
                else:
                    self.current_turn = True
            else:
                self.current_turn = False

        self.tic_tac_toe_board = data
        board_update_msg = "Updated board received:\n"
        board_update_msg += self.format_board(data)

        #notify player that it is their turn
        if self.current_turn:
            board_update_msg += "It is your turn"

        self.server_responses.put(board_update_msg + "\n")
        self.state_updated = True

    #save player order
    #order message is sent before board update so state has not been fully updated here yet
    def _handle_order_msg(self, data):
        player_turn, self.player_game_symbol = data.split(":")
        self.server_responses.put("You were assigned symbol: " + self.player_game_symbol + "\n")
        if int(player_turn) == 0:
            self.current_turn = True
        else:
            self.current_turn = False

    def _handle_deregister_msg(self, success, data):
        if success:
            self.successfully_registered = False
        else:
            self.successfully_registered = True

        self.server_responses.put(data + "\n")
        self.register_response_received_from_server = False
        self.state_updated = True
        self.exit_game = True

    #player has joined, update game state
    def _handle_player_joined_msg(self, data):
        self.game_can_be_started = True
        self.server_responses.put(data + "\n")
        self.state_updated = True

    #player left, update game state
    def _handle_player_left_msg(self, data):
        self.game_can_be_started = False
        self.server_responses.put(data + "\n")
        self.state_updated = True