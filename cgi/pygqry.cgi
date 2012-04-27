#!/usr/bin/python

pyver = '0.35.4.17'


##### Timing my self
import time
cgistart = time.time()

import os,_mysql,cgi,re,datetime
form=cgi.FieldStorage()


##### Simple Error Out
def stderr(err):
        print 'Content-Type: text/html'
        print ''
        print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">'
        print '<html>'
        print 'Error: '+err+'<br>'
        exit()


##### Connection to DB
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


##### IP<>Dec
def iptonum(n):
        x = int(n.split('.')[0]) * 16777216 + int(n.split('.')[1]) * 65536 + int(n.split('.')[2]) * 256 + int(n.split('.')[3])
        return str(x)

def numtoip(n):
	ip = ''
	for div in (16777216,65536,256,1):
		ip += str(n / div)
		if div != 1:
			ip += '.'
		n = n % div
	return ip


##### Re's for later
re_ten=re.compile('^10\.')
re_oneseventwo=re.compile('^172\.[123][0-9]')
re_oneninetwo=re.compile('^192\.168')
re_ipppp=re.compile('^[12]?[0-9]?[0-9]\.[12]?[0-9]?[0-9]\.[12]?[0-9]?[0-9]\.[12]?[0-9]?[0-9]$')
re_ippp=re.compile('^[12]?[0-9]?[0-9]\.[12]?[0-9]?[0-9]\.[12]?[0-9]?[0-9]\.?$')
re_ipp=re.compile('^[12]?[0-9]?[0-9]\.[12]?[0-9]?[0-9]\.?$')
re_ip=re.compile('^[12]?[0-9]?[0-9]\.?$')
re_dt=re.compile('^20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]$')
re_tm=re.compile('^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]$')
re_hst=re.compile('^[a-zA-Z].*\..*[a-zA-Z]$')
re_ty=re.compile('[a-zA-Z0-9\-\=\.\,\(\)\/\+\*\~\<\>\|\;\:\!\?\/\[\]\{\}\@\$\#\%\_\ ]')
re_tck=re.compile('\'')


##### CGI variable grabbing including input scrubbing,checking and errors
try:
	lim = form["lim"].value
	lim = lim[:7]
except Exception:
	lim = '20000' 
if lim:
	if re_tck.search(lim):
		stderr('Limit format invalid, tick')
	if not re_ty.search(lim):
		stderr('Limit format invalid, type')
	try:
		int(lim)
	except Exception:
		strerr('Limit format invalid, int')	
	lim = int(lim)

try:
	a_yr = form["a_yr"].value
except Exception:
        a_yr = None
if a_yr:
	if re_tck.search(a_yr):
		stderr('Time format invalid, tick')
	if not re_ty.search(a_yr):
		stderr('Time format invalid, type')	
	try:	
		a_yr = a_yr[:4]
		a_yr = int(a_yr)
	except Exception:
		stderr('Time format invalid, int')

try:
        a_mo = form["a_mo"].value
except Exception:
        a_mo = None
if a_mo:
	if re_tck.search(a_mo):
		stderr('Time format invalid, tick')
	if not re_ty.search(a_mo):
		stderr('Time format invalid, type')
	try:
		a_mo = a_mo[:2]
		a_mo = int(a_mo)
	except Exception:
		stderr('Time format invalid, smallint')

try:
        a_dy = form["a_dy"].value
except Exception:
        a_dy = None
if a_dy:
	if re_tck.search(a_dy):
		stderr('Time format invalid, tick')
	if not re_ty.search(a_dy):
		stderr('Time format invalid, type')
	try:
		a_dy = a_dy[:2]
		a_dy = int(a_dy)
	except Exception:
		stderr('Time format invalid, int')

try:
        a_hr = form["a_hr"].value
except Exception:
        a_hr = None
if a_hr:
	if re_tck.search(a_hr):
		stderr('Time format invalid, tick')
	if not re_ty.search(a_hr):
		stderr('Time format invalid, type')
	try:
		a_hr = a_hr[:2]
		a_hr = int(a_hr)
	except Exception:
		stderr('Time format invalid, int')

try:
        a_mn = form["a_mn"].value
except Exception:
        a_mn = None
if a_mn:
	if re_tck.search(a_mn):
		stderr('Time format invalid, tick')
	if not re_ty.search(a_mn):
		stderr('Time format invalid, type')
	try:
		a_mn = a_mn[:2]
		a_mn = int(a_mn)
	except Exception:
		stderr('Time format invalid, int')

try:
        o_yr = form["o_yr"].value
except Exception:
        o_yr = None
if o_yr:
	if re_tck.search(o_yr):
		stderr('Time format invalid')
	if not re_ty.search(o_yr):
		stderr('Time format invalid, type')
	try:	
		o_yr = o_yr[:4]
		o_yr = int(o_yr)
	except Exception:
		stderr('Time format invalid, int')	

try:
        o_mo = form["o_mo"].value
except Exception:
        o_mo = None
if o_mo:
	if re_tck.search(o_mo):
		stderr('Time format invalid, tick')
	if not re_ty.search(o_mo):
		stderr('Time format invalid, type')
	try:
		o_mo = o_mo[:2]
		o_mo = int(o_mo)
	except Exception:
		stderr('Time format invalid, int')

try:
        o_dy = form["o_dy"].value
except Exception:
        o_dy = None
if o_dy:
	if re_tck.search(o_dy):
		stderr('Time format invalid, tick')
	for c in o_dy:
		if not re_ty.search(c):
			stderr('Time format invalid, type')
	try:
		o_dy = o_dy[:2]
		o_dy = int(o_dy)
	except Exception:
		stderr('Time format invalid, int')

try:
        o_hr = form["o_hr"].value
except Exception:
        o_hr = None
if o_hr:
	if re_tck.search(o_hr):
		stderr('Time format invalid, tick')
	for c in o_hr:
		if not re_ty.search(c):
			stderr('Time format invalid, type')
	try:
		o_hr = o_hr[:2]
		o_hr = int(o_hr)
	except Exception:
		stderr('Time format invalid, int')

