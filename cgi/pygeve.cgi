#!/usr/local/bin/python

pyver = '0.35.4.17'

import time
cgistart = time.time()

import _mysql,cgi,re,string,binascii
form=cgi.FieldStorage()

def stderr(err):
        print 'Content-Type: text/html'
        print ''
        print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">'
        print '<html>'
        print 'Error: '+err+'<br>'
        exit()

re_ten=re.compile('^10\.')
re_oneseventwo=re.compile('^172\.')
re_oneninetwo=re.compile('^192\.168')
re_ip=re.compile('^[12]?[0-9]?[0-9]\.[12]?[0-9]?[0-9]\.[12]?[0-9]?[0-9]\.[12]?[0-9]?[0-9]$')
re_ty=re.compile('[a-zA-Z0-9]')
re_tck=re.compile('\'')


##### CGI grabbing
try:
        cid=form["c"].value
except Exception:
        exit()
if cid:
	if re_tck.search(cid):
		stderr('CID format invalid, tick')
	try:
		int(cid)
	except Exception:
		stderr('CID format invalid, int')
	cid = cid[:32]


try:
	sid=form["s"].value
except Exception:
	exit()
if sid:
	if re_tck.search(sid):
		stderr('SID format invalid, tick')
	try:
		int(sid)
	except Exception:
		stderr('SID format invalid, int')
	sid = sid[:8]


try:
	raw=form["raw"].value
except Exception:
	raw='no'
if raw:
	if re_tck.search(raw):
		stderr('Raw format invalid, tick')
	for chr in raw:
		if not re_ty.search(chr):
			stderr('Raw format invalid, type')
	raw = raw[:8]


try:
	hex=form["hex"].value
except Exception:
	hex='no'
if hex:
	if re_tck.search(hex):
		stderr('Hex format invalid, tick')
	for chr in raw:
		if not re_ty.search(chr):
			stderr('Hex format invalid, type')
	hex = hex[:8]


##### IP<->Dec funcs
def rvrslv(rip):
	import socket
	try:
		answ = socket.getnameinfo((rip,80),0)[0]
	except Exception:
		answ = 'NXDomain'
	return answ

def numtoip(n):
	ip = ''
	for div in (16777216,65536,256,1):
		ip += str(n / div)
		if div != 1:
			ip += '.'
		n = n % div
	return ip


##### Set up DB connection
conf=open('/etc/pyg.conf','r')
re_com = re.compile('^#')
conf_db=''
conf_host=''
conf_user=''
conf_passwd=''
for line in conf:
	if not re_com.search(line):
		if line.find('db=') == 0:
			conf_db=line.split('=')[1].rstrip('\n')
		if line.find('host=') == 0:
			conf_host=line.split('=')[1].rstrip('\n')
		if line.find('user=') == 0:
			conf_user=line.split('=')[1].rstrip('\n')
		if line.find('passwd=') == 0:
			conf_passwd=line.split('=')[1].rstrip('\n')
if not conf_db or not conf_host or not conf_user or not conf_passwd:
	stderr(' DB config info could not be read from /etc/pyg.conf<br>Ensure all vars are present and uncommented (db=, host=, user=, passwd=, proxy=).<br>')
db=_mysql.connect(host=conf_host,db=conf_db,user=conf_user,passwd=conf_passwd)


##### Main query: Payload, ips, time, etc
qrystr="Select event.timestamp,sensor.hostname,signature.sig_name,iphdr.ip_src,iphdr.ip_dst,signature.sig_sid from event left join(sensor,signature,iphdr) on (event.sid = sensor.sid and event.signature = signature.sig_id and event.sid = iphdr.sid and event.cid = iphdr.cid) where event.cid = '"+cid+"' and event.sid = '"+sid+"'"
db.query(qrystr)
dbqry=db.store_result()
qryres=dbqry.fetch_row()
if qryres:
	htime=qryres[0][0]
	hsnsr=qryres[0][1]
	hsig=qryres[0][2]
	hsip=numtoip(int(qryres[0][3]))
	hdip=numtoip(int(qryres[0][4]))
	hsid=qryres[0][5]	
else:
        htime="null"
        hsnsr="null"
        hsig="null"
        hsip="null"
        hdip="null"


