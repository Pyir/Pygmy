#!/usr/bin/python

pyver = '0.35.4.17'

import os,re,_mysql,datetime,time

# Current time, previous midnight and minutes from midnight
now = datetime.datetime.now()
zero = datetime.datetime(now.year,now.month,now.day,0,0,0)
frmid = now - zero
frmid = str(frmid.seconds /60)

# Time me
cgistart = time.time()


#######################################
def stderr(err):
	print 'Content-Type: text/html'
	print ''
	print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">'
	print '<html>'
	print 'Error: '+err+'<br>'
	exit()

def sts(s):
        out = ''
        st=s.split('-')
        for part in st:
                 out += part+'\n'
        return out

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


##########################################################
conf=open('/etc/pyg.conf','r')
re_com = re.compile('^#')
conf_db=''
conf_host=''
conf_user=''
conf_passwd=''
for line in conf:
	if not re_com.search(line):
        	if line.find('db=') == 0 and line:
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

##########################################################

### Grab sid+sensors.if
qrystr = 'select sid,hostname,interface from sensor order by sid'
db.query(qrystr)
dbqry=db.store_result()
snsrs = dict() 
rc = 0
while rc != dbqry.num_rows():
        line = dbqry.fetch_row()[0]
        try:
                qr=line[1]+'.'+line[2]
                snsrs[line[0]]=qr
                rc += 1
        except Exception:
                rc += 1
si = []
for i in snsrs:
	si.append(int(i))
si.sort()

### Grab class list
qrystr = 'select sig_class_id,sig_class_name from sig_class order by sig_class_id'
db.query(qrystr)
dbqry=db.store_result()
clss = dict() 
rc = 0
while rc != dbqry.num_rows():
        line = dbqry.fetch_row()[0]
        try:
                clss[str(line[0])]=line[1]
                rc += 1
        except Exception:
                rc += 1
ci = []
for i in clss:
	ci.append(int(i))
ci.sort()
	 
##########################################################
print 'Content-Type: text/html'
print ''
print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">'
print '<html>'
print '<head>'
print '<title>Pygmy Snort Console </title>'
print '<script src="../pygmy/popup.js" type="text/javascript" ></script>'
print '</head>'
print '<body>'
print '<font face="calibri">'

########################### Rally up the queries and store them away ##############################################
##################### Top x events
qrystr = 'select distinct sig_name, count(cid) from event join signature on signature = sig_id where timestamp >= Date_Sub(NOW(), Interval '+frmid+' minute)group by signature order by count(cid) DESC limit 10'
db.query(qrystr)
dbqry=db.store_result()
topeve = []
rc = 0
while rc != dbqry.num_rows():
        line = dbqry.fetch_row()
        try:
                topeve.append(line[0][0]+'~'+line[0][1])
                rc += 1
        except Exception:
                rc += 1

###################### Last x events
re_strpdt=re.compile('20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]')
qrystr = 'select sensor.hostname,event.timestamp,signature.sig_name,iphdr.ip_src,iphdr.ip_dst,event.sid,event.cid from event left join (sensor,iphdr,signature) on (event.sid = sensor.sid and event.sid = iphdr.sid and event.cid = iphdr.cid and event.signature = signature.sig_id) where event.timestamp >= Date_Sub(NOW(), Interval 15 minute) order by event.timestamp desc limit 10'
db.query(qrystr)
dbqry=db.store_result()
if str(dbqry.num_rows()) == '0':
	qrystr = 'select sensor.hostname,event.timestamp,signature.sig_name,iphdr.ip_src,iphdr.ip_dst,event.sid,event.cid from event left join (sensor,iphdr,signature) on (event.sid = sensor.sid and event.sid = iphdr.sid and event.cid = iphdr.cid and event.signature = signature.sig_id) where event.timestamp >= Date_Sub(NOW(), Interval 3 Hour) order by event.timestamp desc limit 10'
	db.query(qrystr)
	dbqry=db.store_result()