try:
        o_mn = form["o_mn"].value
except Exception:
        o_mn = None
if o_mn:
	if re_tck.search(o_mn):
		stderr('Time format invalid, tick')
	for c in o_mn:
		if not re_ty.search(c):
			stderr('Time format invalid, type')
	try:
		o_mn = o_mn[:2]
		o_mn = int(o_mn)
	except Exception:
		stderr('Time format invalid, int')

try:
        end = form["o"].value
except Exception:
        end = '60'
if re_tck.search(end):
	stderr('Time format invalid, tick')
for c in end:
	if not re_ty.search(c):
		stderr('Time format invalid, type')
try:
	int(end)
except Exception:
	stderr('Time format invalid, int')


try:
	start = form["a"].value
except Exception:
	# If start is not defined, make it +60 to avoid run away queries
        if int(end) > 60:
                start = str(int(end) - 60)
        else:
                start = '0'
if re_tck.search(start):
	stderr('Time format invalid, tick')
for c in start:
	if not re_ty.search(c):
		stderr('Time format invalid, type')
try:
	int(start)
except Exception:
	stderr('Time format invalid, int')


try:
        mode = form["m"].value
except Exception:
	mode = None 
if mode:
	if re_tck.search(mode):
		stderr('Mode format invalid, tick')
	for c in mode:
		if not re_ty.search(c):
			stderr('Mode format invalid, type')
	mode = mode[:2]


try:
	src = form["src"].value
except Exception:
	src = None
if src:
	if re_tck.search(src):
		stderr('IP format invalid, tick')
	# Checking for /8,/16,/24 style IP input for range searching.
	if not re_ipppp.search(src):
		if not re_ippp.search(src):
			if not re_ipp.search(src):
				if not re_ip.search(src):
					stderr('SRC IP format invalid, type (ranges need trailing dot!)')	
	src = src[:15]


try:
        dst = form["dst"].value
except Exception:
        dst = None
if dst:
	if re_tck.search(dst):
		stderr('IP format invalid, tick')
	if not re_ipppp.search(dst):
		if not re_ippp.search(dst):
			if not re_ipp.search(dst):
				if not re_ip.search(dst):
					stderr('DST IP format invalid, type (ranges need trailing dot!)')
	dst = dst[:15]


try:
        snd = form["snd"].value
except Exception:
        snd = None
if snd:
        if re_tck.search(snd):
                stderr('IP format invalid, tick')
        if not re_ipppp.search(snd):
		if not re_ippp.search(snd):
			if not re_ipp.search(snd):
				if not re_ip.search(snd):
                			stderr('IP format invalid, type')
        snd = snd[:15]
	src = snd
	dst = snd

try:
        snsr = form["snsr"].value
except Exception:
        snsr = None
if snsr:
	if re_tck.search(snsr):
		stderr('Sensor format invalid, tick')
	for c in snsr:
		if not re_ty.search(c):	
			stderr('Sensor format invalid, type')
	snsr = snsr[:5]


try:
        sig = form["sig"].value
except Exception:
        sig = None
if sig:
	if re_tck.search(sig):
		stderr('Sig format invalid, tick')	
	for c in sig:
		if not re_ty.search(c):
			stderr('Sig ID format invalid, type')
	sig = sig[:32]
	try:
		int(sig)
	except Exception:
		stderr('Sig format invalid, int')


try:
        sigx = form["sigx"].value
except Exception:
        sigx = None
if sigx:
	if re_tck.search(sigx):
		stderr('Sig Text format invalid, tick.<br>If searching for a rule name, remove the single tick!')
	for c in sigx:
		if not re_ty.search(c):
			stderr('Sig Text format invalid, type')
	sigx = sigx[:254]
	# Converting sigx for mysql wildcard issue
	re_myq = re.compile('[%_]')
	nsigx = ''
	tsig = ''
	for c in sigx:
		if re_myq.search(c):
			nsigx += chr(92)+c 
		else:
			nsigx += c


try:
        cls = form["cls"].value
except Exception:
        cls = None
if cls:
	if re_tck.search(cls):
		stderr('Cls format invalid, tick')
	for chr in cls:
		if not re_ty.search(chr):
			stderr('Cls format invalid, type')
	cls = cls[:4]
	try:
		int(cls)
	except Exception:
		stderr('Cls format invalid, int')


try:
        clsx = form["clsx"].value
except Exception:
        clsx = None
if clsx:
	if re_tck.search(clsx):
		stderr('Clsx format invalid, tick')
	for chr in clsx:
		if not re_ty.search(chr):
			stderr('Cls format invalid, type')
	clsx = clsx[:254]


try:
	tcpsrc = form["tcpsrc"].value
except Exception:
	tcpsrc = None
if tcpsrc:
	if re_tck.search(tcpsrc):
		stderr('Port format invalid, tick')
	for chr in tcpsrc:
		if not re_ty.search(chr):
			stderr('Port format invalid, type')
	tcpsrc = tcpsrc[:5]
	try:
		int(tcpsrc)
	except Exception:
		stderr('Port format invalid, int')


try:
        tcpdst = form["tcpdst"].value
except Exception:
        tcpdst = None
if tcpdst:
	if re_tck.search(tcpdst):
		stderr('Port format invalid, tick')
	for chr in tcpdst:
		if not re_ty.search(chr):
			stderr('Port format invalid, type')
	tcpdst = tcpdst[:5]
	try:
		int(tcpdst)
	except Exception:
		stderr('Port format invalid, int')


try:
        udpsrc = form["udpsrc"].value
except Exception:
        udpsrc = None
if udpsrc:
	if re_tck.search(udpsrc):
		stderr('Port format invalid, tick')
	for chr in udpsrc:
		if not re_ty.search(udpsrc):
			stderr('Port format invalid, type')
	udpsrc = udpsrc[:5]
	try:
		int(udpsrc)
	except Exception:
		stderr('Port format invalid, int')


