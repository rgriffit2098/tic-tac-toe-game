# Tic-Tac-Toe Game

This a Tic-Tac-Toe game implemented using Python.

**How to play:**

1. **Start the server:** Run the `server.py` script with the arguments "\<server port number\>" on a machine that 
is designated as the server. Example: `server.py` 6400
2. **Connect clients:** Run the `client.py` script with the arguments "\<server ip\> \<server port number\>" on two 
different machines that are not the server or on different terminals on the server. Example: `client.py` 127.0.0.1 6400
3. **Play the game:** Players take turns entering their moves into the terminal. The first player to get three in a row wins!

**Technologies used:**

* Python
* Sockets

**Game Message Protocols:**

Clients will send messages to the server in a dictionary wrapped in json, where the dictionary keys are "action" and "data". 
The "action" field will be one of the event types defined below. The "data" field will contain any data needed to process
the action request. 

The server will respond/send updates to clients with a dictionary wrapped in json, where the dictionary keys are "action", 
"data", and "success". The "action" field will either contain the event type that was sent to the server by the client, or 
an update type action such as "Board-update", letting the client know that there was an update made by another client. The 
"data" field will contain either the response to a client request or an update. The "success" field will let the client know 
whether their request was valid, or there was an issue with it. It will always be "True" when the server sends a game update 
to all clients.

***Event Types:***

1. Register - Client will send a register message with the player's name to the server upon initial connection.
2. De-register - Client will send a de-register message when the player chooses to exit the game.
3. Start - Client will send a start message to the server when all players have connected to play.
4. Stop - Client will send a stop message to the server when a player wishes to quit the game without exiting out completely.
5. Move - Client will send a message containing the move (X/O) and location of that move to the server. 
6. Order - Server will send a message to all clients with the order in which the players will take their turns. 
7. Board-update - Server will send a message to all clients with the most up-to-date information after a move has been played. 
8. Fin - Server will send a message to all clients when the game is finished with the reason.
9. Alert - Server will send an alert to all clients containing some information to print to the client

**Additional resources:**

* [[Link to Python documentation](https://docs.python.org/3/)]
* [[Link to sockets tutorial](https://docs.python.org/3/howto/sockets.html)]
* [[Link to tic-tac-toe tutorial](https://www.wikihow.com/Play-Tic-Tac-Toe)]