if str(dbqry.num_rows()) == '0':
        qrystr = 'select sensor.hostname,event.timestamp,signature.sig_name,iphdr.ip_src,iphdr.ip_dst,event.sid,event.cid from event left join (sensor,iphdr,signature) on (event.sid = sensor.sid and event.sid = iphdr.sid and event.cid = iphdr.cid and event.signature = signature.sig_id) where event.timestamp >= Date_Sub(NOW(), Interval 12 Hour) order by event.timestamp desc limit 10'
        db.query(qrystr)
        dbqry=db.store_result()

lasteve = []
rc = 0
while rc != dbqry.num_rows():
        line = dbqry.fetch_row()
        try:
                lasteve.append(line[0][0]+'~'+re_strpdt.sub('',line[0][1])+'~'+line[0][2]+'~'+line[0][3]+'~'+line[0][4]+'~'+line[0][5]+'~'+line[0][6])
                rc += 1
        except Exception:
                rc += 1

######################### Src IP Count
qrystr = 'select iphdr.ip_src,count(event.cid) from event join iphdr on (event.sid = iphdr.sid and event.cid = iphdr.cid) where timestamp >= Date_Sub(NOW(),INTERVAL 6 HOUR) group by iphdr.ip_src order by count(event.cid) desc limit 10'
db.query(qrystr)
dbqry=db.store_result()
topsrc = []
rc = 0
while rc != dbqry.num_rows():
        line = dbqry.fetch_row()
        try:
                topsrc.append(line[0][0]+'~'+line[0][1])
                rc += 1
        except Exception:
                rc += 1

######################## Dst IP Count
qrystr = 'select iphdr.ip_dst,count(event.cid) from event join iphdr on (event.sid = iphdr.sid and event.cid = iphdr.cid) where timestamp >= Date_Sub(NOW(),INTERVAL 6 HOUR) group by iphdr.ip_dst order by count(event.cid) desc limit 10'
db.query(qrystr)
dbqry=db.store_result()
topdst = []
rc = 0
while rc != dbqry.num_rows():
        line = dbqry.fetch_row()
        try:
                topdst.append(line[0][0]+'~'+line[0][1])
                rc += 1
        except Exception:
                rc += 1

####################### TCP sport
qrystr = 'select tcphdr.tcp_sport,count(event.cid) from event join tcphdr on (event.sid = tcphdr.sid and event.cid = tcphdr.cid) where timestamp >= Date_Sub(NOW(),INTERVAL 6 HOUR) group by tcphdr.tcp_sport order by count(event.cid) desc limit 10'
db.query(qrystr)
dbqry=db.store_result()
tcpsp = []
rc = 0
while rc != dbqry.num_rows():
        line = dbqry.fetch_row()
        try:
                tcpsp.append(line[0][0]+'~'+line[0][1])
                rc += 1
        except Exception:
                rc += 1

###################### TCP dp
qrystr = 'select tcphdr.tcp_dport,count(event.cid) from event join tcphdr on (event.sid = tcphdr.sid and event.cid = tcphdr.cid) where timestamp >= Date_Sub(NOW(),INTERVAL 6 HOUR) group by tcphdr.tcp_dport order by count(event.cid) desc limit 10'
db.query(qrystr)
dbqry=db.store_result()
tcpdp = []
rc = 0
while rc != dbqry.num_rows():
        line = dbqry.fetch_row()
        try:
                tcpdp.append(line[0][0]+'~'+line[0][1])
                rc += 1
        except Exception:
                rc += 1

####################### UDP sp
qrystr = 'select udphdr.udp_sport,count(event.cid) from event join udphdr on (event.sid = udphdr.sid and event.cid = udphdr.cid) where timestamp >= Date_Sub(NOW(),INTERVAL 6 HOUR) group by udphdr.udp_sport order by count(event.cid) desc limit 10'
db.query(qrystr)
dbqry=db.store_result()
udpsp = []
rc = 0
while rc != dbqry.num_rows():
        line = dbqry.fetch_row()
        try:
                udpsp.append(line[0][0]+'~'+line[0][1])
                rc += 1
        except Exception:
                rc += 1