try:
        udpdst = str(form["udpdst"].value)
except Exception:
        udpdst = None
if udpdst:
	if re_tck.search(udpdst):
		stderr('Port format invalid, tick')
	for chr in udpdst:
		if not re_ty.search(udpdst):
			stderr('Port format invalid, type')
	udpdst = udpdst[:5]
	try:
		int(udpdst)
	except Exception:
		stderr('Port format invalid, int')
	

##### Build start/end minutes or dates depending on what we have
## Undefined start&end will be 0&60, if specific times exist, calc A and O for query 
## Alpha (0m ago) = TO:, most current date
## Omega (60m ago) = From:, oldest date

now = datetime.datetime.now()
dterr = ''

if a_yr>=1998 and a_mo>=1 and a_mo<=12 and a_dy>=1 and a_dy<=31 and a_hr>=0 and a_hr<=23 and a_mn>=0 and a_mn<=59 and o_yr>=1998 and o_mo>=1 and o_mo<=12 and o_dy>=1 and o_dy<=31 and o_hr>=0 and o_hr<=23 and o_mn>=0 and o_mn<=59:
	# Adjust To: time to present if they are in future
	if datetime.datetime(a_yr,a_mo,a_dy,a_hr,a_mn,now.second,now.microsecond) > now:
		a_yr = now.year
		a_mo = now.month
		a_dy = now.day
		a_hr = now.hour
		a_mn = now.minute		
	# Adjust from: minutes so a_mn and o_mn are always +1
	if datetime.datetime(a_yr,a_mo,a_dy,a_hr,a_mn) == datetime.datetime(o_yr,o_mo,o_dy,o_hr,o_mn):
		o_mn -= 1
	tdt = datetime.datetime(a_yr,a_mo,a_dy,a_hr,a_mn)
	fdt = datetime.datetime(o_yr,o_mo,o_dy,o_hr,o_mn)
	now = datetime.datetime.now()
	ns = now - tdt 
	ne = now - fdt 
	# Cumulative day-minutes and sub day second-minutes for a grand total minutes
	start = str(ns.days * 24 * 60 + ns.seconds / 60)
	end = str(ne.days * 24 * 60 + ne.seconds / 60)
	# If not sane, default
	if int(start) > int(end) or int(end) < 0 or int(start) < 0:
		dterr = 'Defaulted Date '+start+' : '+end
		start = '0'
		end = '60'
## If date vars are not defined, use A & O to define them (cur - a and cur - o)
else:
	adel = datetime.timedelta(minutes=int(start))
	odel = datetime.timedelta(minutes=int(end))
	tdt = now - adel
	fdt = now - odel 
	if fdt == tdt:
		fdt = datetime.datetime(fdt.year,fdt.month,fdt.day,fdt.hour,fdt.minute - 1,fdt.second,fdt.microsecond)


##### Sid, Sensor, IF List
qrystr = "select sid,hostname,interface from sensor order by sid" 
db.query(qrystr)
dbqry=db.store_result()
sensors = {}
rc = 0
while rc != dbqry.num_rows():
        line = dbqry.fetch_row()[0]
        try:
                if line[0] and line[1] and line[2]:
                        sensors[line[0]] = line[1]+' '+line[2]
                        rc += 1
        except Exception:
                rc += 1


##### Event Class List
qrystr = "Select * from sig_class"
db.query(qrystr)
dbqry=db.store_result()
classes = {}
rc = 0
while rc != dbqry.num_rows():
        line = dbqry.fetch_row()
        try:
                if line[0][0] and line[0][1]:
                       	classes[line[0][0]] = line[0][1] 
        except Exception:
                rc += 1

##### Pre-Build IP ranges #####
if src:
	# Full 4 oct. IP, just plug in
	if len(src.rstrip('.').split('.')) == 4:
		srca = src
		srco = src
	# Partial/range IP
	if len(src.rstrip('.').split('.')) < 4:
		# Drop optional trailing dot and make list , don't want null list obj. 
		srcx = src.rstrip('.').split('.')
		# Count listobj and tack on trailing 0/255's for sql range
		if len(srcx) == 3:
			srca = srcx[0]+'.'+srcx[1]+'.'+srcx[2]+'.0'
			srco = srcx[0]+'.'+srcx[1]+'.'+srcx[2]+'.255'
		if len(srcx) == 2:
			srca = srcx[0]+'.'+srcx[1]+'.0.0'
			srco = srcx[0]+'.'+srcx[1]+'.255.255'
		if len(srcx) == 1:
			srca = srcx[0]+'.0.0.0'
			srco = srcx[0]+'.255.255.255'
if dst:
	if len(dst.rstrip('.').split('.')) == 4:
		dsta = dst
		dsto = dst
	if len(dst.rstrip('.').split('.')) < 4:
		dstx = dst.rstrip('.').split('.')
		if len(dstx) == 3:
			dsta = dstx[0]+'.'+dstx[1]+'.'+dstx[2]+'.0'
			dsto = dstx[0]+'.'+dstx[1]+'.'+dstx[2]+'.255'
		if len(dstx) == 2:
			dsta = dstx[0]+'.'+dstx[1]+'.0.0'
			dsto = dstx[0]+'.'+dstx[1]+'.255.255'
		if len(dstx) == 1:
			dsta = dstx[0]+'.0.0.0'
			dsto = dstx[0]+'.255.255.255'


##### Query Building
qrystr =  " Select event.sid, event.cid, event.timestamp, signature.sig_id, signature.sig_name, sig_class.sig_class_id, sig_class.sig_class_name, iphdr.ip_src, iphdr.ip_dst, signature.sig_sid"
if tcpsrc or tcpdst:
	qrystr += ",tcphdr.tcp_sport,tcphdr.tcp_dport"
if udpsrc or udpdst:
	qrystr += ",udphdr.udp_sport,udphdr.udp_dport"
qrystr += " from event left join (iphdr, signature, sig_class"
if tcpsrc or tcpdst:
	qrystr += ",tcphdr"
