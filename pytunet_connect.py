import time, sys
import urllib.request, urllib.error, hashlib
import codecs

login_url  = 'http://net.tsinghua.edu.cn/cgi-bin/do_login'
logout_url = 'http://net.tsinghua.edu.cn/cgi-bin/do_logout'
check_url  = 'http://net.tsinghua.edu.cn/cgi-bin/do_login'
query_url  = 'https://usereg.tsinghua.edu.cn/login.php'

times_cnt = {1: 'FIRST', 2: 'SECOND', 3: 'THIRD', 4: 'FORTH', 5: 'FIFTH'}
ret_type  = {'logout_ok'       : 'LOGOUT SUCCESS',
			'not_online_error' : 'NOT ONLINE',
			'ip_exist_error'   : 'IP ALREADY EXISTS',
			'user_tab_error'   : 'THE CERTIFICATION PROGRAM WAS NOT STARTED',
			'username_error'   : 'WRONG USERNAME',
			'user_group_error' : 'ACCOUNT INFOMATION INCORRECT',
			'password_error'   : 'WRONG PASSWORD',
			'status_error'     : 'ACCOUNT OVERDUE, PLEASE RECHARGE',
			'available_error'  : 'ACCOUNT HAS BEEN SUSPENDED',
			'delete_error'     : 'ACCOUNT HAS BEEN DELETED',
			'usernum_error'    : 'USERS NUMBER LIMITED',
			'online_num_error' : 'USERS NUMBER LIMITED',
			'mode_error'       : 'DISABLE WEB REGISTRY',
			'time_policy_error': 'CURRENT TIME IS NOT ALLOWED TO CONNECT',
			'flux_error'       : 'FLUX OVER',
			'ip_error'         : 'IP NOT VALID',
			'mac_error'        : 'MAC NOT VALID',
			'sync_error'       : 'YOUR INFOMATION HAS BEEN MODIFIED, PLEASE TRY AGAIN AFTER 2 MINUTES',
			'ip_alloc'         : 'THE IP HAS BEEN ASSIGNED TO OTHER USER'
			}

version  = '1.1'
sleep_time = 8

#########################################################
#				Main Login/Logout Modules				#
#########################################################

def trans_content(response):
	content = response.read().decode()
	ret = ''
	for ch in content:
		if ch.isalpha() or ch == '_':
			ret += ch
	return ret

def tunet_login(username, password):
	hashcd_md5 = hashlib.md5()
	hashcd_md5.update(password.encode())
	tr_password = hashcd_md5.hexdigest()
	login_data = 'username=' + username + '&password=' + tr_password + '&drop=0&type=1&n=100'
	login_data = login_data.encode()
	request_url = urllib.request.Request(login_url, login_data)
	try:
		response_url = urllib.request.urlopen(request_url)
	except urllib.error.HTTPError as e:
		print ('THE SERVER COULD NOT FULFILL THE REQUEST, PLEASE CHECK YOUR NETWORK')
		sys.exit(1)
	except urllib.error.URLError as e:
		print ('WE FAILED TO REACH A SERVER, PLEASE CHECK YOUR NETWORK')
		sys.exit(1)
	ret = trans_content(response_url)
	print (ret_type.get(ret, 'CONNECTED'))
	return ret

def tunet_logout():
	try:
		response_url = urllib.request.urlopen(logout_url)
	except urllib.error.HTTPError as e:
		print ('THE SERVER COULD NOT FULFILL THE REQUEST, PLEASE CHECK YOUR NETWORK')
		sys.exit(1)
	except urllib.error.URLError as e:
		print ('WE FAILED TO REACH A SERVER, PLEASE CHECK YOUR NETWORK')
		sys.exit(1)
	ret = trans_content(response_url)
	print (ret_type.get(ret, 'CONNECTED'))
	return ret

def tunet_check():
	check_data = 'action=check_online'
	check_data = check_data.encode()
	request_url = urllib.request.Request(check_url, check_data)
	try:
		response_url = urllib.request.urlopen(request_url)
	except urllib.error.HTTPError as e:
		print ('THE SERVER COULD NOT FULFILL THE REQUEST, PLEASE CHECK YOUR NETWORK')
		sys.exit(1)
	except urllib.error.URLError as e:
		print ('WE FAILED TO REACH A SERVER, PLEASE CHECK YOUR NETWORK')
		sys.exit(1)
	ret = trans_content(response_url)
	if ret == '':
		print ('NOT ONLINE')
	else:
		print (ret_type.get(ret, 'CONNECTED'))
	return ret

#########################################################
#					Help&Version Modules				#
#########################################################

def tunet_help():
	print ('-h, --help   : show all options of Tsinghua University Internet Connector')
	print ('-v, --version: show version of Tsinghua University Internet Connector')
	print ('-u           : input your username after \'-u\'')
	print ('-p           : input your password after \'-p\'')
	print ('-a           : enter username and password later, you can login other campus network account')
	print ('-i, --login  : login operation')
	print ('-o, --logout : logout operation')
	print ('-c, --check  : check the internet')
	print ('-q, --query  : query basic infomation, online state and flux usage details')
	print ('-d, --delete : delete an exitent IP')

def tunet_version():
	print ('Tsinghua University Internet Connector ', version)

def tunet_others():
	print ('UNKNOWN OPTIONS')
	print ('WHICH OPTION DO YOU WANT?')
	tunet_help()
	print ('IF ANY ERROR, PLEASE CONTACT im@huhaoyu.com.')

#########################################################
#						Main Part						#
#########################################################

def tunet_connect(username, password):
	ret = 'ip_exist_error'
	for count in range(5):
		print ('%s attempts to connect...' % times_cnt.get(count + 1))
		if ret != tunet_login(username, password):
			break
		if count == 4:
			print ('please try to reconnect after 1 minute')
			break
		print ('try to reconnect after %s seconds' %sleep_time)
		time.sleep(sleep_time)
		print ()