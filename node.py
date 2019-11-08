import random
import time
import hashlib
from constants import *
from message import Message

class Node:

	def __init__(self, x, y, grid=True):

		# coordinates of this node
		self.x = x
		self.y = y

		self.sk = self.create_random_string() # sk = secret key
		self.pk = '' # pk = public key

		# messages this node has received
		self.messages = []

		''' Graph of nodes this node is connected to.

			key:   neighbor's public key
			value: {
				'known_min_distance'  : 4.556284
				'claimed_coordinates' : (10.0, 12.5),
				'neighbors' : { ... repeats ... }
			}

			Example:
			self.neighbors = {
				0 : {
						'pk0' : {
							'known_min_distance'  : 4.556284
							'claimed_coordinates' : (10.0, 12.5),
							'neighbors' : { ... }
						},
						'pk1' : {

						},
						'pk2' : {

						}
				},
				1 : {

				}

			}

			'''
		self.neighbors = {}

		# map of pings to the time they were sent out
		# key   = ping random string
		# value = time ping was sent
		self.pings = {}
		self.time_of_last_ping0 = None

	def main_loop(self):
		t = time.time() # unix time, example: 1424233311.771502

		# ping on PING_FREQUENCY
		ping = None
		if self.time_of_last_ping0 == None \
		or 1.0 / (t - self.time_of_last_ping0) < PING_FREQUENCY:
			ping = self.ping()
			self.pings = self.update_ping_list(ping, t)
			self.time_of_last_ping = t

		messages_to_send = self.respond_to_messages()
		return ping, messages_to_send

	def update_ping_list(self, p, t):

		# save most recent ping
		rs = p.m.split('\n')[2] # rs = random string of ping
		self.pings[rs] = t

		# trim old pings that are out of range R
		pings = {}
		for rs, pt in self.pings.items():
			# rs = random string
			# pt = ping time
			time_since_ping = time.time() - pt
			max_time_since_ping = (2.0 * R) / SIGNAL_SPEED
			if time_since_ping < max_time_since_ping:
				pings[rs] = pt

		return pings

	def create_random_string(self, string_length=256):
		return ''.join(
			random.choice(ALL_CHARS) for i in range(string_length))

	def ping(self):
		random_string = self.create_random_string()
		# return Message(
		# 	'PING!\n' + \
		# 	'Hi Node: %s\n' %  + \
		# 	'This is the random string you sent me.\n' + \
		# 	'%s\n' % old_random_string + \
		# 	'Send me back this new random string.\n' + \
		# 	'%s\n' % new_random_string + \
		# 	'and sign it please.\n' + \
		# 	'\n' + \
		# 	'Sincerely,' + \
		# 	'Node: %s\n' % self.pk)
		return Message(
			'PING!\n' + \
			'Send me back this random string.\n' + \
			'%s\n' % random_string + \
			'and sign it please.\n' + \
			'\n' + \
			'Sincerely,' + \
			'Node: %s\n' % self.pk)

	def echo(self, m):
		specifed_random_string_to_echo = m.m.split('\n')[1]
		return self.send_message('ECHO\n' + specifed_random_string_to_echo + '\n' + self.pk)

	def respond_to_messages(self):
		messages_to_send = []
		unread_messages  = []
		for m in self.messages:
			if m.m.startswith('PING'):
				messages_to_send.append(self.echo(m))

				# if m.m.startswith('ECHO'):

			else: # default of switch (why doesn't python have switches?)
				unread_messages.append(m)

		self.messages = unread_messages
		return messages_to_send

	def send_message(self, m, rpk=None):
		# t   = time of sending this message (int)
		# m   = message to be sent (Message object)
		# rpk = receiver public key

		return Message(m, rpk)

	def print_n(self, num_nodes='?', i='?', start_space='    ', newline_start=False):
		print('%s%sNode %s out of %s at (%.4f, %.4f)' \
			% ('\n' if newline_start else '', start_space, i, num_nodes, self.x, self.y))