if udpsrc or udpdst:
	qrystr += ",udphdr"
qrystr += ") on (event.sid = iphdr.sid and event.cid = iphdr.cid and event.signature = signature.sig_id and signature.sig_class_id = sig_class.sig_class_id"
if tcpsrc or tcpdst:
	qrystr += " and tcphdr.sid = event.sid and tcphdr.cid = event.cid"
if udpsrc or udpdst:
	qrystr += " and udphdr.sid = event.sid and udphdr.cid = event.cid"
qrystr += ") where"
qrystr += " timestamp >= Date_Sub(NOW(),INTERVAL "+str(end)+" MINUTE) and"
qrystr += " timestamp <= Date_Sub(NOW(),INTERVAL "+str(start)+" MINUTE)"
if src and dst:
	if src == dst:
		qrystr += " and ((iphdr.ip_src >= '"+iptonum(srca)+"' and iphdr.ip_src <= '"+iptonum(srco)+"')"
		qrystr += " or (iphdr.ip_dst >= '"+iptonum(dsta)+"' and iphdr.ip_dst <= '"+iptonum(dsto)+"'))"	
	else:
		qrystr += " and (iphdr.ip_src >= '"+iptonum(srca)+"' and iphdr.ip_src <= '"+iptonum(srco)+"')"
		qrystr += " and (iphdr.ip_dst >= '"+iptonum(dsta)+"' and iphdr.ip_dst <= '"+iptonum(dsto)+"')"
else:
	if src:
		qrystr += " and (iphdr.ip_src >= '"+iptonum(srca)+"' and iphdr.ip_src <= '"+iptonum(srco)+"')"
	if dst:
		qrystr += " and (iphdr.ip_dst >= '"+iptonum(dsta)+"' and iphdr.ip_dst <= '"+iptonum(dsto)+"')"
if snsr:
	qrystr += " and event.sid = '"+snsr+"'"
if sig:
	qrystr += " and signature.sig_id = '"+sig+"'"
if not sig and sigx:
	qrystr += " and signature.sig_name like '%"+nsigx+"%'" 
if cls:
	qrystr += " and sig_class.sig_class_id = '"+cls+"'"	
if not cls and clsx:
	qrystr += " and sig_class.sig_class_name like '%"+clsx+"%'"
if tcpsrc:
	qrystr += " and tcphdr.tcp_sport = '"+tcpsrc+"'"	
if tcpdst:
	qrystr += " and tcphdr.tcp_dport = '"+tcpdst+"'"
if udpsrc:
	qrystr += " and udphdr.udp_sport = '"+udpsrc+"'"
if udpdst:
	qrystr += " and udphdr.udp_dport = '"+udpdst+"'"
qrystr += " order by "
if mode == 'es' or mode == 'se':
	qrystr += "iphdr.ip_src,event.timestamp desc"
if mode == 'ed' or mode == 'de':
	qrystr += "iphdr.ip_dst,event.timestamp desc"
if mode == 'sd':
	qrystr += "iphdr.ip_src,iphdr.ip_dst,event.timestamp desc"
if mode == 'ds':
	qrystr += "iphdr.ip_dst,iphdr.ip_src,event.timestamp desc"
if not mode:
	qrystr += "event.timestamp desc"
qryout = qrystr 


##### Store query results in "store"
db.query(qrystr)
dbqry=db.store_result()
## Empty sets/list for results
usrc = set() 
udst = set() 
ueve = set()
store = []
## Results count,cap flag, limit  
rc = 0
cap = 0
qrc = int(dbqry.num_rows())
acu = str(qrc)
if qrc > lim:
	cap = 1 
	qrc = lim 
while rc != qrc:
	line = dbqry.fetch_row()
	try:
		if line[0][0] and line[0][1] and line[0][2] and line[0][3] and line[0][4] and line [0][5] and line[0][6] and line[0][7] and line[0][8]:
			store.append(line)
			usrc.add(line[0][7])
			udst.add(line[0][8])
			ueve.add(line[0][4]+'~'+line[0][3])		
			rc += 1
	except Exception:
		rc += 1
qryend = time.time()


##### HTML Header w/ mktree js
print 'Content-Type: text/html'
print ''
print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">'
print '<html>'
print '<head>'
print '<title>Pygmy Query Engine</title>'
print '<!-- Big thanks to Matt Kruse for mktree.js (www.javascripttoolbox.com/lib/mktree/source.php) -->'
print '<link rel="stylesheet" href="../pygmy/mktree.css" type="text/css">'
print '<script src="../pygmy/mktree.js" type="text/javascript" ></script>'
print '<script src="../pygmy/popup.js" type="text/javascript" ></script>'
print '</head>'
print '<body>'
print '<font face="calibri">'


##### Print Search Bar
print '<form action="../cgi-bin/pygqry.cgi" method="post">'
print '<table frame="box" rules="none" width="1300" >'
print '<tr>'
print '<td><form><input type="button" value="Pygmy" OnClick="window.location.href=\'./pygmy.cgi\'"></form></td>'
print '<td align="right"><font size="1">Year&nbsp;&nbsp;</td>'
print '<td align="right"><font size="1">Month&nbsp;&nbsp;</td>'
print '<td align="right"><font size="1">Day&nbsp;&nbsp;</td>'
print '<td align="right"><font size="1">Hour&nbsp;&nbsp;</td>'
print '<td align="right"><font size="1">Min&nbsp;&nbsp;</td>'
print '<td>&nbsp;</td>'
print '<td>&nbsp;</td>'
print '<td align="right"><font size="1">Source&nbsp;&nbsp;</td>'
print '<td align="right"><font size="1">Destination&nbsp;&nbsp;</td>'
print '<td>&nbsp;</td>'
print '<td>&nbsp;</td>'
print '<td align="right"><font size="1">Source&nbsp;&nbsp;</td>'
print '<td align="right"><font size="1">Destination&nbsp;&nbsp;</td>'
print '<td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td><font size="1">'+pyver+'</font></td>'
print '</tr>'
print '<td align="right"><font size="2">From:</td>'
print '<td><input type="text" name="o_yr" value="'+str(fdt.year)+'" style="width:40px;text-align:right"></td>'
print '<td><input type="text" name="o_mo" value="'+str(fdt.month)+'" style="width:30px;text-align:right"></td>'
print '<td><input type="text" name="o_dy" value="'+str(fdt.day)+'" style="width:30px;text-align:right"></td>'
print '<td><input type="text" name="o_hr" value="'+str(fdt.hour)+'" style="width:30px;text-align:right"></td>'
print '<td><input type="text" name="o_mn" value="'+str(fdt.minute)+'" style="width:30px;text-align:right"></td>'
print '<td>&nbsp;</td>'
print '<td align="right"><font size="2">IP:</td>'
print '<td><input type="text" name="src" style="width:100px;text-align: right" '
if src:
	print 'value="'+src+'"'