###################### UDP dp
qrystr = 'select udphdr.udp_dport,count(event.cid) from event join udphdr on (event.sid = udphdr.sid and event.cid = udphdr.cid) where timestamp >= Date_Sub(NOW(),INTERVAL 6 HOUR) group by udphdr.udp_dport order by count(event.cid) desc limit 10'
db.query(qrystr)
dbqry=db.store_result()
udpdp = []
rc = 0
while rc != dbqry.num_rows():
        line = dbqry.fetch_row()
        try:
                udpdp.append(line[0][0]+'~'+line[0][1])
                rc += 1
        except Exception:
                rc += 1

######################### Src to uniq dst
qrystr = 'select iphdr.ip_src, count(distinct iphdr.ip_dst) from event join iphdr on (event.cid = iphdr.cid and event.sid = iphdr.sid) where event.timestamp >= Date_Sub(NOW(), Interval 6 Hour) group by iphdr.ip_src order by count(distinct iphdr.ip_dst) desc limit 10'
db.query(qrystr)
dbqry=db.store_result()
srcxd = []
rc = 0
while rc != dbqry.num_rows():
	line = dbqry.fetch_row()
	try:
		srcxd.append(line[0][0]+'~'+line[0][1])
		rc += 1
	except Exception:
		rc += 1

###################### Dst to uniq Src
qrystr = 'select iphdr.ip_dst, count(distinct iphdr.ip_src) from event join iphdr on (event.cid = iphdr.cid and event.sid = iphdr.sid) where event.timestamp >= Date_Sub(NOW(), Interval 6 Hour) group by iphdr.ip_dst order by count(distinct iphdr.ip_src) desc limit 10'
db.query(qrystr)
dbqry=db.store_result()
dstxs = []
rc = 0
while rc != dbqry.num_rows():
	line = dbqry.fetch_row()
	try:
		dstxs.append(line[0][0]+'~'+line[0][1])
		rc += 1
	except Exception:
		rc += 1

###################### Src to uniq events
qrystr = 'select iphdr.ip_src, count(distinct event.signature) from event join iphdr on (event.sid = iphdr.sid and event.cid = iphdr.cid) where event.timestamp >= Date_Sub(NOW(), Interval 6 Hour) group by ip_src order by count(distinct event.signature) desc limit 10'
db.query(qrystr)
dbqry=db.store_result()
srcex = []
rc = 0
while rc != dbqry.num_rows():
        line = dbqry.fetch_row()
        try:
                srcex.append(line[0][0]+'~'+line[0][1])
                rc += 1
        except Exception:
                rc += 1

###################### Dst to uniq events
qrystr = 'select iphdr.ip_dst, count(distinct event.signature) from event join iphdr on (event.sid = iphdr.sid and event.cid = iphdr.cid) where event.timestamp >= Date_Sub(NOW(), Interval 6 Hour) group by ip_dst order by count(distinct event.signature) desc limit 10'
db.query(qrystr)
dbqry=db.store_result()
dstex = []
rc = 0
while rc != dbqry.num_rows():
        line = dbqry.fetch_row()
        try:
                dstex.append(line[0][0]+'~'+line[0][1])
                rc += 1
        except Exception:
                rc += 1

##################### Newest Sigs
qrystr ='select sig_id,sig_name from signature order by sig_id desc limit 10'
db.query(qrystr)
dbqry=db.store_result()
rcntsig = dict()
rc = 0
while rc != dbqry.num_rows():
        line = dbqry.fetch_row()
        try:
                rcntsig[str(line[0][0])]=line[0][1]
                rc += 1
        except Exception:
                rc += 1
# Set up dicts of start/end times for query links
rcntstart = dict()
rcntend = dict()
for sigid in rcntsig:
	qrystr = "select timestamp from event where signature="+sigid+" order by timestamp limit 1"
	db.query(qrystr)
	dbqry = db.store_result()
	try:
		line = dbqry.fetch_row()
		rcntstart[str(sigid)] = str(line[0][0]) 
	except Exception:
		rcntstart[str(sigid)] = 'None' 
