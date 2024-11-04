from tic_tac_toe.message.event_type import EventType
import logging

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
            del request["internal_request"]

        if not internal_request:
            #handle register event
            if EventType.REGISTER.value == action:
                response_data, success = self._process_register_request(addr, request)
            #handle de-register event
            elif EventType.DEREGISTER.value == action:
                response_data, success = self._process_deregister_request(addr, request)
            #handle start event
            elif EventType.START.value == action:
                response_data, success = self._process_start_request(addr)
            #handle stop event
            elif EventType.STOP.value == action:
                response_data, success = self._process_stop_request(addr)
            #handle player move event
            elif EventType.MOVE.value == action:
                response_data, success = self._process_player_move_request(addr, request)
            #TODO
            elif EventType.BOARD_UPDATE.value == action:
                response_data = f'"{action}" has not been implemented yet.'
            #TODO
            elif EventType.FIN.value == action:
                response_data = f'"{action}" has not been implemented yet.'
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
        if addr in self.connected_player_dict:
            del(self.connected_player_dict[addr])

        self._deregister_client(addr)

    #deregisters client if registered and alerts all other clients that the player has disconnected
    def _deregister_client(self, addr):
        #TODO add logic here to send a FIN message to all players since player has disconnected
        #remove client from registered player dictionary if registered
        if addr in self.registered_player_dict:
            response_data = f'"{self.registered_player_dict[addr]}" has left the game.'
            self.logger.info(response_data)
            del(self.registered_player_dict[addr])
            self._send_message_to_clients(addr, EventType.ALERT, response_data)

    #register method
    def _process_register_request(self, addr, request):
        self.logger.info(f'Processing register request from "{addr}"')
        data = request.get("data")
        success = True

        if addr not in self.registered_player_dict:
            if data not in self.registered_player_dict.values():
                self.registered_player_dict[addr] = data
                response_data = f'"{data}" has joined the game.'
                #TODO update alert to be a new event type so that clients can know when a player has joined/left
                # to update the menu options
                self._send_message_to_clients(addr, EventType.ALERT, response_data)
            else:
                response_data = f'"{data}" has already been taken as a player name.'
                success = False
        else:
            response_data = f'"{data}" has already been registered.'
            success = False

        self.logger.info(response_data)
        return response_data, success

    def _process_deregister_request(self, addr, request):
        self.logger.info(f'Processing deregister request from "{addr}"')
        data = request.get("data")
        success = True

        if addr in self.registered_player_dict:
            if data in self.registered_player_dict.values():
                self._deregister_client(addr)
                response_data = f'"{data}" has successfully de-registered.'
            else:
                response_data = f'"{data}" was not already registered.'
                success = False
        else:
            response_data = f'"{data}" was not already registered.'
            success = False

        self.logger.info(response_data)
        return response_data, success

    def _process_start_request(self, addr):
        self.logger.info(f'Processing start request from "{addr}"')
        success = True

        if not self.game_has_started:
            self.game_has_started = True
            self.tic_tac_toe_board = self._create_new_board()
            response_data = f'{self.registered_player_dict[addr]} has started the game'
            self._send_message_to_clients(addr, EventType.START, response_data)
        else:
            response_data = "The game has already been started"
            success = False

        self.logger.info(response_data)
        return response_data, success

    def _process_stop_request(self, addr):
        self.logger.info(f'Processing stop request from "{addr}"')
        success = True

        if self.game_has_started:
            self.game_has_started = False
            response_data = f'{self.registered_player_dict[addr]} has stopped the game'
            #send fin message to all players since game has been stopped
            self._send_message_to_clients(addr, EventType.FIN, response_data)
        else:
            response_data = "The game has not been started yet"
            success = False

        self.logger.info(response_data)
        return response_data, success

    def _process_player_move_request(self, addr, request):
        self.logger.info(f'Processing player move request from "{addr}"')
        data = request.get("data")
        success = True
        return "Method has not been implemented yet.", success

    #method to send message to all clients except to the one that is specified. A blank string can
    #be provided to send a message to all clients
    def _send_message_to_clients(self, addr, event_type, message):
        self.logger.info(f'Sending {event_type.name} to clients: {message}')
        response_data = self._create_response(True, event_type.value, message, True)

        for key in self.registered_player_dict.keys():
            if addr != key:
                self.connected_player_dict[key].add_internal_request(response_data)

    def _create_response(self, success, action, response_data, internal_request=False):
        return dict(success=success, action=action, data=response_data, internal_request=internal_request)

    #method to create new board when new game is started
    def _create_new_board(self):
        return [" " for _ in range(9)]