print '></td>'
print '<td><input type="text" name="dst" style="width:100px;text-align: right" '
if dst:
	print 'value="'+dst+'"'
print '></td>'
print '<td>&nbsp;</td>'
print '<td><font size="2">TCP Port:</td>'
print '<td><input type="text" name="tcpsrc" style="width:50px;text-align: right" '
if tcpsrc:
	print 'value="'+tcpsrc+'"'
print '></td>'
print '<td><input type="text" name="tcpdst" style="width:50px;text-align: right" '
if tcpdst:
	print 'value="'+tcpdst+'"'
print '></td>'
print '<td>&nbsp;</td>'
print '<td><font size="2">Sensor:</td>'
print '<td><select name="snsr" style="width:150px">'
print ' <option value="" width="800"> - </option>'
for s in sensors:
        print ' <option '
	if s == snsr:
		print 'selected '	
	print 'value="'+s+'">'+sensors[s]+'</option>'
print '</select></td>'
print '<td>&nbsp;</td>'
print '<td><font size="2">Sig Txt:</td><td><input type="text" name="sigx" style="width:100px;text-align:right"'
if sigx:
	print 'value="'+sigx+'"'
print '></td>'
print '<td><input type="radio" name="m" value="sd" '
if mode == 'sd':
	print 'checked '
print '><font size="2">Src>Dst</td>'
print '<td><input type="radio" name="m" value="se" '
if mode == 'se':
	print 'checked '
print '><font size="2">Src>Eve</td>'
print '<td><input type="radio" name="m" value="es" '
if mode == 'es':
        print 'checked '
print '><font size="2">Eve>Src&nbsp;</td>'
print '</tr>'
print '<td align="right"><font size="2">To:</td>'
print '<td><input type="text" name="a_yr" value="'+str(tdt.year)+'" style="width:40px;text-align:right"></td>'
print '<td><input type="text" name="a_mo" value="'+str(tdt.month)+'" style="width:30px;text-align:right"></td>'
print '<td><input type="text" name="a_dy" value="'+str(tdt.day)+'" style="width:30px;text-align:right"></td>'
print '<td><input type="text" name="a_hr" value="'+str(tdt.hour)+'" style="width:30px;text-align:right"></td>'
print '<td><input type="text" name="a_mn" value="'+str(tdt.minute)+'" style="width:30px;text-align:right"></td>'
print '<td>&nbsp;</td>'
print '<td>&nbsp;</td>'
print '<td><input type="text" name="snd" style="width:100px;text-align: right"></td>'
print '<td><font size="2">&larr;(src <u>or</u> dst)</td>'
print '<td>&nbsp;</td>'
print '<td><font size="2">UDP Port:</td>'
print '<td><input type="text" name="udpsrc" style="width:50px;text-align: right" '
if udpsrc:
	print 'value="'+udpsrc+'"'
print '></td>'
print '<td><input type="text" name="udpdst" style="width:50px;text-align: right" '
if udpdst:
	print 'value="'+udpdst+'"' 
print '></td>'
print '<td>&nbsp;</td>'
print '<td><font size="2">Class:</td>'
print '<td><select name="cls" style="width:150px">'
print ' <option value=""> - </option>'
for c in classes:
        print ' <option '
	if classes[c] == clsx or c == cls:
		print 'selected '	
	print 'value="'+c+'">'+classes[c]+'</option>'
print '</select></td>'
print '<td>&nbsp;</td>'
print '<td><font size="2">Sig ID:</td>'
print '<td><input type="text" name="sig" style="width:100px;text-align: right" '
if sig:
	print 'value="'+sig+'"'
print '></td>'
print '<td><input type="radio" name="m" value="ds" '
if mode == 'ds':
	print 'checked ' 
print '><font size="2">Dst>Src</td></td>'
print '<td><input type="radio" name="m" value="de" '
if mode == 'de':
	print 'checked '
print '><font size="2">Dst>Eve</td></td>'
print '<td><input type="radio" name="m" value="ed" '
if mode == 'ed':
        print 'checked '
print '><font size="2">Eve>Dst&nbsp;</td></td>'
print '</tr>'

## Bottom
print '<tr>'
print '<td align="center"><input type="submit" value="Query"></td>'
print '<td></td><td></td><td></td><td></td><td></td><td></td>'
print '<td></td><td></td><td></td><td></td><td></td><td></td>'
print '<td></td><td></td>'
print '<td><font size="2">Limit:</td><td><input type="text" name="lim" style="width:50px;text-align:right"><font size="2" >&nbsp;&nbsp;'
if lim >= qrc:
        print str(qrc)
else:
        print str(lim)
print '/ '+acu+'</td><td></td><td></td><td></td><td></td>'
print '<td></td>'
print '<td><input type="radio" name="m" value="" '
if not mode:
        print 'checked '
print '><font size="2">Flat</td>'
print '</form>'
print '</tr>'
print '</table>'
print '<font size="1">'+dterr+'</font>'


