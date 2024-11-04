from asyncio import timeout

from altair import value

from tic_tac_toe.message.register import Register
from tic_tac_toe.message.start import Start
from tic_tac_toe.message.stop import Stop
from tic_tac_toe.message.move import Move
from tic_tac_toe.message.deregister import Deregister
from tic_tac_toe.application.application_type import ApplicationType
from tic_tac_toe.message_handler.client.client_message_handler import ClientMessageHandler
from tic_tac_toe.message.event_type import EventType
from threading import Thread
import selectors
import traceback
import socket
import sys
import logging
import datetime
import time

class Client(ApplicationType):
    def __init__(self, server_host, server_port):
        super().__init__()
        self.server_host = server_host
        self.server_port = server_port
        self.client_message_handler = None
        self.client_socket_thread = None
        self.client_input_thread = None
        self.client_output_thread = None

    def start(self):
        self.logger.info("Starting tic-tac-toe client")
        self._start_connection(self.server_host, self.server_port)
        self.client_socket_thread = Thread(target=self._process_socket_traffic)
        self.client_socket_thread.start()

        # start thread to get user input
        self.client_input_thread = Thread(target=self._client_input_handler)
        self.client_input_thread.start()
        #start server output thread
        self.client_output_thread = Thread(target=self._client_output_handler)
        self.client_output_thread.start()

        #while client is still connected to the server
        while self.client_message_handler is not None:
            one = 1

        self.client_socket_thread.join()
        self.client_input_thread.join()
        self.client_output_thread.join()

    #threaded method to get user input to prevent it from blocking server messages from being sent to the user
    def _client_input_handler(self):
        initial_register_request_sent = False
        while self.client_message_handler is not None:
            request = None

            #initial register request
            if not initial_register_request_sent:
                request = self._handle_register_event()
                initial_register_request_sent = True

            #initial register request was sent but player name was taken
            elif (not self.client_message_handler.is_registered() and
                  self.client_message_handler.register_response_received()):
                print("Player name already registered, please pick a different name")
                player_name = input()
                request = self._create_request(Register(player_name))

            #player successfully registered, print out current game state menu
            elif self.client_message_handler.is_registered():
                #get valid commands that the player can send in current state of the game
                command_list = self.client_message_handler.get_valid_commands()

                cmd_prompt = "What would you like to do?\n"
                for index, command in enumerate(command_list):
                    cmd_prompt += f'"{index}". "{command}"\n'

                print(cmd_prompt)
                user_input_is_valid = False
                while not user_input_is_valid:
                    try:
                        user_input = input()
                        val = int(user_input)
                        request = self._create_request_from_command(command_list[val])
                        user_input_is_valid = True
                    except ValueError:
                        print("That's not a valid option, please input a number")
                    except IndexError:
                        print(f'That\'s not a valid option, please input a number between 0 and {len(command_list)-1}')

            if request is not None:
                self.client_message_handler.send_request(request)

            menu_timeout = 0
            while not self.client_message_handler.new_state_detected() and menu_timeout != 30:
                menu_timeout += 1
                time.sleep(1)

                if menu_timeout % 5 == 0:
                    print("Waiting for updates from server")

                if menu_timeout == 30:
                    print("Timed out waiting for new updates from server, would you like to keep waiting for updates? (y/n)")
                    valid_y_n = False

                    #check if user wants to keep waiting for server updates
                    while not valid_y_n:
                        user_input = input()
                        if user_input.lower() == 'y':
                            menu_timeout = 0
                            valid_y_n = True
                        elif user_input.lower() == 'n':
                            valid_y_n = True
                        else:
                            print("Invalid option, select y for yes or n for no")

    #threaded method to print out server messages without input blocking
    def _client_output_handler(self):
        while self.client_message_handler is not None:
            server_output = self.client_message_handler.get_server_output()

            #prints out server output
            if server_output is not None:
                print(server_output)

    def _start_connection(self, host, port):
        addr = (host, port)
        self.logger.info(f'starting connection to {addr}')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.client_message_handler = ClientMessageHandler(self.sel, sock, addr)
        self.sel.register(sock, events, data=self.client_message_handler)
        self.logger.info("connection established with the server")

    def _process_socket_traffic(self):
        try:
            while True:
                events = self.sel.select(timeout=1)
                for key, mask in events:
                    message = key.data
                    try:
                        message.process_events(mask)
                    except Exception:
                        self.logger.error(f'client: error: exception for {message.addr}:\n{traceback.format_exc()}')
                        message.close()
                # Check for a socket being monitored to continue.
                if not self.sel.get_map():
                    break

        except KeyboardInterrupt:
            self.logger.error("caught keyboard interrupt, exiting")
        finally:
            self.sel.close()
            self.client_message_handler = None

    #processes different types of commands that the player has selected
    def _create_request_from_command(self, command):
        request = None

        if EventType.REGISTER.name == command:
            request = self._handle_register_event()
        elif EventType.START.name == command:
            request = self._handle_start_event()
        elif EventType.STOP.name == command:
            request = self._handle_stop_event()
        elif EventType.MOVE.name == command:
            request = self._handle_player_move_event()
        elif EventType.DEREGISTER.name == command:
            request = self._handle_deregister_event()

        return request

    #handle register event for initial register of if player de-registers and re-registers
    def _handle_register_event(self):
        print("What would you like your player name to be?")
        player_name = input()
        return self._create_request(Register(player_name))

    def _handle_start_event(self):
        return self._create_request(Start())

    def _handle_stop_event(self):
        return self._create_request(Stop())

    #handles getting the player's next move
    def _handle_player_move_event(self):
        possible_moves_list = self.client_message_handler.get_possible_moves_list()
        possible_moves_board = self.client_message_handler.format_board(possible_moves_list)
        possible_moves_list_only_int = [item for item in possible_moves_list if item.isdigit()]

        print(possible_moves_board)
        valid_move_picked = False
        player_move = None

        #retrieve the next move from the player
        while not valid_move_picked:
            print("Select a spot that you would like to place your next move:")
            player_move = input()
            player_move = "".join(player_move.split())

            #validate against possible move list of only integers
            if player_move in possible_moves_list_only_int:
                valid_move_picked = True
            else:
                print("That's not a valid move, please try again")

        return self._create_request(Move(player_move))

    def _handle_deregister_event(self):
        return self._create_request(Deregister())

    def _create_request(self, event):
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=event.event_type.value, data=event.data),
        )

def main():
    if len(sys.argv) < 3:
        sys.exit('Not enough arguments: <server ip> <server port>')

    #create app logger
    logger = logging.getLogger('app')
    logger.setLevel(logging.DEBUG)
    log_name = datetime.datetime.now().strftime('client_%d_%m_%Y_%H_%M_%S.log')
    fh = logging.FileHandler(log_name)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    client = Client(sys.argv[1], int(sys.argv[2]))
    client.start()

if __name__ == '__main__':
    main()