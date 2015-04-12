import sys, time, os
import urllib.request, hashlib, http.cookiejar
import codecs, re

query_login_url  = 'https://usereg.tsinghua.edu.cn/do.php'
user_info_url    = 'https://usereg.tsinghua.edu.cn/user_info.php'
online_state_url = 'https://usereg.tsinghua.edu.cn/online_user_ipv4.php'
query_logout_url = 'https://usereg.tsinghua.edu.cn/do.php'
delete_url       = 'https://usereg.tsinghua.edu.cn/online_user_ipv4.php'

info_header = [ '#' * 89,
				'#\t\t\t\tUser Flux Detail Infomation\t\t\t\t#',
				'#' * 89]

# the FLUX_UNIT by usereg.tsinghua.edu.cn, i'm puzzled why not 1024
FLUX_UNIT = 1000

#########################################################
#					File I/O Modules					#
#########################################################

def create_path(relative_path):
 	base_path = os.path.abspath(os.path.dirname(sys.argv[0]))
 	return os.path.join(base_path, relative_path)

def write_inline(file_handler, contents):
	for line in contents:
		file_handler.write(line + '\r\n')

def save_query(contents):
	relative_path = 'USER_DETAIL_INFOMATION.LOG'
	file_handler = open(create_path(relative_path), 'w')
	write_inline(file_handler, info_header)
	file_handler.write('\t\t\t\tDatetime: ' + time.strftime('%Y-%m-%d %H:%M:%S') + '\r\n' + '-' * 89 + '\r\n')
	write_inline(file_handler, contents)
	file_handler.write('\r\n')
	file_handler.close()

#########################################################
#					Connection Modules					#
#########################################################

def create_opener():
	cookie = http.cookiejar.CookieJar()
	cookie_proc = urllib.request.HTTPCookieProcessor(cookie)
	return urllib.request.build_opener(cookie_proc)

def response_login(login_data):
	request_url = urllib.request.Request(query_login_url, login_data.encode())
	try:
		response_url = urllib.request.urlopen(request_url)
	except urllib.error.HTTPError as e:
		print ('THE SERVER COULD NOT FULFILL THE REQUEST, PLEASE CHECK YOUR NETWORK')
		sys.exit(1)
	except urllib.error.URLError as e:
		print ('WE FAILED TO REACH A SERVER, PLEASE CHECK YOUR NETWORK')
		sys.exit(1)
	return response_url.read().decode('gb2312')

#########################################################
#				Main Login/Logout Modules				#
#########################################################

def query_login(username, password):
	hashcd_md5 = hashlib.md5()
	hashcd_md5.update(password.encode())
	tr_password = hashcd_md5.hexdigest()
	login_data = 'user_login_name=' + username + '&user_password=' + tr_password + '&action=login'
	urllib.request.install_opener(create_opener())
	answer = response_login(login_data)
	if answer == 'ok':
		return True
	else:
		return False

def query_logout():
	logout_data = 'action=logout'
	request_url = urllib.request.Request(query_logout_url, logout_data.encode())
	try:
		response_url = urllib.request.urlopen(request_url)
	except urllib.error.HTTPError as e:
		print ('THE SERVER COULD NOT FULFILL THE REQUEST, PLEASE CHECK YOUR NETWORK')
		sys.exit(1)
	except urllib.error.URLError as e:
		print ('WE FAILED TO REACH A SERVER, PLEASE CHECK YOUR NETWORK')
		sys.exit(1)

#########################################################
#				Data Post-Process Modules				#
#########################################################

def post_process(info):
	end_time = time.strftime('%Y-%m-%d')
	start_time = end_time[:8:] + '01'
	flux_detail_url = 'https://usereg.tsinghua.edu.cn/user_detail_list.php?action=balance2&user_login_name=&user_real_name=&desc=&order=&start_time=' + start_time + '&end_time=' + end_time + '&user_ip=&user_mac=&nas_ip=&nas_port=&is_ipv6=0&page=1&offset=200'	
	try:
		response_usr = urllib.request.urlopen(user_info_url)
		response_state = urllib.request.urlopen(online_state_url)
		response_details = urllib.request.urlopen(flux_detail_url)
	except urllib.error.HTTPError as e:
		print ('THE SERVER COULD NOT FULFILL THE REQUEST, PLEASE CHECK YOUR NETWORK')
		sys.exit(1)
	except urllib.error.URLError as e:
		print ('WE FAILED TO REACH A SERVER, PLEASE CHECK YOUR NETWORK')
		sys.exit(1)

	info = flux_account_query(info, response_usr)
	info = online_state_query(info, response_state.read().decode('gb2312'), True)
	info = flux_detail_query(info, response_details)
	
	print ('Your flux details and other infomations are saved in USER_DETAIL_INFOMATION.LOG under the SAME directory')
	return info

