from tic_tac_toe.message.event_type import EventType

#singleton class to handle messages sent from the server
class ClientResponseHandler:
    def __init__(self):
        pass

    #parses server responses and makes updates on client side accordingly
    def process_server_message(self, response):
        print(f"Received server message: {response}")
        success = bool(response.get("success"))
        action = int(response.get("action"))
        data = response.get("data")

        #TODO
        if EventType.BOARD_UPDATE.value == action:
            response_data = f'"{action}" has not been implemented yet.'
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

        print(response_data)