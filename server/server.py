'''
Tomasz Flendrich
nr indeksu 264596
'''
import sqlite3
import thread
from datetime import datetime
import Pyro4
import sys
import os

'''
This module is the server of the Messenger. It handles contacting with the clients.
'''
class Server(object):
	def log_in(self, nick, password):
		'''When a client sends us a log in request'''
		database=sqlite3.connect(os.path.dirname(os.path.realpath(__file__))+"\database.db") # thread-safe as long as every thread has a different cursor (and they do)
		cursor=database.cursor()
		cursor.execute("SELECT Rowid, Nick, Password FROM Users WHERE Nick LIKE ?", (nick,))
		existing=cursor.fetchone()
		if existing==None:
			cursor.execute("INSERT INTO Users VALUES (?, ?)", (nick, password))
			database.commit()
			cursor.close()
			return "account created"
		else:
			if existing[1]==nick and existing[2]==password:
				cursor.close()
				return "correct password"
			else:
				cursor.close()
				return "wrong password"

	def new_messages_info_request(self, nick):
		'''When a client wants to know from whom he has pending messages.
		Keep in mind that it doesn't check the password.'''
		database=sqlite3.connect(os.path.dirname(os.path.realpath(__file__))+"\database.db")
		cursor=database.cursor()
		cursor.execute("SELECT DISTINCT Sender FROM Messages WHERE Receiver LIKE ?", (nick,))
		result=cursor.fetchall()
		cursor.close()
		return result

	def send_data(self, nick, password, senders):
		'''Sends the messages coming from senders (a tuple) to a specific contact'''
		database=sqlite3.connect(os.path.dirname(os.path.realpath(__file__))+"\database.db")
		cursor=database.cursor()
		cursor.execute("SELECT Rowid, Nick, Password FROM Users WHERE Nick LIKE ?", (nick,))
		existing=cursor.fetchone()
		if existing==None or existing[2]!=password:
			cursor.close()
			return None # the password is wrong
		results=[]
		for sender in senders:
			cursor.execute("SELECT Sender, Date2, Message FROM Messages WHERE Receiver LIKE ? AND Sender Like ?", (nick, sender))
			result=cursor.fetchall()
			results.append(result)
			cursor.execute("DELETE FROM Messages WHERE Receiver LIKE ? and Sender LIKE ?", (nick, sender))
			database.commit()
			cursor.close()
		return results

	def new_data(self, sender, receiver, password, message):
		'''Receives a message from the sender to its receiver'''
		date=datetime.now()
		database=sqlite3.connect(os.path.dirname(os.path.realpath(__file__))+"\database.db")
		cursor=database.cursor()
		cursor.execute("SELECT Rowid, Nick, Password FROM Users WHERE Nick LIKE ?", (sender,))
		existing=cursor.fetchone()
		if existing!=None:
			if existing[1]==sender and existing[2]==password:
				pass
			else:
				cursor.close()
				return "wrong username or password"
		else:
			cursor.close()
			return "wrong username or password"
		cursor.execute("INSERT INTO Messages VALUES (?, ?, ?, ?)", (sender, receiver, date, message))
		database.commit()
		cursor.close()
		return

	def add_contact(self, nick, contact_nick):
		'''Adds a contact to one's contact list'''
		database=sqlite3.connect(os.path.dirname(os.path.realpath(__file__))+"\database.db")
		cursor=database.cursor()
		cursor.execute("INSERT OR IGNORE INTO Contacts(Nick, Contact) VALUES (?, ?)", (nick, contact_nick)) # Inserts without repetitions
		database.commit()
		cursor.close()


	def delete_contact(self, nick, contact_nick):
		'''Deletes a contact from one's contact list'''
		database=sqlite3.connect(os.path.dirname(os.path.realpath(__file__))+"\database.db")
		cursor=database.cursor()
		cursor.execute("DELETE FROM Contacts WHERE Nick LIKE ? AND Contact LIKE ?", (nick, contact_nick))
		database.commit()
		cursor.close()

	def give_contacts(self, nick):
		'''Returns the contacts of a certain nick'''
		database=sqlite3.connect(os.path.dirname(os.path.realpath(__file__))+"\database.db")
		cursor=database.cursor()
		cursor.execute("SELECT Contact FROM Contacts WHERE Nick LIKE ?", (nick,))
		results=cursor.fetchall()
		cursor.close()
		return results

database=sqlite3.connect(os.path.dirname(os.path.realpath(__file__))+"\database.db")
cursor=database.cursor()
try:
	cursor.execute("CREATE TABLE Users (Nick text, Password text)")
	cursor.execute("CREATE TABLE Messages (Sender text, Receiver text, Date2 text, Message text)")
	cursor.execute("CREATE TABLE Contacts (Nick text, Contact text, UNIQUE(Nick, Contact))")
	database.commit()
except sqlite3.OperationalError:
	pass

cursor.close()
Pyro4.config.HOST
server=Server()
daemon=Pyro4.Daemon()
ns=Pyro4.locateNS()
uri=daemon.register(server)
ns.register("server", uri)

daemon.requestLoop()