#########################################################
#				Integrated Query Modules				#
#########################################################

flux_account_keys = ('用户名', '用户组', '姓名', '证件号', '当前计费组', '使用时长(IPV4)', '使用流量(IPV4)',
					 '使用时长(IPV6)', '使用流量(IPV6)', '帐户余额')
online_state_keys = ()
flux_detail_keys  = ()

#Auxiliary Function
def turn_key(key):
	if key[-5:-1] == 'byte':
		flux, unit = key.split('(')
		flux = float(flux) / FLUX_UNIT / FLUX_UNIT
		new_key = '-->' + str(int(flux)) + '(MB)'
		key += new_key
	return key


def get_days(year, month):
	month_length = (31,28,31,30,31,30,31,31,30,31,30,31)
	month_length_leap = (31,29,31,30,31,30,31,31,30,31,30,31)
	if year % 400 == 0 or year % 100 != 0 and year % 4 == 0:
		return month_length_leap[month-1]
	else:
		return month_length[month-1]

def solve_flux(flux):
	unit = flux[-1]
	val = float(flux[:len(flux)-1:])

	if unit == 'B':
		val /= FLUX_UNIT * FLUX_UNIT
	elif unit == 'K':
		val /= FLUX_UNIT
	elif unit == 'G':
		val *= FLUX_UNIT

	return int(val)

def trans_content(raw):
	raw = re.sub('<[^>]+>|&nbsp;|[\n\t]+|-->',' ',raw)
	raw = re.sub(' +', ' ', raw)
	return raw

def push_front(figure, line):
	tf = []
	tf.append(line)
	return tf + figure

def display_fluxAccount_onlineState(info):
	print()
	for line in info:
		if line[0] != '-':
			print(line)
		else:
			print()

def display_flux_detail(fluxin, year, month, day):
	maxflux = 0
	divide = 10
	figure = []
	for flux in fluxin:
		if flux > maxflux:
			maxflux = flux

	top = str(int(maxflux)) + 'MB|'
	length = len(top)
	mid = str(int(maxflux / 2)) + 'MB|'
	mid = ' ' * (length - len(mid)) + mid
	bottom = '0MB|'
	bottom = ' ' * (length - len(bottom)) + bottom
	unit = maxflux / divide

	for i in range(day):
		fluxin[i] = int(fluxin[i] / unit)

	for i in range(divide):
		line = ''
		if i == divide - 1:
			line = top
		elif i == int((divide - 1) / 2):
			line = mid
		elif i == 0:
			line = bottom
		else:
			line = ' ' * (length - 1) + '|'
		for j in range(day):
			if fluxin[j] > 0:
				line += '**'
				fluxin[j] -= 1
			else:
				line += '  '

		figure = push_front(figure, line)

	figure = push_front(figure, '**每日流量使用统计列表**')
	figure.append(' ' * length + '--' * day)
	date_front = str(year) + '-' + str(month) +'-' + '1'
	date_rear  = str(year) + '-' + str(month) +'-' + str(day)
	date_mid   = str(year) + '-' + str(month) +'-' + '15'
	figure.append(' %s\t\t\t%s\t\t\t%s' %(date_front, date_mid, date_rear))

	for line in figure:
		print(line)

	print()

#Integrated Query
def flux_account_query(info, response):
	info.append('**用户基本信息**')
	done = trans_content(response.read().decode('gb2312'))
	match = re.search('用户名.*?(元) ', done)
	done = match.group()
	tlist = done.split(' ')
	line = ''

	for key in tlist:
		if line != '':
			key = turn_key(key)
			line = line + '\t: ' + key
			info.append(line)
			line = ''
		elif key in flux_account_keys:
			line = key

	info.append('-' * 89)
	return info

def online_state_query(info, raw, do_display):
	info.append('**用户在线状态**')
	
	done = trans_content(raw)
	match = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.*\d{2}:\d{2}', done)

	if match == None:
		info.append('当前没有任何IP在线')
	else:
		info.append('在线IP地址\t登陆日期\t登陆时间')
		done = match.group()
		tlist = done.split(' ')
		line = ''
		count = 0

		for key in tlist:
			if count == 0:
				if re.search('\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3}', key) != None:
					line = key
					count += 1
			elif count == 1:
				if re.search('\d{4}-\d{2}-\d{2}', key) != None:
					line += '\t' + key
					count += 1
			elif count == 2:
				if re.search('\d{2}:\d{2}:\d{2}', key) != None:
					line += '\t' + key
					info.append(line)
					line = ''
					count = 0

	info.append('-' * 89)
	if do_display:
		display_fluxAccount_onlineState(info)
	return info