##### Query for port info
qrystr="Select tcp_sport,tcp_dport from tcphdr where cid = '"+cid+"' and sid = '"+sid+"'"
db.query(qrystr)
dbqry=db.store_result()
qryres=dbqry.fetch_row()
if qryres:
	tcps=": "+qryres[0][0]
        tcpd=": "+qryres[0][1]
else:
	tcps=""
	tcpd=""


##### Query for udp port info
qrystr="Select udp_sport,udp_dport from udphdr where cid = '"+cid+"' and sid = '"+sid+"'"
db.query(qrystr)
dbqry=db.store_result()
qryres=dbqry.fetch_row()
if qryres:
	udps=": "+qryres[0][0]
        udpd=": "+qryres[0][1]
else:
	udps=""
	udpd=""

qrystr="Select icmp_type,icmp_code from icmphdr where cid = '"+cid+"' and sid = '"+sid+"'"
db.query(qrystr)
dbqry=db.store_result()
qryres=dbqry.fetch_row()
if qryres:
	icmty=qryres[0][0]
        icmcd=qryres[0][1]
else:
	icmty=""
	icmcd=""

qrystr="Select data_payload from data where cid = '"+cid+"' and sid = '"+sid+"'"
db.query(qrystr)
dbqry=db.store_result()
qryres=dbqry.fetch_row()
if qryres:
	pyldconv=binascii.unhexlify(str(qryres[0][0]))
else:
	pyldconv="~null~"


##### Build common header
head =""
head += "Time: "+htime+"<br>\n"
head += "Sensor: "+hsnsr+"<br>\n"
head += "Event: "+hsig
head += " (<a href=\"./pygrul.cgi?sig="+hsid+"\">"+hsid+"</a>)<br>\n"
head += "Src IP: <a href=\"./pygqry.cgi?src="+hsip+"&dst="+hsip+"\" target=\"_blank\">"+hsip+"</a> "
head += tcps+udps
if re_ten.search(hsip) or re_oneseventwo.search(hsip) or re_oneseventwo.search(hsip):
	dmn = rvrslv(hsip)
	head += " - "+dmn
else:
	dmn = rvrslv(hsip)
	head += " - "+dmn
	head += "&nbsp;(<a href=\"./pygdmn.cgi?ip="+hsip+"\">info</a>) "
head += "<br>\n"
head += "Dst IP: <a href=\"./pygqry.cgi?src="+hdip+"&dst="+hdip+"\" target=\"_blank\">"+hdip+"</a> "
head += tcpd+udpd
if re_ten.search(hdip) or re_oneseventwo.search(hdip) or re_oneninetwo.search(hdip):
	dmn = rvrslv(hdip)
	head += " - "+dmn	
else:
	dmn = rvrslv(hdip)
	head += " - "+dmn
        head += "&nbsp;(<a href=\"./pygdmn.cgi?ip="+hdip+"\">info</a>) "
head += "<br>\n"


##### Build icmp healder info
if icmty:
	ihead = "ICMP Type:&nbsp"+icmty+"<br>ICMP Code:&nbsp"+icmcd+"<br><br>"
else:
	ihead=""
pyldout = filter(lambda x: x in string.printable, pyldconv)


##### Stamp exec time
cgiend = time.time()


##### Build HTML
print 'Content-Type: text/html\n'
print ''
print '<html>'
print '<head>'
print '<title>Pygmy Event Viewer</title>'
print '</head>'
print '<body>'
print '<div id="main">'
print '<font size="3" face="calibri">'
print '<table width="940">'
print '<tr><td align="right"><input type=button value="Back" onClick="history.go(-1)"><input type=button value="Forward" onClick="history.go(+1)"></td></tr>'
print '</table>'
print '<br>'
print head+'<br>'
print ihead+'<br>'
print '&nbsp;<a href="./pygeve.cgi?s='+sid+'&c='+cid+'">ASCII</a>'
print '&nbsp;<a href="./pygeve.cgi?s='+sid+'&c='+cid+'&raw=yes">RAW</a>'
print '&nbsp;<a href="./pygeve.cgi?s='+sid+'&c='+cid+'&hex=yes">HEX</a>'
print '<br>'
print '<textarea rows="35" cols="115">'

if raw == 'yes' or raw == 'y':
	print pyldconv
elif hex == 'yes' or hex == 'y':
        print str(qryres[0][0]) 
else:
	print pyldout
print '</textarea><br>'
print '('+str(round(cgiend - cgistart,3))+' sec)<br>'
print '</div>'
print '</body>'
print '</html>'
