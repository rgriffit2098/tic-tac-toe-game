# Tic-Tac-Toe Game

This a Tic-Tac-Toe game implemented using Python.

**How to play:**

1. **Start the server:** Run the `__main__.py` script with the arguments "server \<server port number\>" on a machine that is designated as the server. Example: `__main__.py` server 6400
2. **Connect clients:** Run the `__main__.py` script with the arguments "client \<server ip\> \<server port number\>" on two different machines that are not the server or on different terminals on the server. Example: `__main__.py` client 127.0.0.1 6400
3. **Play the game:** Players take turns entering their moves into the terminal. The first player to get three in a row wins!

**Technologies used:**

* Python
* Sockets

**Additional resources:**

* [[Link to Python documentation](https://docs.python.org/3/)]
* [[Link to sockets tutorial](https://docs.python.org/3/howto/sockets.html)]
* [[Link to tic-tac-toe tutorial](https://www.wikihow.com/Play-Tic-Tac-Toe)]