##### Time sliding buttons
def slide(sa,sn):
        print '<td style="height:12px;align:center">'
	print '<form method="post" action="/cgi-bin/pygqry.cgi" style="margin:0px;padding:0px">'
        if snd:
                print '<input type="hidden" name="snd" value="'+snd+'">'
        else:
                if src:
                        print '<input type="hidden" name="src" value="'+src+'">'
                if dst:
                        print '<input type="hidden" name="dst" value="'+dst+'">'
        if tcpsrc:
                print '<input type="hidden" name="tcpsrc" value="'+tcpsrc+'">'
        if tcpdst:
                print '<input type="hidden" name="tcpdst" value="'+tcpdst+'">'
        if udpsrc:
                print '<input type="hidden" name="udpsrc" value="'+udpsrc+'">'
        if udpdst:
                print '<input type="hidden" name="udpdst" value="'+udpdst+'">'
        if snsr:
                print '<input type="hidden" name="snsr" value="'+snsr+'">'
        if cls:
                print '<input type="hidden" name="cls" value="'+cls+'">'
	if sig:
		print '<input type="hidden" name="sig" value="'+sig+'">'
        if sigx:
                print '<input type="hidden" name="sigx" value="'+sigx+'">'
        if lim:
                print '<input type="hidden" name="lim" value="'+str(lim)+'">'
        if mode:
                print '<input type="hidden" name="m" value="'+mode+'">'
	if sa > 0:
		# Pos num, back <--
		adj_a = end
		adj_o = str(int(end) + sa)
		if adj_a == adj_o:
			adj_o = str(int(adj_o) + 1)
	if sa < 0:
		# Neg num, fwd -->
		adj_a = str(int(start) + sa)
		adj_o = start
		if adj_a == adj_o:
			adj_o = str(int(adj_o) + 1)
	if sa == 0:
		adj_a = '0' 
		adj_o = str(start)
		if adj_a == adj_o:
			adj_o = str(int(adj_o) + 1)
	print '<input type="hidden" name="a" value="'+adj_a+'">'
	print '<input type="hidden" name="o" value="'+adj_o+'">'	
        print '<input type="submit" value="'+sn+'" style="font-size:11px;width:44px;height:22px">'
        print '</form></td>'


## Print Time Sliding Buttons
print '<table><tr>'
slide(1440,"-24h")
slide(360,"-6h")
slide(60,"-1h")
slide(15,"-15m")
print '<td style="height:12px;align:left;font-size:10px">&nbsp;&bull;&nbsp;</td>'
## Print Foward buttons if gap is more than required
if int(start) != 0:
	if int(end) > 15:
		slide(-15,"+15m")
	if int(end) > 60:
		slide(-60,"+1h")	
	if int(end) > 360:
		slide(-360,"+6h")	
	if int(end) > 1440:
		slide(-1440,"+24h")
slide(0,"Now")
print '</tr></table>'



##### Unpack unique event,src,dst sets and sort
if mode:
	# Unique Events
	ue = []
	for line in ueve:
		ue.append(line)
	ue.sort()
	# Unique Sources
	us = []
	for line in usrc:
		us.append(line)
	us.sort()
	# Unique Destinations
	ud = []
	for line in udst:
		ud.append(line)
	ud.sort()


##### Mode branches

## Event to Src/Dst mode
if mode == 'es' or mode == 'ed':
	print '<ul class="mktree" id="root">'
	if mode == 'es':
		print 'Unique Events by Source IP'
	if mode == 'ed':
		print 'Unique Events by Destination IP'
	# Generated unique class list and sort
	esd_cls = set()
	esd_ucls = []
	for line in store:
		esd_cls.add(line[0][6])
	for item in esd_cls:
		esd_ucls.append(item)
	esd_ucls.sort()
	# For each class, print events and sources
	for utyp in esd_ucls:
		# Count events and sigs	
		ecnt = 0
		sdcnt = 0
		icnt = 0
		cnt_sig = set()
		cnt_sdip = set()	
		for line in store:
			if line[0][6] == utyp:
				ecnt += 1
				cnt_sig.add(line[0][3])
				if mode == 'es':
					cnt_sdip.add(line[0][7])
				if mode == 'ed':
					cnt_sdip.add(line[0][8])
		sdcnt = len(cnt_sig)	
		icnt = len(cnt_sdip)
		# Threshholds for bolding
		thec = ecnt / 5 
		if thec <= 10:
			thec = 10 
		thic = icnt / 5 
		if thic <= 10:
			thic = 10 
		# Event level Tallys
		print '<li class="liOpen">'+utyp+' ( '+str(sdcnt)+' sigs, '+str(icnt)
		if mode == 'es':
			print ' src, '
		if mode == 'ed':
			print ' dst, '
		print str(ecnt)+' events )'
		print '<ul>'
		for uniq in ue:
			esd_src = set()	
			esd_usrc = []	
			esd_sid = uniq.split('~')[1]
			esd_sig = uniq.split('~')[0]
			# Parse store for sig.sid_id and add src ip's to uniq set 
			for line in store:
				if line[0][3] == esd_sid and line[0][6] == utyp:
					if mode == 'es':
						esd_src.add(line[0][7])
					if mode == 'ed':
						esd_src.add(line[0][8])
			# unpack uniq set to a list & sort
			for item in esd_src:
				esd_usrc.append(item)
			esd_usrc.sort()
			if len(esd_src) > 0:
				cnt = 0
				for line in store:
					if line[0][4] == esd_sig:
						cnt += 1
				# Bold Event counts above thresholds
				print '<li>'+esd_sig+' ( '
				if len(esd_usrc) >= thic and len(esd_usrc) <> icnt:
					print '<font color="red">'
				print str(len(esd_usrc))
				if len(esd_usrc) >= thic and len(esd_usrc) <> icnt:
					print '</font>'
				if mode == 'es':
					print ' src,'
				if mode == 'ed':
					print ' dst,'
				if cnt >= thec and cnt <> ecnt:
					print '<font color="red">'
				print str(cnt)
				if cnt >= thec and cnt <> ecnt:
					print '</font>'
				print ' events )'
                        	print '<ul>'
				for item in esd_src: 
					out = []
					clr = 3
					for line in store:
						if line[0][3] == esd_sid and (line[0][7] == item or line[0][8] == item):
							if clr == 3:
								outstr = '<tr bgcolor="EEEECC">'
								clr = 1
							else:
								outstr = '<tr>'
								clr += 1
							# Print Sensor 
							outstr += '<td>'+sensors[line[0][0]]+'</td>'
							# Print Date/Time
							outstr += '<td>'+line[0][2]
							# Print Event
							outstr += '<td><a href="./pygeve.cgi?s='+line[0][0]+'&c='+line[0][1]+'" onClick="return popup(this,\'data\')" target="data">'+line[0][4]+'</a></td>'
							# Print Srcip with ip,flip links
							outstr += '<td><a href="./pygqry.cgi?src='+numtoip(int(line[0][7]))+'&dst='+numtoip(int(line[0][7]))+'&a='+start+'&o='+end+'&m=ed">'+numtoip(int(line[0][7]))+'</a></td>'
							outstr += '<td><a href="./pygqry.cgi?src='+numtoip(int(line[0][8]))+'&dst='+numtoip(int(line[0][8]))+'&a='+start+'&o='+end+'&m=es">'+numtoip(int(line[0][8]))+'</a></td>'
							if tcpsrc or tcpdst or udpsrc or udpdst:	
						        	outstr += '<td>'+line[0][10]+'</font></td><td>'+line[0][11]+'</font></td>'
							outstr += '</tr>'
							out.append(outstr)
					print '<li>'+numtoip(int(item))+' <font size="1">x'+str(len(out))+'</font>'
					print '<ul>'
					print '<table frame="void" border="1" cellspacing="4" cellpadding="3" width="1100">'
					print '<tr bgcolor="CCCCEE"><td>Sensor</td><td>Time</td><td>Event</td><td>Src IP</td><td>Dst IP</td>'
					if tcpsrc or tcpdst: 
						print '<td>TCP|Src</font></td><td>TCP|Dst</font></td>'
					if udpsrc or udpdst: 
						print '<td>UDP|Src</font></td><td>UDP|Dst</font></td>'
					print '</tr>'
					for line in out:
						print line
					print '</table>'
					print '</ul>'
					print '</li>'
				print '</ul>'
				print '</li>'	
		print '</ul>'
		print '</li>'
	print '</ul>'


