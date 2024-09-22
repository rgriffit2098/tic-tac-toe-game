# Statement of Work

## Tic-Tac-Toe Game

**Team:**
Rocky Griffith

## Project Objective

To develop a tic-tac-toe game that runs using python. The game will be hosted on a server where multiple clients will connect to it to play. The purpose of this project is to implement networking fundamentals using socket programming.

This game will involve a minimum of two players where they can choose how many games they would like to play to determine a winner (for example best 2 out of 3). The goal is to expand on this where the game can be played in a tournament fashion when there are more than 2 players connected to the same server.

## Scope

**Inclusions:**

- Server that will keep track of players that connect to the server
- Client that will connect to server
- Client that can see the current state of the tic-tac-toe board
- Client that can input moves to the server
- Server that determines who's turn it is
- Server that can handle input from the client
- Server that can prevent clients from inputing moves when it's not their turn
- Server determines the winner of a round
- Server will reset board after each round
- Create a tic-tac-toe board
- Possible web based implementation if time allows it
- Client can take multiple arguments to show key information to the user
- Server can take multiple arguments to show key information to the user

**Exclusions:**

- Support for multiple servers for redundancy purposes will not be implemented (only 1 server per client sessions). However, multiple servers with different game sessions can be ran if enough resources are provided.

## Deliverables

- A python script to start the server
- A python script to start the client
- Commented code
- Architecture design documentation (server/client)
- Presentation of how the game works

## Timeline

**Key Milestones:**

- Sprint 1: Socket Programming, TCP Client Server (Sept 22-Oct 06)
- Sprint 2:  Develop Game Message Protocol, Manage Client connections (Oct 06-Oct 20)
- Sprint 3:  Multi-player functionality, Synchronize state across clients. (Oct 20-Nov 03)
- Sprint 4:  Game play, Game State (Nov 03-Nov 17)
- Sprint 5: Implement Error Handling and Testing (Nov 17-Dec 6)

**Task Breakdown:**

- Create simple TCP client/server - 4 hrs
- Develop game messaging protocol - 4 hrs
- Managing client connections - 4 hrs
- Multi-player functionality - 8 hrs
- Synchonize state across clients - 4 hrs
- Game play to include tic-tac-toe board - 16 hrs
- Game state - 4 hrs
- Error handling - 8 hrs
- Handle client/server arguments - 4 hrs
- Testing - 16 hrs

## Technical Requirements

**Hardware:**

- One machine/VM to run the server software
- Two or more machines/VMs to run the client software
- A networking equipment so that each of the machines can communicate (routers/switches/cabling)

**Software:**

- Python installed on each host that will be running the software
- Python socket libraries
- Python threading libraries
- Any operating system can work

## Assumptions

The assumptions are that the CSU lab machines will be available and have network connectivity with one another. It is also assumed that they can all host python executables (i.e. the server/client side scripts).

## Roles and Responsibilities

Rocky Griffith is the sole member of the team so he is the project manager and software developer of this project.

## Communication Plan

No communication plan is needed as it is an individual project.
