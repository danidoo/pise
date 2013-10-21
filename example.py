#!/usr/bin/env python

import pise
import sys

def printUsers(users, username=None):
	printUsers = []
	if username:
		printUsers.append(users[username])
	else:
		printUsers = users.values()
	for user in printUsers:
		print 'Username: ' + user.get('name')
		print 'Enabled: ' + str(user.get('enabled'))

ise = pise.iseERS(debug=True)

ise.connect('1.1.1.1', 'ersadm', 'ISEisC00L')

users = ise.getUsers()
printUsers(users)
print '---------------------'

user = ise.addUser('daniel', 'ISEisC00L')
users = ise.getUsers()

user = ise.getUserDetails('daniel')
users[user['name']] = user
printUsers(users)
print '---------------------'

ise.disableUser('daniel')
user = ise.getUserDetails('daniel')
users[user['name']] = user
printUsers(users)
print '---------------------'

ise.enableUser('daniel')
user = ise.getUserDetails('daniel')
users[user['name']] = user
printUsers(users)
print '---------------------'

ise.deleteUser('daniel')

users = ise.getUsers()
printUsers(users)
print '---------------------'

ise.disconnect()
