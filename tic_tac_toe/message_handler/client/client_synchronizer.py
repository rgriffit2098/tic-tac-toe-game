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
        #sending moves when it's not their turn
        self.player_turn_order = 0
        #current player's turn to make a move in the game (either 0 or 1)
        self.current_turn = 0
        self.server_responses = Queue()

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

    #parses server responses and makes updates on client side accordingly
    def process_server_message(self, response):
        self.logger.info(f"Received server message: {response}")
        success = bool(response.get("success"))
        action = int(response.get("action"))
        data = response.get("data")

        if EventType.REGISTER.value == action:
            if success:
                self.successfully_registered = True
            else:
                self.successfully_registered = False

            self.server_responses.put(data)
            self.register_response_received_from_server = True
        #TODO
        elif EventType.BOARD_UPDATE.value == action:
            self._handle_board_update(data)
        #TODO
        elif EventType.FIN.value == action:
            response_data = f'"{action}" has not been implemented yet.'
        #TODO
        elif EventType.ORDER.value == action:
            response_data = f'"{action}" has not been implemented yet.'
        #print alert to client
        elif EventType.ALERT.value == action:
            response_data = data
        else:
            response_data = f'Error: invalid action "{action}".'

    #format new board update for player
    def _handle_board_update(self, data):
        self.tic_tac_toe_board = data
        board_update_msg = "Updated board received:\n"

        for i in range(9):
            board_update_msg += "| {} |".format(data[i])

            if (i + 1) % 3 == 0:
                board_update_msg += "\n"

        self.server_responses.put(board_update_msg)
