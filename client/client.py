'''
Tomasz Flendrich
nr indeksu 264596
'''
import Pyro4
from datetime import datetime
import Tkinter
import sqlite3
from math import floor
import tkMessageBox
import sys
import os
'''
This module is the client of the Messenger.
'''

class Application():
	def __init__(self):

		self.server=Pyro4.Proxy("PYRONAME:server")
		self.selected_contact=None
		self.initialize()

	def log_in(self, nick, password):
		'''This method runs after clicking the "log in" button.'''

		# illegal characters cause problems for this client only (the server and other clients are safe),
		if nick=="" or any(i in nick for i in '<>:"/\\|?*=#%$+`&{}') or len(nick)>40:
			tkMessageBox.showerror("Wrong username", 'The username cannot be blank,\nlonger than 40 characters\nand cannot have any of these characters:\n< > : " / \\ | ? * = # % $ + ` & { } ')
			return

		message=self.server.log_in(nick, password)
		if message=="wrong password":
			tkMessageBox.showerror("Wrong password", "The password is invalid")
			return
		#logged in succesfuly
		self.database=sqlite3.connect(os.path.dirname(os.path.realpath(__file__))+'\\'+nick+'_incoming.db')
		self.cursor=self.database.cursor()
		try:
			self.cursor.execute('''CREATE TABLE Incoming (Contact text, Incoming integer, Date2 text, Message text)''')
			self.database.commit()
		except sqlite3.OperationalError:
			pass

		self.nick=nick
		self.password=password
		self.log_in_window.destroy()
		self.image_blank=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+'\\images\\blank.gif'
		self.image_red=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+'\\images\\10.gif'
		self.opened_windows=[]
		self.chat_window={}
		self.message_frame={}
		self.message_entry={}
		self.canvas_chat={}
		self.scrollbar={}
		self.message_frame_interior={}
		self.message_label={}
		self.send_button={}
		self.message_string_variable={}
		self.button={}
		self.image={}
		self.new_window() # starts the main window

	def repeated_function(self):
		'''Checks if there are any incoming messages from our contacts.
		Also, receives messages from contacts with whom we have a chat window opened
		and both adds them to the archives and displays them in the chat window'''
		contacts_to_listen_to=[]
		for contact in self.server.new_messages_info_request(self.nick): # for every contact that has any pending messages
			if contact in self.contacts: # we look for those, which we have in our contact list
				contacts_to_listen_to.append(contact[0])
		messages=self.server.send_data(self.nick, self.password, self.opened_windows) # request to send us the messages
		if messages!=None: # for every huge message pack from the server
			for message_pack in messages: # select the messages from one person
				for message in message_pack: # and treat them seperately
					self.cursor.execute("INSERT INTO Incoming Values (?, ?, ?, ?)", (message[0], 1, message[1], message[2]))
					contact_name=message[0]
					previous_messages=self.message_string_variable[contact_name].get()
					previous_messages=previous_messages+"\n"+contact_name+" "+message[1][:-7]+"\n"+message[2]
					self.message_string_variable[contact_name].set(previous_messages)
				self.database.commit()
				try: self.chat_window[message_pack[0][0]].after(50, lambda canvas=self.canvas_chat[message_pack[0][0]]:canvas.yview_moveto(1.0)) # moves the chat to the bottom
				except IndexError:pass
		for contact in set(contacts_to_listen_to).difference(self.opened_windows): # contacts with which we have the chat window closed and they messaged us
			# display the red dot alarming that there are messages incoming
			self.image[contact]=Tkinter.PhotoImage(file=self.image_red)
			self.button[contact].config(image=self.image[contact])

		self.window.after(1000, self.repeated_function)

	def destroy_main_window(self, event):
		'''To close all the chat windows after closing the main window.'''
		for contact_name in self.opened_windows:
			self.chat_window[contact_name].destroy()


	def new_window(self):
		'''This method creates the main window'''
		self.window=Tkinter.Tk()
		self.window.withdraw()
		self.window.title("Messenger")
		self.position(self.window, "right")
		contacts_frame_exterior=Tkinter.Frame(self.window)
		contacts_frame_exterior.grid(column=0, row=0, pady=(0, 15))
		self.canvas=Tkinter.Canvas(contacts_frame_exterior, borderwidth=0, background="#ffffff", width=140, height=250)
		scrollbar=Tkinter.Scrollbar(contacts_frame_exterior, orient="vertical", command=self.canvas.yview)
		self.canvas.configure(yscrollcommand=scrollbar.set)
		scrollbar.pack(side="right",fill="y")
		self.canvas.pack(side="left")
		self.window.bind("<Destroy>", self.destroy_main_window)
		self.window.after(1000, self.repeated_function)
		self.display_contacts()
		self.add_contact_button=Tkinter.Button(self.window, text="Add a contact", command=self.add_contact_dialog)
		self.delete_contact_button=Tkinter.Button(self.window, text="Delete contact", command=lambda:self.delete_contact_button_action())
		self.add_contact_button.grid(column=0, row=1)
		self.delete_contact_button.grid(column=0, row=2)
		self.window.resizable(width=False, height=False)
		self.window.geometry("140x345")
		self.window.deiconify()
		self.window.mainloop()

	def display_contacts(self):
		'''This method displays the contacts on the contact list'''
		message=self.server.give_contacts(self.nick)
		self.contacts=message
		self.contacts_buttons=[]
		self.contacts_new=[]
		try:
			self.contacts_frame.destroy()
		except AttributeError:
			pass # it means that the contacts havent been displayed yet
		self.contacts_frame=Tkinter.Frame(self.canvas, background='#ffffff')
		self.canvas.create_window((0,0),window=self.contacts_frame,anchor='nw')
		self.contacts_frame.bind("<Configure>",self.configure_canvas)

		for x in xrange(len(self.contacts)):
			self.button[self.contacts[x][0]]=Tkinter.Button(self.contacts_frame, text=" "+self.contacts[x][0]+" ", anchor="w", background='#eee6dd', width=17, height=1, command=lambda x=[self.contacts[x][0], x]:self.contact_click_button_action(x))
			image=Tkinter.PhotoImage(file=self.image_blank)
			self.button[self.contacts[x][0]].configure(image=image, compound="right")
			self.button[self.contacts[x][0]].configure(width=140, height=25)
			self.contacts_buttons.append(self.button[self.contacts[x][0]])
			self.contacts_new.append(image)
			self.contacts_buttons[x].grid(column=0, row=x)

			if self.selected_contact!=None and self.selected_contact[0]==self.contacts[x][0]: # if this contact was previously clicked (to delete or to chat to)
				self.button[self.contacts[x][0]].config(background='#b7b7b7')
				self.selected_contact[1]=x


	def configure_canvas(self, event):
		self.canvas.configure(scrollregion=self.canvas.bbox("all"),width=140,height=250) 

	def position(self, window, position):
		'''Positions a window either in the center of the screen, or in the right part of it'''
		if position=="right":
			window.update_idletasks()
			width=window.winfo_width()
			height=window.winfo_height()
			x=(window.winfo_screenwidth()/1.25)-(width/1.25)
			y=(window.winfo_screenheight()/5)#-(height/2)
			window.geometry('{}x{}+{}+{}'.format(width, height, int(floor(x)), int(floor(y))))
		if position=="centre": #zupdejtuj to
			window.update_idletasks()
			width=window.winfo_width()
			height=window.winfo_height()
			x=(window.winfo_screenwidth()/2)-(width/2)
			y=(window.winfo_screenheight()/2)-(height/2)
			window.geometry('{}x{}+{}+{}'.format(width, height, int(floor(x)), int(floor(y))))

	def initialize(self):
		'''Displays the log-in window'''
		self.log_in_window=Tkinter.Tk()
		label_nick=Tkinter.Label(self.log_in_window, text="Nick")
		label_pw=Tkinter.Label(self.log_in_window, text="Password")
		entry_nick=Tkinter.Entry(self.log_in_window, width=10)
		entry_pw=Tkinter.Entry(self.log_in_window, show='*', width=10)
		button_log_in=Tkinter.Button(self.log_in_window, text="Log in (sign up)",command=lambda:self.log_in(entry_nick.get(),entry_pw.get()))
		label_nick.grid(column=0, row=0, ipadx=20)
		label_pw.grid(column=1, row=0, ipadx=20)
		entry_nick.grid(column=0, row=1, ipadx=20, padx=(10, 5))
		entry_pw.grid(column=1, row=1, ipadx=20, padx=(5, 10))
		button_log_in.grid(column=0, row=2, columnspan=2)
		self.log_in_window.bind("<Return>",lambda event:self.log_in(entry_nick.get(),entry_pw.get()))
		self.log_in_window.resizable(width=False, height=False)
		self.log_in_window.title('Messenger')
		self.position(self.log_in_window, "centre")
		self.log_in_window.mainloop()

	def add_contact_dialog(self):
		'''Used when the "Add a contact" button is clicked'''
		new_contact_window=Tkinter.Toplevel()
		new_contact_window.withdraw() # hidden because otherwise it appeared for a fraction of a second in its old place before repositioning
		new_contact_label=Tkinter.Label(new_contact_window, text="Enter the nick to add")
		new_contact_entry=Tkinter.Entry(new_contact_window, width=17)
		new_contact_button=Tkinter.Button(new_contact_window, text="OK", command=lambda:self.add_contact_button_action(new_contact_entry, new_contact_window))
		new_contact_label.grid(column=0, row=0)
		new_contact_entry.grid(column=0, row=1, padx=10)
		new_contact_button.grid(column=0, row=2)
		self.position(new_contact_window, "centre")
		new_contact_window.resizable(width=False, height=False)
		new_contact_window.bind("<Return>", lambda event:self.add_contact_button_action(new_contact_entry, new_contact_window))
		new_contact_window.deiconify()

	def add_contact_button_action(self, entry, window):
		text=entry.get()
		self.server.add_contact(self.nick, text)
		self.display_contacts()
		window.destroy()

	def delete_contact_button_action(self):
		if self.selected_contact==None:
			return # nothing to delete
		self.server.delete_contact(self.nick, self.selected_contact[0])
		self.display_contacts()
		self.selected_contact=None

	def contact_click_button_action(self, contact):
		'''Used when a contact is clicked'''
		if self.selected_contact==None:
			self.selected_contact=contact #zaznacza ta osobe
			self.contacts_buttons[contact[1]].config(background='#b7b7b7')
			return

		if self.selected_contact!=contact and self.selected_contact!=None:
			# change of the selected contact
			self.contacts_buttons[self.selected_contact[1]].config(background='#eee6dd')
			self.contacts_buttons[contact[1]].config(background='#b7b7b7')
			self.selected_contact=contact 
			return

		if self.selected_contact==contact:
			# deselecting a contact
			self.contacts_buttons[self.selected_contact[1]].config(background='#eee6dd')
			self.selected_contact=None
			if (contact[0] in self.opened_windows)==False:
				self.opened_windows.append(contact[0])
				self.new_chat_window(contact[0])

	def new_chat_window(self, contact_name):
		'''Used when you doubleclick a contact.'''
		self.image[contact_name]=Tkinter.PhotoImage(file=self.image_blank) #delete the red dot
		self.button[contact_name].config(image=self.image[contact_name])
		self.chat_window[contact_name]=Tkinter.Tk()
		self.chat_window[contact_name].withdraw()
		self.chat_window[contact_name].bind("<Destroy>", lambda event, contact_name=contact_name:self.destroy_window(event, contact_name))
		self.position(self.chat_window[contact_name], "centre")
		self.chat_window[contact_name].title(contact_name)
		self.message_frame[contact_name]=Tkinter.Frame(self.chat_window[contact_name])
		self.message_entry[contact_name]=Tkinter.Entry(self.chat_window[contact_name], width=37)
		self.send_button[contact_name]=Tkinter.Button(self.chat_window[contact_name], text="Send", command=lambda contact_name=contact_name:self.send_button_action(contact_name))
		self.canvas_chat[contact_name]=Tkinter.Canvas(self.message_frame[contact_name], borderwidth=0, background="#ffffff", width=320, height=400)
		self.scrollbar[contact_name]=Tkinter.Scrollbar(self.message_frame[contact_name], orient="vertical", command=self.canvas_chat[contact_name].yview)
		self.canvas_chat[contact_name].configure(yscrollcommand=self.scrollbar[contact_name].set)
		self.scrollbar[contact_name].pack(side="right",fill="y")
		self.canvas_chat[contact_name].pack(side="left")
		self.message_frame_interior[contact_name]=Tkinter.Frame(self.canvas_chat[contact_name], background='#ffffff')
		self.canvas_chat[contact_name].create_window((0, 0), window=self.message_frame_interior[contact_name], anchor='nw')
		self.message_frame_interior[contact_name].bind("<Configure>", lambda event, contact_name=contact_name:self.configure_canvas_chat(event, contact_name))
		self.message_string_variable[contact_name]=Tkinter.StringVar(self.chat_window[contact_name])
		self.message_label[contact_name]=Tkinter.Label(self.message_frame_interior[contact_name], textvariable=self.message_string_variable[contact_name])
		self.message_label[contact_name].config(width=420, anchor="nw", background='#ffffff', wraplength='340', font=("Helvetica", 10), justify="left")
		self.message_label[contact_name].pack()
		self.canvas_chat[contact_name].configure(width=420, height=400)
		self.set_initial_messages(contact_name) # displays a part of the chat history with that contact
		self.message_frame[contact_name].grid(column=0, row=0, columnspan=2)
		self.message_entry[contact_name].grid(column=0, row=1)
		self.send_button[contact_name].grid(column=1, row=1)
		self.chat_window[contact_name].geometry("365x490")
		self.chat_window[contact_name].bind("<Return>", lambda contact=contact_name:self.send_button_action(contact_name))
		self.chat_window[contact_name].resizable(width=False, height=False)
		self.chat_window[contact_name].deiconify()
		self.chat_window[contact_name].after(100, lambda canvas=self.canvas_chat[contact_name]:canvas.yview_moveto(1.0)) #moves the chat to the bottom


	def configure_canvas_chat(self, event, contact_name):
		self.canvas_chat[contact_name].configure(scrollregion=self.canvas_chat[contact_name].bbox("all"),width=340,height=450) 

	def set_initial_messages(self, contact_name):
		'''Displays the 20 last messages from this contact (if they exist)'''

		self.cursor.execute("SELECT * FROM Incoming WHERE Contact LIKE ? ORDER BY rowid DESC limit 20", (contact_name,))
		results=self.cursor.fetchall()
		text=""
		for x in results: # it reverses them, so that they are in the correct order
			if x[1]==1:
				text=x[0]+" "+x[2][:-7]+"\n"+x[3]+'\n'+text #+x[2][:-7] because x[2] is the date in a format that displays microseconds and we don't want that
			else:
				text=self.nick+" "+x[2][:-7]+"\n"+x[3]+'\n'+text

		self.message_string_variable[contact_name].set(text[:-1]) # [:-1] is to delete the last newline

	def destroy_window(self, event, contact_name):
		'''Used when a window is destroyed.'''
		try:
			self.opened_windows.remove(contact_name)
		except ValueError:
			pass #because destroy calls are also called on widgets, not the window only

	def send_button_action(self, contact_name):
		'''This function adds the messages you send to your database, sends them to the server, and displays them in the chat window.'''
		message=self.message_entry[contact_name].get()
		self.message_entry[contact_name].delete(0, 100000)
		self.server.new_data(self.nick, contact_name, self.password, message)
		self.cursor.execute("INSERT INTO Incoming VALUES (?, ?, ?, ?)", (contact_name, 0, datetime.now(), message))
		self.database.commit()
		previous_messages=self.message_string_variable[contact_name].get()
		previous_messages=previous_messages+"\n"+self.nick+" "+(str(datetime.now()))[:-7]+"\n"+message
		self.message_string_variable[contact_name].set(previous_messages)
		self.chat_window[contact_name].after(50, lambda canvas=self.canvas_chat[contact_name]:canvas.yview_moveto(1.0)) #moves the chat to the bottom

app=Application()
