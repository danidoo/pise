#!/usr/bin/env python
# Cisco Identity Services Engine ERS API Library
# By: Daniel Garcia
# Use at your own risk!

import sys
if sys.version_info < (2, 7, 0):
	sys.exit('This library needs at least Python version 2.7')
import httplib
import base64
import string
import xml.etree.ElementTree as ET

class iseERS:
	def __init__(self, debug=False):
		self.debug = debug
		self.conn = None

		self.InternalUserXML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ns3:internaluser name="" id="" description="" xmlns:ns2="ers.ise.cisco.com" xmlns:ns3="identity.ers.ise.cisco.com">
<changePassword>false</changePassword>
<customAttributes></customAttributes>
<email></email>
<enabled>true</enabled>
<firstName></firstName>
<lastName></lastName>
<password></password>
</ns3:internaluser>"""

		self.method = {'CREATE': 'POST', 'READ': 'GET', 'UPDATE': 'PUT', 'DELETE': 'DELETE'}
		self.resources = {
			'EndPoint': {'path': '/ers/config/endpoint', 'header': 'application/vnd.com.cisco.ise.identity.endpoint.1.0+xml'},
			'EndPointsIdentityGroup': {'path': '/ers/config/endpointgroup', 'header': 'application/vnd.com.cisco.ise.identity.endpointgroup.1.0+xml'},
			'InternalUser': {'path': '/ers/config/internaluser', 'header': 'application/vnd.com.cisco.ise.identity.internaluser.1.0+xml'},
			'IdentityGroup': {'path': '/ers/config/identitygroup', 'header': 'application/vnd.com.cisco.ise.identity.identitygroup.1.0+xml'},
		}

	def debugMsg(self, msg):
		if self.debug == True:
			print msg

	def connect(self, IPAdd, ERSAdmin, ERSPasswd, Port='9060', reqTimeout=5):
		self.debugMsg('Opening Connection to ISE ERS Server')
		self.conn = httplib.HTTPSConnection(IPAdd, Port, timeout=reqTimeout)

		self.ersURL = 'https://' + IPAdd + ':' + Port
		self.ersAuthString = 'Basic ' + base64.encodestring('%s:%s' % (ERSAdmin, ERSPasswd)).replace('\n', '')

		url = self.ersURL +  self.resources['InternalUser']['path'] + '/versioninfo'

		body = ''
		self.conn.putrequest(self.method['READ'], url)
		self.conn.putheader('Accept', self.resources['InternalUser']['header'])
		self.conn.putheader('Authorization', self.ersAuthString)
		self.conn.putheader("Content-Length", "%d" % len(body))
		self.conn.endheaders()
		self.conn.send(body)

		resp = self.conn.getresponse()
		data = resp.read()

		if resp.status == 200:
			self.debugMsg('ISE Server connection established')
		else:
			sys.exit('Error connecting with ISE Server, response code: ' + str(resp.status))

	def disconnect(self):
		self.debugMsg('Closing Connection to ISE ERS Server')
		self.conn.close()

	def request(self, operation, resource, objId='', body=''):
		url = self.ersURL + self.resources[resource]['path'] + '/' + objId

		self.debugMsg('--------------\nMaking Request\n--------------\n' + self.method[operation] + ' ' + url +
			'\nAccept: ' + self.resources[resource]['header'] + '\n' +
			'Content-Type: ' + self.resources[resource]['header'] + '\n' +
			'Authorization: ' + self.ersAuthString + '\n' + body)

		self.conn.putrequest(self.method[operation], url)
		self.conn.putheader('Content-Type', self.resources[resource]['header'])
		self.conn.putheader('Accept', self.resources[resource]['header'])
		self.conn.putheader('Authorization', self.ersAuthString)
		self.conn.putheader("Content-Length", "%d" % len(body))
		self.conn.endheaders()
		self.conn.send(body)

		resp = self.conn.getresponse()
		data = resp.read()

		self.debugMsg('------------\nGot Response\n------------\n' + str(resp.status) + ' ' + resp.reason + '\n' + data)

		if resp.status == 200 or resp.status == 201 or resp.status == 204:
			return data
		else:
			sys.exit('Error ' + str(resp.status) + ' making ' + method[operation] + ' request at: ' + url)

	def getUsers(self):
		response = self.request('READ', 'InternalUser')
		usersinfo = ET.fromstring(response)

		self.users = {}
		for resource in usersinfo.iter('resource'):
			user = {}
			user['name'] = resource.attrib['name']
			user['description'] = resource.attrib['description']
			user['id'] = resource.attrib['id']
			user['link'] = resource.find('link').attrib['href']
			self.users[resource.attrib['name']] = user

		return self.users

	def addUser(self, username, password, description='', firstName='', lastName='', email=''):
		user = ET.fromstring(self.InternalUserXML)

		user.attrib['name'] = username
		if user.attrib['name'] in self.users:
			sys.exit('This username already exists in the server\'s Internal Users database')
		user.attrib['description'] = description
		user.find('firstName').text = firstName
		user.find('lastName').text = lastName
		user.find('email').text = email
		user.find('password').text = password
	
		body = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + ET.tostring(user)

		self.request('CREATE', 'InternalUser', body=body)

	def getUserDetails(self, username):
		response = self.request('READ', 'InternalUser', self.users[username]['id'])
		userinfo = ET.fromstring(response)

		self.users[username]['firstName'] = str(userinfo.find('firstName').text)
		self.users[username]['lastName'] = str(userinfo.find('lastName').text)
		self.users[username]['email'] = userinfo.find('email').text
		self.users[username]['enabled'] = (userinfo.find('enabled').text == 'true')
		
		return self.users[username]

	def disableUser(self, username):
		response = self.request('READ', 'InternalUser', objId=self.users[username]['id'])
		userinfo = ET.fromstring(response)

		userinfo.find('enabled').text = 'false'

		body = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + ET.tostring(userinfo)

		self.request('UPDATE', 'InternalUser', objId=self.users[username]['id'], body=body)

	def enableUser(self, username):
		response = self.request('READ', 'InternalUser', objId=self.users[username]['id'])
		userinfo = ET.fromstring(response)

		userinfo.find('enabled').text = 'true'

		body = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + ET.tostring(userinfo)

		self.request('UPDATE', 'InternalUser', objId=self.users[username]['id'], body=body)
	
	def deleteUser(self, username):
		self.request('DELETE', 'InternalUser', objId=self.users[username]['id'])

