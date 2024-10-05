from tic_tac_toe.service.server import Server
from tic_tac_toe.service.client import Client
import sys

def main():
    if len(sys.argv) < 2:
        sys.exit('Not enough arguments. Choose between server and client.')

    app_type_str = sys.argv[1].lower()
    app_type = None

    if app_type_str == 'server':
        if len(sys.argv) < 3:
            sys.exit('Not enough arguments. server <listening port>')

        app_type = Server(int(sys.argv[2]))

    elif app_type_str == 'client':
        if len(sys.argv) < 4:
            sys.exit('Not enough arguments. client <server ip> <server port>')

        app_type = Client(sys.argv[2], int(sys.argv[3]))

    else:
        sys.exit('Invalid app type. Choose between server and client.')

    app_type.start()

if __name__ == '__main__':
    main()