for sigid in rcntsig:
	qrystr = "select timestamp from event where signature="+sigid+" order by timestamp desc limit 1"
	db.query(qrystr)
	dbqry = db.store_result()
	try:
		line = dbqry.fetch_row()
		rcntend[str(sigid)] = str(line[0][0])
	except Exception:
		rcntend[str(sigid)] = 'None'

#################### Snsr / Type grid
data = dict()
qrystr = 'select sid,hostname,interface from sensor'
db.query(qrystr)
dbqry = db.store_result()
snsrs = dict() 
rc = 0
while rc != dbqry.num_rows():
        line = dbqry.fetch_row()
        try:
		qr = line[0][1]+':'+line[0][2] 
                snsrs[str(line[0][0])] = qr
                rc += 1
        except Exception:
                rc += 1

## Build placeholders for data grid
for snsr in snsrs:
	data[snsr]=dict()

qrystr = 'select sig_class_name from sig_class'
db.query(qrystr)
dbqry=db.store_result()
clss = []
rc = 0
while rc != dbqry.num_rows():
        line = dbqry.fetch_row()
        try:
                clss.append(line[0][0])
                rc += 1
        except Exception:
                rc += 1


# Get event counts per class/sensor for grid
for cls in clss:
	qrystr = "select distinct sensor.sid,count(event.cid) from sensor join (event,signature,sig_class) on (sensor.sid = event.sid and event.signature = signature.sig_id and signature.sig_class_id = sig_class.sig_class_id)"
	qrystr += " where event.timestamp >= Date_Sub(NOW(), Interval "+frmid+" minute) and sig_class.sig_class_name = '"+cls+"' group by sensor.hostname"
	db.query(qrystr)
	dbqry=db.store_result()
	rc = 0
	while rc != dbqry.num_rows():
		line = dbqry.fetch_row()
		try:
			tup = [(cls,line[0][1])]
			data[line[0][0]].update(tup)
			rc += 1
		except Exception:
			rc += 1

############### Start printing the grids and Tops #######################################
print '<table width="1412" frame="box" rules="all">'
print '<tr><td><a href="./pygqry.cgi?m=es&a=0&o=60"><img src="../pygmy/pyg.jpg"></a></td>'
print '<td><font size="1"><center>Last Event</td>'
for cls in clss:
	print '<td align="center"><font size="1"><a href="./pygqry.cgi?a=0&o='+frmid+'&m=es&clsx='+cls+'">'+sts(cls)+'</td>'
print '</tr>'	
for snsr in snsrs:
	print '<tr><td><font size="1">&nbsp;<a href="./pygqry.cgi?a=0&o='+frmid+'&m=es&snsr='+snsr+'">'+snsrs[snsr]+'&nbsp;</a>'
	qrystr = "select event.timestamp from event join sensor on (event.sid = sensor.sid) where event.timestamp >= Date_Sub(Now(), Interval 12 Hour) and sensor.sid = '"+snsr+"' order by event.timestamp desc limit 1"	
	db.query(qrystr)
	dbqry=db.store_result()
	line = dbqry.fetch_row()
	if dbqry.num_rows() == 0:
		line = '+12hr'
	else:
		line = str(line[0][0]).split(' ')[1]
	print '<td><font size="1">&nbsp;'+line+'&nbsp;</td>'
	for cls in clss:
		print '<td align="right"><font size="2">'
		try:
			print '<a href="./pygqry.cgi?a=0&o='+frmid+'&m=es&snsr='+snsr+'&clsx='+cls+'">'+data[snsr][cls]+'</a>&nbsp;&nbsp;'
		except Exception:
			print '&nbsp;'
		print '</td>'
	print '</td></tr>'
print '</table>'
print '</td></tr></table>'
print '<table width="1412" cellspacing="0" cellpadding="0">'
print '<tr><td>'
print '<table width="560" height="270" frame="box">'
print '<tr><td><font size="2"><b>Top event counts</td></tr>'
lc = 0
for line in topeve:
	lc += 1
	sgxo = ''
	sgx = line.split('~')[0]
	for chr in sgx:
		if chr == '+':
			sgxo += '%2B'
		else:
			sgxo += chr
	print '<tr><td><font size="2">&nbsp;<a href="./pygqry.cgi?a=0&o='+frmid+'&m=es&sigx='+sgxo+'">'+line.split('~')[0][:75]+'</a></td><td><font size="2">'+line.split('~')[1]+'</td></tr>'