## Src/Dst to Dst/Src mode	
elif mode == 'sd' or mode == 'ds':
	print '<ul class="mktree" id="root">'
	if mode == 'sd':
		print 'Unique Sources to Destinations' 
		usd = us
	if mode == 'ds':
		print 'Unique Destinations to Sources'
		usd = ud	
        for uniq in usd:
		sdo = set()
		usdo = []
		# Parse store for uniq dst for this src
		for line in store:
			if mode == 'sd':	
				if line[0][7] == uniq:
					sdo.add(line[0][8])
			if mode == 'ds':
				if line[0][8] == uniq:
					sdo.add(line[0][7])	
		for item in sdo:
			usdo.append(item)
		usdo.sort()
		# Seems like extra code but did no want to check mode for every line in store..
		cnt = 0	
		if mode == 'sd':
			for line in store:
				if line[0][7] == uniq:
					cnt += 1 
		if mode == 'ds':
			for line in store:
				if line[0][8] == uniq:
					cnt += 1	
		# Print counts (,,)
		thic = cnt / 5
		if thic <= 10:
			thic = 10
		print '<li>'+numtoip(int(uniq))+' ( '+str(len(usdo))
		if mode == 'sd':
			print ' dst, '
		if mode == 'ds':
			print ' src, '	
		print str(cnt)+' events )'
		#
		print '<ul>'
		for item in usdo:
			out = []
			clr = 3
			for line in store:
				# The big one, diff conditions for both modes
				if (mode == 'sd' and (line[0][7] == uniq and line[0][8] == item)) or (mode =='ds' and (line[0][8] == uniq and line[0][7] == item)):
					if clr == 3:
						outstr = '<tr bgcolor="EEEECC">'
						clr = 1
					else:
						outstr = '<tr>'
						clr += 1
                                        outstr += '<td>'+sensors[line[0][0]]+'</td>'
                                        outstr += '<td>'+line[0][2]
                                        outstr += '<td><a href="./pygeve.cgi?s='+line[0][0]+'&c='+line[0][1]+'" onClick="return popup(this,\'data\')" target="data">'+line[0][4]+'</a></td>'
                                        outstr += '<td><a href="./pygqry.cgi?src='+numtoip(int(line[0][7]))+'&dst='+numtoip(int(line[0][7]))+'&a='+start+'&o='+end+'&m=ed">'+numtoip(int(line[0][7]))+'</a></td>'
                                        outstr += '<td><a href="./pygqry.cgi?src='+numtoip(int(line[0][8]))+'&dst='+numtoip(int(line[0][8]))+'&a='+start+'&o='+end+'&m=es">'+numtoip(int(line[0][8]))+'</a></td>'
					if tcpsrc or tcpdst or udpsrc or udpdst:
						outstr += '<td>'+line[0][10]+'</font></td><td>'+line[0][11]+'</font></td>'
                                        outstr += '</tr>'
					out.append(outstr)
                        print '<li>'+numtoip(int(item))+' <font size="1"'
			if len(out) >= thic and len(out) <> cnt:
				print ' color="red"'
			print '> x' 
			print str(len(out))
			print '</font>'
                        print '<ul>'
                        print '<table frame="void" border="1" cellspacing="4" cellpadding="3" width="1100">'
                        print '<tr bgcolor="CCCCEE"><td>Sensor</td><td>Time</td><td>Event</td><td>Src IP</td><td>Dst IP</td>'
			if tcpsrc or tcpdst:
				print '<td>TCP|Src</font></td><td>TCP|Dst</font></td>'
			if udpsrc or udpdst:
				print '<td>UDP|Src</font></td><td>UDP|Dst</font></td>'
			print '</tr>'
			for line in out:
				print line	
                        print '</table>'
                        print '</ul>'
                        print '</li>'
                print '</ul>'
                print '</li>'
	print '</ul>'


