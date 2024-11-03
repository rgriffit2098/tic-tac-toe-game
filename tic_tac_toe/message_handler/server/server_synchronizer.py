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

        #keeps track of the current player's turn. It is updated each time a move is
        #received from a player
        self.current_player_turn = 0

        #current state of tic tac board
        self.tic_tac_toe_board = self._create_new_board()

    def process_client_request(self, addr, request):
        success = True
        action = int(request.get("action"))

        #handle register event
        if EventType.REGISTER.value == action:
            response_data, success = self._process_register_request(addr, request)
        #TODO
        elif EventType.DEREGISTER.value == action:
            response_data = f'"{action}" has not been implemented yet.'
        #TODO
        elif EventType.START.value == action:
            response_data = f'"{action}" has not been implemented yet.'
        #TODO
        elif EventType.STOP.value == action:
            response_data = f'"{action}" has not been implemented yet.'
        #TODO
        elif EventType.MOVE.value == action:
            response_data = f'"{action}" has not been implemented yet.'
        #TODO
        elif EventType.BOARD_UPDATE.value == action:
            response_data = f'"{action}" has not been implemented yet.'
        #TODO
        elif EventType.FIN.value == action:
            response_data = f'"{action}" has not been implemented yet.'
        #alert requests made to the server are made internally to send to all clients
        #so forward on the contents
        elif EventType.ALERT.value == action:
            response_data = request.get("data")
            if request.has_key("success"):
                success = eval(request.get("success"))
        else:
            response_data = f'Error: invalid action "{action}".'

        return self._create_response(success, action, response_data)

    def add_new_connected_client(self, addr, server_message_handler):
        self.connected_player_dict[addr] = server_message_handler

    def remove_connected_client(self, addr):
        #remove client from connected players dictionary
        if addr in self.connected_player_dict:
            del(self.connected_player_dict[addr])

        self._deregister_client(addr)

    #deregisters clients and alerts all other clients
    def _deregister_client(self, addr):
        #remove client from registered player dictionary if registered
        if addr in self.registered_player_dict:
            response_data = f'"{self.registered_player_dict[addr]}" has de-registered.'
            self.logger.info(response_data)
            self._send_message_to_clients(addr, EventType.ALERT, response_data)
            del(self.registered_player_dict[addr])

    #register method
    def _process_register_request(self, addr, request):
        self.logger.info(f'Processing register request from "{addr}"')
        data = request.get("data")
        success = True

        if addr not in self.registered_player_dict:
            if data not in self.registered_player_dict.values():
                self.registered_player_dict[addr] = data
                response_data = f'"{data}" has been registered.'
                self._send_message_to_clients(addr, EventType.ALERT, response_data)
            else:
                response_data = f'"{data}" has already been taken as a player name.'
        else:
            response_data = f'"{data}" has already been registered.'
            success = False

        self.logger.info(response_data)
        return response_data, success

    #method to send message to all clients except to the one that the original response data is for
    def _send_message_to_clients(self, addr, event_type, message):
        self.logger.info("Sending", f"{event_type.name}", "to clients:", f"{message}")
        response_data = self._create_response(True, event_type.value, message)

        for key in self.registered_player_dict.keys():
            if addr != key:
                self.connected_player_dict[key].add_internal_request(response_data)

    def _create_response(self, success, action, response_data):
        return dict(success=success, action=action, data=response_data)

    #method to create new board when new game is started
    def _create_new_board(self):
        return ["" for _ in range(9)]