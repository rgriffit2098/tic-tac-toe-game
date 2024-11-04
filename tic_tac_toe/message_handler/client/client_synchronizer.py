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
        #determines if the player can send a move to the server
        self.can_send_move = False
        #saves the player's turn order so that the client can prevent users from
        #sending moves when it's not their turn (either 0 or 1)
        self.player_turn_order = None
        #saves the player's game symbol sent from the server (either X or O)
        self.player_game_symbol = None
        #current player's turn to make a move in the game
        self.current_turn = False
        self.server_responses = Queue()
        self.state_updated = False
        #keep state of tic-tac-toe board
        self.tic_tac_toe_board = None

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
                if self.tic_tac_toe_board is not None:
                    valid_commands.append(EventType.MOVE.name)

                valid_commands.append(EventType.STOP.name)
            else:
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
            self._handle_board_update_msg(success, data)
        elif EventType.FIN.value == action:
            self._handle_fin_msg(success, data)
        elif EventType.ORDER.value == action:
            self._handle_order_msg(success, data)
        elif EventType.DEREGISTER.value == action:
            self._handle_deregister_msg(success, data)
        elif EventType.ALERT.value == action:
            self._handle_alert_msg(success, data)
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
        self.game_has_started = True

    def _handle_fin_msg(self, success, data):
        #reset client game state
        self.game_has_started = False
        self.player_turn_order = False
        self.can_send_move = False
        self.player_game_symbol = None
        self.current_turn = False
        self.tic_tac_toe_board = None
        self.state_updated = True

    #format new board update for player
    def _handle_board_update_msg(self, success, data):
        self.tic_tac_toe_board = data
        board_update_msg = "Updated board received:\n"
        board_update_msg += self.format_board(data)
        self.server_responses.put(board_update_msg)
        self.state_updated = True

    #save player order
    #order message is sent before board update so state has not been fully updated here yet
    def _handle_order_msg(self, success, data):
        self.player_turn_order = data

    def _handle_deregister_msg(self, success, data):
        if success:
            self.successfully_registered = False
        else:
            self.successfully_registered = True

        self.server_responses.put(data)
        self.register_response_received_from_server = False
        self.state_updated = True

    def _handle_alert_msg(self, success, data):
        self.server_responses.put(data)