## Src/Dst to Event mode
elif mode == 'se' or mode == 'de':
	print '<ul class="mktree" id="root">'
	if mode == 'se':
		print 'Unique Sources to Events'
		usd = us
	if mode == 'de':
		print 'Unique Destinations to Events'
		usd = ud
	for uniq in usd:
		sde = set()
		usde = []
		# Parse store for uniq events per src
		cnt = 0
		for line in store:
			if mode == 'se':
				if line[0][7] == uniq:
					sde.add(line[0][4])
					cnt += 1
			if mode == 'de':
				if line[0][8] == uniq:
					sde.add(line[0][4])
					cnt += 1	
		thic = cnt / 5 
		if thic <= 10:
			thic = 10	
		for item in sde:
			usde.append(item)
		usde.sort()
		print '<li>'+numtoip(int(uniq))+' ( '+str(len(usde))+' sigs, '+str(cnt)+' events )' 
		print '<ul>'
		for item in usde:
			out = []
			clr = 3
			for line in store:
				if (mode == 'se' and (line[0][7] == uniq and line[0][4] == item)) or (mode == 'de' and (line[0][8] == uniq and line[0][4] == item)):
					if clr == 3:
						outstr = '<tr bgcolor="EEEECC">'
                                                clr = 1
                                        else:
                                                outstr = '<tr>'
                                                clr += 1
					outstr += '<td>'+sensors[line[0][0]]+'</td>'
					outstr += '<td>'+line[0][2]+'</td>'
					outstr += '<td><a href="./pygeve.cgi?s='+line[0][0]+'&c='+line[0][1]+'" onClick="return popup(this,\'data\')" target="data">'+line[0][4]+'</a></td>'
                                        outstr += '<td><a href="./pygqry.cgi?src='+numtoip(int(line[0][7]))+'&dst='+numtoip(int(line[0][7]))+'&a='+start+'&o='+end+'&m=ed">'+numtoip(int(line[0][7]))+'</a></td>'
                                        outstr += '<td><a href="./pygqry.cgi?src='+numtoip(int(line[0][8]))+'&dst='+numtoip(int(line[0][8]))+'&a='+start+'&o='+end+'&m=es">'+numtoip(int(line[0][8]))+'</a></td>'
					if tcpsrc or tcpdst or udpsrc or udpdst:
						outstr += '<td>'+line[0][10]+'</font></td><td>'+line[0][11]+'</font></td>'
                                        outstr += '</tr>'
					out.append(outstr)
                        print '<li>'+item+' <font size="1" '
			if len(out) >= thic and len(out) <> cnt:
				print 'font color="red"'
			print '> x'+str(len(out))+'</font>'
                        print '<ul>'
                        print '<table frame="void" border="1" cellspacing="4" cellpadding="3" width="1100">'
                        print '<tr bgcolor="CCCCEE"><td>Sensor</td><td>Time</td><td>Event</td><td>Src IP</td><td>Dst IP</td>'
			if tcpsrc or tcpdst:
				print '<td>TCP|Src</font></td><td>TCP|Dst</font></td>'
			if udpsrc or udpdst:
				print '<td>UDP|Src</font></td><td>UDP|Dst</font></td>'
			print '</tr>'
			for line in out:
				print line
			print '</table>'
			print '</ul>'
			print '</li>'
		print '</ul>'
		print '</li>'
	print '</ul>'


## Flat list default
else:
	flt_src = set()
	flt_dst = set()
	flt_eve = set()
	cnt = 0
	for line in store:
		flt_src.add(line[0][7])
		flt_dst.add(line[0][8])
		flt_eve.add(line[0][3])
		cnt += 1
	print '<table border="1" width="1300" frame="void" cellspacing="4" cellpadding="3" width="1100">'
	print '<tr bgcolor = "CCCCEE">'
	print '<td>Sensor</font></td><td>Time</font></td><td>Event x '+str(cnt)+' ('+ str(len(flt_eve))+' uniq)</font></td><td>Src IP x '+str(len(flt_src))+'</font></td><td>Dst IP x '+str(len(flt_dst))+'</font></td>'
	if tcpsrc or tcpdst:
		print '<td>TCP|Src</font></td><td>TCP|Dst</font></td>'
	if udpsrc or udpdst:
		print '<td>UDP|Src</font></td><td>UDP|Dst</font></td>'
	print '</tr>' 
	clr = 3 
	for line in store:
		if clr == 3:
			print '<tr bgcolor="EEEECC">'
			clr = 1
		else:
			print '<tr>'
			clr += 1
		print '<td width="100">'+sensors[line[0][0]]+'</td>',
		print '<td width="140">'+line[0][2]+'</td>',
		print '<td><a href="./pygeve.cgi?s='+line[0][0]+'&c='+line[0][1]+'" onClick="return popup(this,\'data\')" target="data">'+line[0][4]+'</a></td>',
		print '<td><a href="./pygqry.cgi?src='+numtoip(int(line[0][7]))+'&dst='+numtoip(int(line[0][7]))+'&a='+start+'&o='+end+'&m=ed">'+numtoip(int(line[0][7]))+'</a></td>'
		print '<td><a href="./pygqry.cgi?src='+numtoip(int(line[0][8]))+'&dst='+numtoip(int(line[0][8]))+'&a='+start+'&o='+end+'&m=es">'+numtoip(int(line[0][8]))+'</a></td>'
		if tcpsrc or tcpdst or udpsrc or udpdst:
			print '<td>'+line[0][10]+'</font></td><td>'+line[0][11]+'</font></td></td>'
		print '</tr>'
	print '</table>'
print '<br>'


renderend = time.time()

print '<br><br><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<font size="1">Query: '+str(round(qryend - cgistart,3))+'s - Render: '+str(round(renderend - cgistart,3))+'s</font>'
print '</html>'