fill = 10 - lc
for n in range(1,fill):
	print '<tr><td><font size="2">&nbsp;</td><td><font size="2">&nbsp;</td></tr>' 
print '</table>'
print '</td>'
print '<td>'
print '<table width="852" height="270" frame="box">'
print '<tr><td><font size="2"><b>Recent Events</td></tr>'
lc = 0
for line in lasteve:
	lc += 1
	outstr = '<tr><td><font size="2">&nbsp;'
	outstr += line.split('~')[0]
	outstr += '</td><td><font size="2">'
	outstr += line.split('~')[1]
        outstr += '</td><td><font size="2">'
	outstr += '<a href="./pygeve.cgi?s='+line.split('~')[5]+'&c='+line.split('~')[6]+'" onClick="return popup(this,\'data\')" target="data">'+line.split('~')[2][:75]+'</a>'
        outstr += '</td><td align="right"><font size="2">'
	outstr += '<a href="./pygqry.cgi?a=0&o='+frmid+'&src='+numtoip(int(line.split('~')[3]))+'&dst='+numtoip(int(line.split('~')[3]))+'">'+numtoip(int(line.split('~')[3]))+'</a>'
        outstr += '</td><td align="left"><font size="2">&rarr;'
	outstr += '<a href="./pygqry.cgi?a=0&o='+frmid+'&src='+numtoip(int(line.split('~')[4]))+'&dst='+numtoip(int(line.split('~')[4]))+'">'+numtoip(int(line.split('~')[4]))+'</a>'
        outstr += '</td></tr>'
	print outstr
fill = 10 - lc
for n in range(1,fill):
        print '<tr><td><font size="2">&nbsp;</td><td><font size="2">&nbsp;-&nbsp;</td></tr>'
print '</table>'
print '</td>'
print '</tr>'
print '</table>'
print '<table width="1412" cellpadding="0" cellspacing="0">'
print '<tr><td>'	
print '<table width="225" height="270" frame="box">'
print '<tr><td><font size="2"><b>Src /w most Dst</td><td></td></tr>'
lc = 0
for line in srcxd:
	lc += 1
        print '<tr><td><font size="2">'
        print '&nbsp;<a href="./pygqry.cgi?a=0&o='+frmid+'&m=ed&src='+numtoip(int(line.split('~')[0]))+'">'+numtoip(int(line.split('~')[0]))+'</a>'
        print '</td><td><font size="2">'
        print line.split('~')[1]
        print '</td></tr>'
fill = 10 - lc
for n in range(1,fill):
        print '<tr><td><font size="2">&nbsp;</td><td><font size="2">&nbsp;</td></tr>'
print '</table>'
print '</td><td>'
print '<table width="225" height="270" frame="box">'
print '<tr><td><font size="2"><b>Dst /w most Src</td><td></td></tr>'
lc = 0
for line in dstxs:
	lc += 1
        print '<tr><td><font size="2">'
        print '&nbsp;<a href="./pygqry.cgi?a=0&o='+frmid+'&m=es&dst='+numtoip(int(line.split('~')[0]))+'">'+numtoip(int(line.split('~')[0]))+'</a>'
        print '</td><td><font size="2">'
        print line.split('~')[1]
        print '</td></tr>'
fill = 10 - lc
for n in range(1,fill):
        print '<tr><td><font size="2">&nbsp;</td><td><font size="2">&nbsp;</td></tr>'
print '</table>'
print '</td><td>'
print '<table width="225" height="270" frame="box">'
print '<tr><td><font size="2"><b>Src /w most Events</td><td></td></tr>'
lc = 0
for line in srcex:
	lc += 1
        print '<tr><td><font size="2">'
        print '&nbsp;<a href="./pygqry.cgi?a=0&o='+frmid+'&m=se&src='+numtoip(int(line.split('~')[0]))+'">'+numtoip(int(line.split('~')[0]))+'</a>'
        print '</td><td><font size="2">'
        print line.split('~')[1]
        print '</td></tr>'
