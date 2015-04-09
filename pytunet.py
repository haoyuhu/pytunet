#########################################################
#						Welcome							#
#	Tsinghua University Internet Connector in Python	#
#					 Version: v1.1 						#
#					Date: 2015/04/09					#
#			By: Haoyu hu	Email: im@huhaoyu.com		#
#			Address: Tsinghua University				#
#########################################################

import pytunet_connect
import pytunet_query
import sys, getopt, getpass, os, re

def pytunet():
	relative_path = 'USERNAME_PASSWORD.txt'
	file_handler = open(pytunet_query.create_path(relative_path), 'r')
	lines = file_handler.readlines()
	if len(lines) != 2:
		print('%s IS DAMAGED, PLEASE CHECK THE CONTENT FORMAT IN THE FILE:' %relative_path)
		print('CONTENT FORMAT AS FOLLOWS:')
		print('username=huhy14\npassword=123456')
		exit(1)
	username = re.sub('\s', '', lines[0])
	password = re.sub('\s', '', lines[1])
	_, username = username.split('=')
	_, password = password.split('=')
	file_handler.close()

	try:
		options, args = getopt.getopt(sys.argv[1:], 'acdhiop:qu:v', ['help', 'login', 'logout', 'check', 'version', 'query', 'delete'])
	except getopt.GetoptError:
		pytunet_connect.tunet_others()
		sys.exit(1)

	want_login = False
	want_query = False
	want_delete = False
	flag = False

	name, value = None, None

	for name, value in options:
		if name in ('-h', '--help'):
			pytunet_connect.tunet_help()
			sys.exit(0)
		elif name in ('-v', '--version'):
			pytunet_connect.tunet_version()
			sys.exit(0)
		elif name == '-a':
			flag = True
		elif name == '-u':
			username = value
		elif name == '-p':
			password = value
		elif name in ('-i', '--login'):
			want_login = True
		elif name in ('-o', '--logout'):
			pytunet_connect.tunet_logout()
			sys.exit(0)
		elif name in ('-c', '--check'):
			pytunet_connect.tunet_check()
			sys.exit(0)
		elif name in ('-q', '--query'):
			want_query = True
		elif name in ('-d', '--delete'):
			want_delete = True

	if flag:
		username = input('username: ')
		password = getpass.getpass('password: ')

	if want_query:
		pytunet_query.tunet_query(username, password)

	if want_delete:
		pytunet_query.tunet_delete(username, password)

	if want_login or not want_query and not want_login and not want_delete:
		pytunet_connect.tunet_connect(username, password)

	# if not want_query and not want_login:
	# 	print ('WARNING: YOU JUST DIDN\'T DO ANYTHING! IF YOU WANT TO CONNECT TO THE CAMPUS NETWORK, THE COMMAND MUST INCLUDE -i OR --login')
	# 	print()
	# 	pytunet_connect.tunet_help()

if __name__ == '__main__':
	pytunet()