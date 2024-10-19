from holoviews.operation.timeseries import resample

from tic_tac_toe.message.event_type import EventType

#singleton class to keep game state in sync with all clients
class ServerRequestHandler:
    def __init__(self):
        #dictionary keeping track of clients that are connected
        #key: player that is connected (ip addr, port), value: server message handler for player
        self.connected_player_dict = dict()

        #dictionary keeping track of clients that are registered to play
        #key: player that is registered (ip addr, port), value: player name
        self.registered_player_dict = dict()

    def process_client_request(self, addr, request):
        success = False
        action = int(request.get("action"))

        #handle register event
        if EventType.REGISTER.value == action:
            response_data = self._process_register_request(addr, request)
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
            response_data = request
        else:
            response_data = f'Error: invalid action "{action}".'

        return self._create_response(success, action, response_data)

    def add_new_connected_client(self, addr, server_message_handler):
        self.connected_player_dict[addr] = server_message_handler

    def remove_new_connected_client(self, addr):
        #remove client from connected players dictionary
        if addr in self.connected_player_dict:
            del(self.connected_player_dict[addr])

        #remove client from registered player dictionary if registered
        if addr in self.registered_player_dict:
            del(self.registered_player_dict[addr])

    #register method
    def _process_register_request(self, addr, request):
        print(f'Processing register request from "{addr}"')
        data = request.get("data")

        if addr not in self.registered_player_dict:
            if data not in self.registered_player_dict.values():
                self.registered_player_dict[addr] = data
                response_data = f'"{data}" has been registered.'
                self._send_message_to_clients(addr, EventType.ALERT, response_data)
            else:
                response_data = f'"{data}" has already been taken as a player name.'
        else:
            response_data = f'"{data}" has already been registered.'

        print(response_data)
        return response_data

    #method to send message to all clients except to the one that the original response data is for
    def _send_message_to_clients(self, addr, event_type, message):
        print("Sending", f"{event_type.name}", "to clients:", f"{message}")
        response_data = self._create_response(True, event_type.value, message)

        for key in self.registered_player_dict.keys():
            if addr != key:
                self.connected_player_dict[key].add_internal_request(response_data)

    def _create_response(self, success, action, response_data):
        return dict(success=success, action=action, data=response_data)