def flux_detail_query(info, response):
	info.append('**每日流量使用统计列表**')
	info.append('登出日期\t入流量\t出流量')
	done = trans_content(response.read().decode('gb2312'))
	year, month = time.strftime('%Y %m').split(' ')
	days = get_days(int(year), int(month))
	tlist = re.findall('\d{4}-\d{2}-\d{2}|\d+[.]*\d*[BKMG]', done)

	fluxin_perday = [0 for i in range(days)]
	fluxout_perday = [0 for i in range(days)]

	for i in range(len(tlist)):
		if i % 7 == 1:
			year, month, day = tlist[i].split('-')
			iday = int(day)
		elif i % 7 == 2:
			fluxin_perday[iday-1] += solve_flux(tlist[i])
		elif i % 7 == 3:
			fluxout_perday[iday-1] += solve_flux(tlist[i])
	
	for i in range(days):
		if i + 1 < 10:
			d = '0' + str(i + 1)
		else:
			d = str(i + 1)
		info.append('%s\t%s\t%s' %(time.strftime('%Y-%m-') + d, str(fluxin_perday[i]) + 'MB', str(fluxout_perday[i]) + 'MB'))

	display_flux_detail(fluxin_perday, int(year), int(month), days)
	return info

#########################################################
#					IP Offline Modules					#
#########################################################
def tunet_delete(username, password):
	print('FETCHING DATA FROM http://usereg.tsinghua.edu.cn, PLEASE WAIT FOR A MOMENT...')
	is_login = query_login(username, password)
	if is_login:
		info = []
		try:
			response_state = urllib.request.urlopen(online_state_url)
		except urllib.error.HTTPError as e:
			print ('THE SERVER COULD NOT FULFILL THE REQUEST, PLEASE CHECK YOUR NETWORK')
			sys.exit(1)
		except urllib.error.URLError as e:
			print ('WE FAILED TO REACH A SERVER, PLEASE CHECK YOUR NETWORK')
			sys.exit(1)
		raw = response_state.read().decode('gb2312')
		info = online_state_query(info, raw, False)
		tlist = re.findall('\w{32}', raw)

		print()
		if len(info) == 3:
			for i in range(2):
				print (info[i])
			print ('\nNOW SYSTEM LOGOUT')
			query_logout()
			exit(1)
		else:
			for i in range(len(info) - 1):
				if i == 0:
					print (info[i])
				elif i == 1:
					print ('序号\t' + info[i])
				else:
					print (str(i-1) + '\t' + info[i])
			print()

		while True:
			index = int(input('Which IP do you want to delete, please inpute the INDEX(0 to QUIT): '))
			if index in range(1, len(tlist) + 1):
				break
			elif index == 0:
				print ('NOW SYSTEM LOGOUT')
				query_logout()
				exit(0)
			print ('YOUR INPUT IS INVALID, PLEASE INPUT AGAIN\n')

		ip = re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', info[index+1])
		post = 'action=drop&user_ip=' + ip[0] + '&checksum=' + tlist[index-1]
		
		request = urllib.request.Request(delete_url, post.encode())
		try:
			response = urllib.request.urlopen(request)
		except urllib.error.HTTPError as e:
			print ('THE SERVER COULD NOT FULFILL THE REQUEST, PLEASE CHECK YOUR NETWORK')
			sys.exit(1)
		except urllib.error.URLError as e:
			print ('WE FAILED TO REACH A SERVER, PLEASE CHECK YOUR NETWORK')
			sys.exit(1)
		
		if response.read().decode('gb2312') == 'ok':
			print('IP %s IS OFFLINE' %ip[0])
		else:
			print('IP ERROR, CAN\'T DELETE THE ADDRESS')
		query_logout()
	else:
		print ('CAN\'T CAPTURE YOUR FLUX DATA, PLEASE TRY AGAIN LATER')

#########################################################
#						Main Part						#
#########################################################

def tunet_query(username, password):
	print('FETCHING DATA FROM http://usereg.tsinghua.edu.cn, PLEASE WAIT FOR A MOMENT...')
	is_login = query_login(username, password)
	if is_login:
		info = []
		info = post_process(info)
		save_query(info)
		query_logout()
	else:
		print ('CAN\'T CAPTURE YOUR FLUX DATA, PLEASE TRY AGAIN LATER')

def pytunet_query():
	username = 'hhy14'
	password = '123456'
	tunet_query(username, password)

if __name__ == '__main__':
	pytunet_query()