from tic_tac_toe.message.event_type import EventType
import logging
import random

#singleton class to keep game state in sync with all clients
class ServerSynchronizer:
    def __init__(self):
        self.logger = logging.getLogger('app')
        #dictionary keeping track of clients that are connected
        #key: player that is connected (ip addr, port), value: server message handler for player
        self.connected_player_dict = dict()

        #dictionary keeping track of clients that are registered to play
        #key: player that is registered (ip addr, port), value: player name
        self.registered_player_dict = dict()

        #dictionary keeping track of the turn order for each client (0 or 1)
        self.player_turn_dict = dict()

        #keeps track if the game has started
        self.game_has_started = False

        #keeps track of the current player's turn. It is updated each time a move is
        #received from a player
        self.current_player_turn = 0

        #current state of tic tac board
        self.tic_tac_toe_board = self._create_new_board()

    def process_client_request(self, addr, request):
        success = True
        action = int(request.get("action"))
        internal_request = False

        if "internal_request" in request:
            internal_request = request.get("internal_request")
            request.pop("internal_request")

        if not internal_request:
            #handle register event
            if EventType.REGISTER.value == action:
                response_data, success = self._process_register_request(addr, request)
            #handle de-register event
            elif EventType.DEREGISTER.value == action:
                response_data, success = self._process_deregister_request(addr)
            #handle start event
            elif EventType.START.value == action:
                response_data, success = self._process_start_request(addr)
            #handle stop event
            elif EventType.STOP.value == action:
                response_data, success = self._process_stop_request(addr)
            #handle player move event
            elif EventType.MOVE.value == action:
                response_data, success = self._process_player_move_request(addr, request)
            else:
                response_data = f'Error: invalid action "{action}".'
        #forward message to client
        else:
            response_data = request.get("data")
            if "success" in request:
                success = bool(request.get("success"))

        return self._create_response(success, action, response_data)

    #add new client to connected player dictionary for tracking
    def add_new_connected_client(self, addr, server_message_handler):
        self.connected_player_dict[addr] = server_message_handler

    #remove client from connected player dictionary
    def remove_connected_client(self, addr):
        #remove client from connected players dictionary
        if addr in self.connected_player_dict.keys():
            self.connected_player_dict.pop(addr)

        self._deregister_client(addr)

    #deregisters client if registered and alerts all other clients that the player has disconnected
    def _deregister_client(self, addr):
        #remove client from registered player dictionary if registered
        if addr in self.registered_player_dict.keys():
            response_data = f'"{self.registered_player_dict[addr]}" has left the game.'
            self.logger.info(response_data)
            self.registered_player_dict.pop(addr)

            #finish game as player has left
            if self.game_has_started:
                self.player_turn_dict.pop(addr)
                self._send_fin_message(response_data)
            #notify other player that game can't be started anymore now that other player has left
            else:
                self._send_message_to_clients(addr, EventType.PLAYER_LEFT, response_data)

    #register method
    def _process_register_request(self, addr, request):
        self.logger.info(f'Processing register request from "{addr}"')
        data = request.get("data")
        success = True

        if addr not in self.registered_player_dict:
            if data not in self.registered_player_dict.values():
                self.registered_player_dict[addr] = data
                response_data = f'"{data}" has joined the game.'
                self._send_message_to_clients(addr, EventType.PLAYER_JOINED, response_data)

                #send newly joined player info on previously joined player to get them in sync
                for registered_player in self.registered_player_dict.values():
                    if registered_player != data:
                        self.connected_player_dict[addr].add_internal_request(
                            self._create_response(True, EventType.PLAYER_JOINED.value,
                                                  f'"{registered_player}" has joined the game.',
                                                  True))
            else:
                response_data = f'"{data}" has already been taken as a player name.'
                success = False
        else:
            response_data = f'"{data}" has already been registered.'
            success = False

        self.logger.info(response_data)
        return response_data, success

    def _process_deregister_request(self, addr):
        self.logger.info(f'Processing deregister request from "{addr}"')
        success = True

        if addr in self.registered_player_dict.keys():
            response_data = f'"{self.registered_player_dict[addr]}" has successfully de-registered.'
            self._deregister_client(addr)
        else:
            response_data = f'"{addr}" was not already registered.'
            success = False

        self.logger.info(response_data)
        return response_data, success

    def _process_start_request(self, addr):
        self.logger.info(f'Processing start request from "{addr}"')
        success = True

        #don't allow the game to start if only 1 player has registered
        if len(self.registered_player_dict) > 1:
            if not self.game_has_started:
                self.game_has_started = True
                self.tic_tac_toe_board = self._create_new_board()
                response_data = f'{self.registered_player_dict[addr]} has started the game'
                self._send_message_to_clients(addr, EventType.START, response_data)
                self._determine_player_order()
                self._send_message_to_clients("", EventType.BOARD_UPDATE, self.tic_tac_toe_board)
            else:
                response_data = "The game has already been started"
                success = False
        else:
            response_data = "Not enough players have registered to start the game."
            success = False

        self.logger.info(response_data)
        return response_data, success

    def _process_stop_request(self, addr):
        self.logger.info(f'Processing stop request from "{addr}"')
        success = True

        if self.game_has_started:
            # send fin message to all players since game has been stopped
            response_data = f'{self.registered_player_dict[addr]} has stopped the game'
            self._send_fin_message(response_data)
        else:
            response_data = "The game has not been started yet"
            success = False

        self.logger.info(response_data)
        return response_data, success

    #determines which player will go first and what symbol they will be using
    def _determine_player_order(self):
        player_one_turn = random.randint(0, 1)

        if player_one_turn == 0:
            player_two_turn = 1
        else:
            player_two_turn = 0

        player_one_turn_set = False

        #assign each player their order and symbol
        for registered_player in self.registered_player_dict:
            if not player_one_turn_set:
                self.player_turn_dict[registered_player] = str(player_one_turn) + ":X"
                player_one_turn_set = True

                if player_one_turn == 0:
                    self.current_player_turn = registered_player
            else:
                self.player_turn_dict[registered_player] = str(player_two_turn) + ":O"

                if player_two_turn == 0:
                    self.current_player_turn = registered_player

            #send player turn info to each client
            player_turn_response = self._create_response(True, EventType.ORDER.value,
                                                         self.player_turn_dict[registered_player], True)
            self.connected_player_dict[registered_player].add_internal_request(player_turn_response)

    #processes each move request made by the players
    def _process_player_move_request(self, addr, request):
        self.logger.info(f'Processing player move request from "{addr}"')
        data = int(request.get("data"))
        success = True
        response = ""

        if self.current_player_turn == addr:
            #update board with symbol in position requested by player
            symbol = self.player_turn_dict[addr].split(":")[1]
            self.tic_tac_toe_board[data] = symbol
            self._send_message_to_clients("", EventType.BOARD_UPDATE, self.tic_tac_toe_board)

            #player has won, game over
            if self._player_has_won(symbol):
                self._send_fin_message(f'{self.registered_player_dict[addr]} has won. Game over.')
            #game has resulted in a draw, game over
            elif self._is_draw():
                self._send_fin_message("DRAW! Game over.")
            else:
                #update current player's turn
                for player in self.player_turn_dict:
                    if player != addr:
                        self.current_player_turn = player
                        break
        else:
            success = False
            response = "It is not your turn"

        return response, success

    #end the game
    def _send_fin_message(self, fin_message):
        #reset game state
        self.game_has_started = False
        self._send_message_to_clients("", EventType.FIN, fin_message)

    #method to send message to all clients except to the one that is specified. A blank string can
    #be provided to send a message to all clients
    def _send_message_to_clients(self, addr, event_type, message):
        self.logger.info(f'Sending {event_type.name} to clients: {message}')

        for key in self.registered_player_dict.keys():
            response_data = self._create_response(True, event_type.value, message, True)

            if addr != key:
                self.connected_player_dict[key].add_internal_request(response_data)

    def _create_response(self, success, action, response_data, internal_request=False):
        return dict(success=success, action=action, internal_request=internal_request, data=response_data)

    #method to create new board when new game is started
    def _create_new_board(self):
        return [" " for _ in range(9)]

    #logic to determine when the game is won
    def _player_has_won(self, symbol):
        if (self.tic_tac_toe_board[0] == symbol and self.tic_tac_toe_board[1] == symbol and self.tic_tac_toe_board[2] == symbol) or \
                (self.tic_tac_toe_board[3] == symbol and self.tic_tac_toe_board[4] == symbol and self.tic_tac_toe_board[5] == symbol) or \
                (self.tic_tac_toe_board[6] == symbol and self.tic_tac_toe_board[7] == symbol and self.tic_tac_toe_board[8] == symbol) or \
                (self.tic_tac_toe_board[0] == symbol and self.tic_tac_toe_board[3] == symbol and self.tic_tac_toe_board[6] == symbol) or \
                (self.tic_tac_toe_board[1] == symbol and self.tic_tac_toe_board[4] == symbol and self.tic_tac_toe_board[7] == symbol) or \
                (self.tic_tac_toe_board[2] == symbol and self.tic_tac_toe_board[5] == symbol and self.tic_tac_toe_board[8] == symbol) or \
                (self.tic_tac_toe_board[0] == symbol and self.tic_tac_toe_board[4] == symbol and self.tic_tac_toe_board[8] == symbol) or \
                (self.tic_tac_toe_board[2] == symbol and self.tic_tac_toe_board[4] == symbol and self.tic_tac_toe_board[6] == symbol):
            return True
        else:
            return False

    #logic to determine when the game is at a draw
    def _is_draw(self):
        if " " not in self.tic_tac_toe_board:
            return True
        else:
            return False