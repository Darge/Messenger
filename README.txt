=========
Messenger
=========

Messenger contains of two parts: the client and the server, used to create a simple, yet useful online messenger. It uses Pyro4 to communicate between one server and many clients.


Current features:
=================
* Sending and receiving messages
* Password protected nicknames
* Adding and removing contacts, which are stored on the server
* Client-sided archives of messages from the past
* Lightweight
* New incoming message indicator
* GUI

How to run:
===========
To run the Messenger, you have to start the name server using this command:
python -m Pyro4.naming
Then run server.py Then you can run as many clients (client.py) as you want.