fill = 10 - lc
for n in range(1,fill):
        print '<tr><td><font size="2">&nbsp;</td><td><font size="2">&nbsp;</td></tr>'
print '</table>'
print '</td><td>'
print '<table width="225" height="270" frame="box">'
print '<tr><td><font size="2"><b>Dst /w most Events</td><td></td></tr>'
lc = 0
for line in dstex:
	lc += 1
        print '<tr><td><font size="2">'
        print '&nbsp;<a href="./pygqry.cgi?a=0&o='+frmid+'&m=de&dst='+numtoip(int(line.split('~')[0]))+'">'+numtoip(int(line.split('~')[0]))+'</a>'
        print '</td><td><font size="2">'
        print line.split('~')[1]
        print '</td></tr>'
fill = 10 - lc
for n in range(1,fill):
        print '<tr><td><font size="2">&nbsp;</td><td><font size="2">&nbsp;</td></tr>'
print '</table>'
print '</td><td>'
print '<table width="512" height="270" frame="box">'
print '<tr><td><font size="2"><b>Newest Sigs</td><td></td></tr>'
lc = 0 
for sgid in sorted(rcntsig, reverse=True):
	lc += 1
	rcnt_a=rcntend[sgid]
	if rcnt_a <> 'None':
		rcnt_a=rcnt_a.split(' ')[0].split('-')+rcnt_a.split(' ')[1].split(':')
	else:
		rcnt_a=[str(now.year),str(now.month),str(now.day),str(now.hour),str(now.minute),str(now.second)]
	rcnt_o=rcntstart[sgid]
	if rcnt_o <> 'None':
		rcnt_o=rcnt_o.split(' ')[0].split('-')+rcnt_o.split(' ')[1].split(':')	
	else:
		rcnt_o=[str(now.year),str(now.month),str(now.day),str(now.hour),str(now.minute),str(now.second)]
	print '<tr><td><font size="2">'
	print '&nbsp;<a href="./pygqry.cgi?m=es&sig='+sgid
	print '&a_yr='+rcnt_a[0]+'&a_mo='+rcnt_a[1]+'&a_dy='+rcnt_a[2]+'&a_hr='+rcnt_a[3]+'&a_mn='+str(int(rcnt_a[4])+1)
	print '&o_yr='+rcnt_o[0]+'&o_mo='+rcnt_o[1]+'&o_dy='+rcnt_o[2]+'&o_hr='+rcnt_o[3]+'&o_mn='+str(int(rcnt_o[4])-1)
	print '">'+rcntsig[sgid][:70]+'</a>'
	print '<td><font size="2">'
	print rcnt_a[1].lstrip('0')+'-'+rcnt_a[2]+' '+rcnt_a[3]+':'+rcnt_a[4]
	print '</td></tr>'
fill = 10 - lc
for n in range(1,fill):
        print '<tr><td><font size="2">&nbsp;</td><td><font size="2">&nbsp;</td></tr>'
print '</table>'
print '</td></tr>'
print '</table>'

####

print '<table width="1412" cellpadding="0" cellspacing="0">'
print '<tr>'
print '<td>'
print '<table width="236" height="270" frame="box">'
print '<tr><td><font size="2"><b>Top Src IPs</td><td></td></tr>'
lc = 0
for line in topsrc:
	lc += 1
	print '<tr><td><font size="2">'
	print '&nbsp;<a href="./pygqry.cgi?a=0&o='+frmid+'&m=se&src='+numtoip(int(line.split('~')[0]))+'">'+numtoip(int(line.split('~')[0]))+'</a>'
	print '</td>'
	print '<td><font size="2">'
	print line.split('~')[1]
	print '</td></tr>'
fill = 10 - lc
for n in range(1,fill):
        print '<tr><td><font size="2">&nbsp;</td><td><font size="2">&nbsp;</td></tr>'
