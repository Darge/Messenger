import unittest
import random
import Pyro4
import string
import sys



class Tests(unittest.TestCase):
    pass
    # To run these tests, both server.py and the server name have to be running
#	def setUp(self):
#		self.server=Pyro4.Proxy("PYRONAME:server")
#		self.nick1=str(random.randint(0, 10000000))+str(random.randint(0, 10000000))+str(random.randint(0, 10000000))+str(random.randint(0, 10000000))
#		self.password1=str(random.randint(0, 10000000))+str(random.randint(0, 10000000))+str(random.randint(0, 10000000))+str(random.randint(0, 10000000))
#		self.nick2=str(random.randint(0, 10000000))+str(random.randint(0, 10000000))+str(random.randint(0, 10000000))+str(random.randint(0, 10000000))
#		self.password2=str(random.randint(0, 10000000))+str(random.randint(0, 10000000))+str(random.randint(0, 10000000))+str(random.randint(0, 10000000))
#		self.server.log_in(self.nick1, self.password1)
#		self.server.log_in(self.nick2, self.password2)
#
#	def test_logging_in(self):
#		for x in xrange(100):
#			nick=str(random.randint(0, 10000000))+str(random.randint(0, 10000000))+str(random.randint(0, 10000000))+str(random.randint(0, 10000000))
#			password=str(random.randint(0, 10000000))+str(random.randint(0, 10000000))+str(random.randint(0, 10000000))+str(random.randint(0, 10000000))
#
#			self.assertEqual(self.server.log_in(nick, password), "account created")
#			self.assertEqual(self.server.log_in(nick, password), "correct password")
#			self.assertEqual(self.server.log_in(nick, password+"a"), "wrong password")
#			self.assertEqual(self.server.log_in(nick, ""), "wrong password")
#
#	def test_new_messages_info_request(self):
#
#		for x in xrange(100):
#			message=''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(random.randint(0, 100000)))
#			#message="message_text"
#			self.assertEqual(self.server.new_messages_info_request(self.nick1), [])
#			self.server.new_data(self.nick1, self.nick2, self.password1, message)
#			self.assertFalse(self.server.new_messages_info_request(self.nick2)==[])
#			result=self.server.send_data(self.nick2, self.password2, [self.nick1,])
#			self.assertFalse(result==[[]])
#			self.assertTrue(self.server.send_data(self.nick2, self.password2, [self.nick1,])==[[]])
#
#			self.assertEqual(result[0][0][0], self.nick1)
#			self.assertEqual(result[0][0][2], message)
#
#	def test_contacts(self):
#		self.server.add_contact(self.nick1, self.nick2)
#		result=self.server.give_contacts(self.nick1)
#		self.assertEqual(result[0][0], self.nick2)
#		result2=self.server.delete_contact(self.nick1, self.nick2)
#		self.assertEqual(result2, None)
#

sys.path.append("..")
suite = unittest.TestLoader().loadTestsFromTestCase(Tests)
unittest.TextTestRunner(verbosity=2).run(suite)

