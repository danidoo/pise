#!/usr/bin/env python
# encoding: utf-8
"""
pise-cli.py

Created by Daniel Garcia on 2014-07-29.
Copyright (c) 2014 __MyCompanyName__. All rights reserved.
"""

from cmd import Cmd
import pise


class ISEPrompt(Cmd):

	ise_param = {'ipAddress': '', 'username': 'ersadmin', 'password': 'C1sco12345', 'port': '9060'}
	ise = pise.iseERS(debug=False)
	connected = False

	def do_ise(self, args):
		""""Sets ISE: IP address, Username (default=admin), Password (default=C1sco12345) and port (default=9060)"""
		if len(args) == 0:
			print "Not enough arguments. IP address is mandatory"
		else:
			# Should add input validation
			a = args.split()
			self.ise_param['ipAddress'] = a[0]
			if len(a) > 1:
				self.ise_param['username'] = a[1]
			if len(a) > 2:
				self.ise_param['password'] = a[2]
			if len(a) > 3:
				self.ise_param['port'] = a[3]
		print self.ise_param

	def do_connect(self, args):
		""""Connects to ISE System using parameters defined with ise command."""
		self.ise.connect(self.ise_param['ipAddress'], self.ise_param['username'], self.ise_param['password'], Port=self.ise_param['port'], reqTimeout=10)
		self.prompt = 'connected> '
		self.connected = True
	
	def do_showusers(self, args):
		""""Show internal ISE DB users"""
		if not self.connected:
			print "Not connected to ISE server"
		else:
			users = self.ise.getUsers()
			for u in users:
				print u

	def do_adduser(self, args):
		""""Add internal ISE DB user"""
		if not self.connected:
			print "Not connected to ISE server"
		else:
			a = args.split()
			if len(a) < 2:
				print "Not enough arguments. IP address is mandatory"
			else:
				# Should add input validation
				self.ise.addUser(a[0], a[1], description='Created via ERS API by pise-cli.')

	def do_deluser(self, args):
		""""Delete internal ISE DB user/users"""
		if not self.connected:
			print "Not connected to ISE server"
		else:
			users = args.split()
			if len(users) < 1:
				print "Not enough arguments. IP address is mandatory"
			else:
				# Should add input validation
				for u in users:
					self.ise.deleteUser(u)

	def do_quit(self, args):
		"""Quits the program."""
		print "Quitting."
		self.ise.disconnect()
		raise SystemExit

if __name__ == '__main__':
	prompt = ISEPrompt()
	prompt.prompt = '> '
	prompt.cmdloop('Starting prompt...')