print '</table>'
print '</td>'
print '<td>'
print '<table width="236" height="270" frame="box">'
print '<tr><td><font size="2"><b>Top Dst IPs</td><td></td></tr>'
lc = 0
for line in topdst:
	lc += 1
        print '<tr><td><font size="2">'
        print '&nbsp;<a href="./pygqry.cgi?a=0&o='+frmid+'&m=de&dst='+numtoip(int(line.split('~')[0]))+'">'+numtoip(int(line.split('~')[0]))+'</a>'
        print '</td>'
        print '<td><font size="2">'
        print line.split('~')[1]
        print '</td></tr>'
fill = 10 - lc
for n in range(1,fill):
        print '<tr><td><font size="2">&nbsp;</td><td><font size="2">&nbsp;</td></tr>'
print '</table>'
print '</td>'
print '<td>'
print '<table width="235" height="270" frame="box">'
print '<tr><td><font size="2"><b>Top Src TCP Ports</td><td></td></tr>'
lc = 0
for line in tcpsp:
	lc += 1
        print '<tr><td><font size="2">'
        print '&nbsp;<a href="./pygqry.cgi?a=0&o='+frmid+'&m=se&tcpsrc='+line.split('~')[0]+'">'+line.split('~')[0]+'</a>'
        print '</td>'
        print '<td><font size="2">'
        print line.split('~')[1]
        print '</td></tr>'
fill = 10 - lc
for n in range(1,fill):
        print '<tr><td><font size="2">&nbsp;</td><td><font size="2">&nbsp;</td></tr>'
print '</table>'
print '</td>'
print '<td>'
print '<table width="235" height="270" frame="box">'
print '<tr><td><font size="2"><b>Top Dst TCP Ports</td><td></td></tr>'
lc = 0
for line in tcpdp:
	lc += 1
        print '<tr><td><font size="2">'
        print '&nbsp;<a href="./pygqry.cgi?a=0&o='+frmid+'&m=de&tcpdst='+line.split('~')[0]+'">'+line.split('~')[0]+'</a>'
        print '</td>'
        print '<td><font size="2">'
        print line.split('~')[1]
        print '</td></tr>'
fill = 10 - lc
for n in range(1,fill):
        print '<tr><td><font size="2">&nbsp;</td><td><font size="2">&nbsp;</td></tr>'
print '</table>'
print '</td>'
print '<td>'
print '<table width="235" height="270" frame="box">'
print '<tr><td><font size="2"><b>Top Src UDP Ports</td><td></td></tr>'
lc = 0
for line in udpsp:
	lc += 1
        print '<tr><td><font size="2">'
        print '&nbsp;<a href="./pygqry.cgi?a=0&o='+frmid+'&m=se&udpsrc='+line.split('~')[0]+'">'+line.split('~')[0]+'</a>'
        print '</td>'
        print '<td><font size="2">'
        print line.split('~')[1]
        print '</td></tr>'
fill = 10 - lc
for n in range(1,fill):
        print '<tr><td><font size="2">&nbsp;</td><td><font size="2">&nbsp;</td></tr>'
print '</table>'
print '</td>'
print '<td>'
print '<table width="235" height="270" frame="box">'
print '<tr><td><font size="2"><b>Top Dst UDP Ports</td><td></td></tr>'
lc = 0
for line in udpdp:
	lc += 1
        print '<tr><td><font size="2">'
        print '&nbsp;<a href="./pygqry.cgi?a=0&o='+frmid+'&m=de&udpdst='+line.split('~')[0]+'">'+line.split('~')[0]+'</a>'
        print '</td>'
        print '<td><font size="2">'
        print line.split('~')[1]
        print '</td></tr>'
fill = 10 - lc
for n in range(1,fill):
        print '<tr><td><font size="2">&nbsp;</td><td><font size="2">&nbsp;</td></tr>'
print '</table>'
print '</td>'
qryend = time.time()
print '<tr><td align="left"><font size="2">(query: '+str(round(qryend - cgistart,3))+'s)</td>'
print '<td></td><td></td><td></td><td></td>'
print '<td align="right"><font size="2">('+pyver+')</td></tr>'
print '</table>'
print '</body>'
print '</html>'
