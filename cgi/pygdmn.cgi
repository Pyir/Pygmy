#!/usr/local/bin/python

pyver = '0.35.4.17'

import sys,cgi,re,urllib2,socket
form=cgi.FieldStorage()

##### Simple standard error out
def stderr(err):
        print 'Content-Type: text/html'
        print ''
        print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">'
        print '<html>'
        print 'Error: '+err+'<br>'
        exit()

##### Get proxy info if configured
conf_prx=''
conf=open('/etc/pyg.conf','r')
for line in conf:
        if line.find('proxy=') == 0:
                conf_prx=line.split('=')[1].rstrip('\n')


##### Define some REs
re_ten=re.compile('^10\.')
re_oneseventwo=re.compile('^172\.')
re_oneninetwo=re.compile('^192\.168')

re_line=re.compile('>Base<')
re_span=re.compile('span id="dns')
re_ifchop=re.compile('^.*>')
re_ibchop=re.compile('</a.*$')
re_classip=re.compile('<td class="td0">')
re_span=re.compile('span id="dns')

re_cut1=re.compile('<tr><td class="td[04]">')
re_cut2=re.compile('</tr>')
re_nspn=re.compile('<span')
re_a=re.compile('>a <')
re_bchop=re.compile('</a><div.*')
re_gap=re.compile('</a>.*>')
re_tag=re.compile('<.*>')

re_ty=re.compile('[a-zA-Z0-9.]')
re_tck=re.compile('\'')
re_ip=re.compile('^[12]?[0-9]?[0-9]\.[12]?[0-9]?[0-9]\.[12]?[0-9]?[0-9]\.[12]?[0-9]?[0-9]$')


##### Get CGI vars 
try:
        ip = form["ip"].value
except Exception:
	stderr('IP required')
if ip:
	if re_tck.search(ip):
		stderr('IP format invalid, tick')
	for chr in ip:
		if not re_ty.search(chr):
			stderr('IP format invalid, type')
	if not re_ip.search(ip):
		stderr('IP format invalid, ip')	


#### Convert ip, open robtex, set formatting vars
try:
	addr = socket.getnameinfo((ip,80),0)[0]
except Exception:
	addr = 'NXDomain'

if conf_prx:
	prx = urllib2.ProxyHandler({'http':conf_prx})
	brw = urllib2.build_opener(prx)
	urllib2.install_opener(brw)

rtx = "http://www.robtex.com/ip/"+ip+".html#ip"
try:
	robpg = urllib2.urlopen(rtx)
except Exception as mecherr:
	print 'Content-Type: text/html'	
	print ''
	print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">'
	print '<html>'
	print 'There was a problem connecting to the internet.<br>The error msg was:<br>&nbsp;&nbsp;&nbsp;<i>'
	print mecherr
	exit()


#### DNSTuff lookup
re_stf_a=re.compile('^<h2>IP ')
re_stf_o=re.compile('map.*dnsmedia')
outstf = []
urlstf = 'http://www.dnsstuff.com/tools/ipall/?ip='+str(ip)
pre = 0
try:
        stfpg = urllib2.urlopen(urlstf)
except Exception:
       	outstf = 'No results<br>' 
if not outstf:
	while 1:
		line = stfpg.readline()
		if not line:
			break
		if re_stf_a.search(line):
			pre = 1
		if re_stf_o.search(line):
			pre = 0
		if pre == 1:
			outstf.append(line.rstrip('\n'))

#### Cymru ASN Lookup
re_cru_a=re.compile('<PRE>')
re_cru_o=re.compile('</PRE><P>')
urlcru = 'http://asn.cymru.com/cgi-bin/whois.cgi?action=do_whois&method_whois=whois&family=ipv4&bulk_paste='+str(ip)
outcru = []
pre = 0
try:
	crupg = urllib2.urlopen(urlcru)
except Exception:
        outcru = 'No results<br>' 
if not outcru:
	while 1:
		line = crupg.readline()
		if not line:
			break
		if re_cru_o.search(line):
			pre = 0
		if pre == 1:
			outcru.append(line.rstrip('\n'))
                if re_cru_a.search(line):
                        pre = 1


##### Start printing first block of names
print 'Content-Type: text/html'
print ''
print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">'
print '<html>'
print '<head><title>Pygmy Domain Query</title></head>'
print '<body>'
print '<font size="3" face="calibri">'
store = []
domcnt = 0
while 1:
        line = robpg.readline()
        if not line:
               break
        if re_line.search(line):
                line=re_classip.sub('\n',line)
                for subline in line.splitlines():
                        if re_span.search(subline):
                                subline=re_ibchop.sub('',subline)
                                subline=re_ifchop.sub('',subline)
				store.append(subline)		
				domcnt += 1

## Height is 16px * #rows, +1 for remainders and padding
domhgt = ((domcnt / 4) + 3 ) * 16
if domhgt > 210:
	domhgt = 210

##### Nav Buttons
print '<table width="940">'
print '<tr><td align="right"><input type=button value="Back" onClick="history.go(-1)"><input type=button value="Forward" onClick="history.go(+1)"></td></tr>'
print '</table>'


##### Top Domains block 
cols = 4
col = 0
print '<div style="width:920px; height:'+str(domhgt)+'px; overflow:auto">'
print 'Domains on '+ip+' per <a href="'+rtx+'" target="_blank">Robtex</a>:'
print '<table width="900">'
#print '<tr><td>Domains on '+ip+' per <a href="'+rtx+'" target="_blank">Robtex</a>:</td></tr>'
print '<tr>'
for dom in store:
	if col >= cols:
		print '</tr>'
		print '<tr>'
		col = 0
	print '<td>&nbsp;&nbsp;'+dom+'&nbsp;&nbsp;</td>'
	col += 1
print '</tr>'
print '</table></div>'
print '<br>'
print '<table width="950">'
print '<tr valign="top">'
print '<td width="440">'


##### DNStuff block on left
print 'DNStuff IP Info:<br>' 
for line in outstf:
	if line.find('<h2>') <> 0:
		print '&nbsp;&nbsp;'+line+'<br>' 


##### ASN Block on left
print 'ASN Info:<br>'
for line in outcru:
	if line.startswith(('1','2','3','4','5','6','7','8','9','0')):
		print '&nbsp;&nbsp;<a href="http://www.maliciousnetworks.org/chart.php?as='+line.split('|')[0]+'" target="_blank">'+line.split('|')[0].rstrip(' ')+'</a>&nbsp; | '+line.split('|')[1]+' | '+line.split('|')[2]+'<br>' 


##### Lookups block on left
print '<br>Lookups:<br>'
print '&nbsp;<a href="http://www.google.com/safebrowsing/diagnostic?site='+ip+'" target="_blank">SafeBrowsing</a>'
url = 'http://www.google.com/safebrowsing/diagnostic?site='+ip
page = urllib2.urlopen(url)
line = page.readline()
re_ms = re.compile('^.*Malicious software includes ')
re_pg = re.compile('^.*Of the.*pages we tested on the site over the past 90 days, ')
re_nw = re.compile('^.*This site was hosted on ')
re_dm = re.compile('^.*Yes, this site has hosted.*It infected ')
out = '( '
if re_ms.search(line):
	gsb = re_ms.sub('',line)
	re_end = re.compile('\..*')
	gsb = re_end.sub('',gsb)
	gsb = gsb.split(' ')
	last = ''
	exp,tro,scr = ('','','')
	for i in gsb:
		if i.find('exploit(s),') >= 0:
			exp = last
		if i.find('scripting') >= 0:
			scr = last
		if i.find('trojan(s),') >= 0:
			tro = last
		last = str(i)
	if exp:
		if int(exp) > 0:
			out += 'expl: '
		if int(exp) <= 3:
			out += '<font color="green">'
		if int(exp) > 3 and int(exp) <= 7:
			out += '<font color="orange">' 
		if int(exp) > 7:
			out += '<font color="red">'
		out += exp+'</font>, '
	if tro:
		if int(tro) > 0:
			out += 'troj: '
		if int(tro) <= 3:
			out += '<font color="green">'
		if int(tro) > 3 and int(tro) <= 7:
			out += '<font color="orange">'
		if int(tro) > 7:
			out += '<font color="red">'
		out += tro+'</font>, '
	if scr:
		if int(scr) > 0:
			out += 'scpt: '
		if int(scr) <= 3:
			out += '<font color="green">'
		if int(scr) > 3 and int(scr) <= 7:
			out += '<font color="orange">'
		if int(scr) > 7:
			out += '<font color="red">'
		out += scr+'</font>, '
if re_pg.search(line):
	out += ' page: '
	re_pgx = re.compile(' page\(.*')
	pg = re_pg.sub('',line)
	pg = re_pgx.sub('',pg) 
	if int(pg) <= 3:
		out += '<font color="green">'
	if int(pg) > 3 and int(pg) <= 7:
		out += '<font color="orange">'
	if int(pg) > 7:
		out += '<font color="red">'
	out += pg+'</font> ,'
if re_nw.search(line):
	out += ' net: '
	re_nwx = re.compile('network\(.*')
	nw = re_nw.sub('',line)
	nw = re_nwx.sub('',nw)
	if int(nw) <= 3:
		out += '<font color="green">'
	if int(nw) > 3 and int(pg) <= 7:
		out += '<font color="orange">'
	if int(nw) > 7:
		out += '<font color="red">'
	out += nw+'</font> ,'
if re_dm.search(line):
	out += ' dom: '
	re_dmx = re.compile('domain\(.*')
	dm = re_dm.sub('',line)
	dm = re_dmx.sub('',dm)
	if int(dm) <= 3:
		out += '<font color="green">'
	if int(dm) > 3 and int(dm) <= 7:
		out += '<font color="orange">'
	if int(dm) > 7:
		out += '<font color="red">'
	out += dm+'</font>'
print out.rstrip(',')+')<br>'


print '&nbsp;<a href="http://www.mcafee.com/threat-intelligence/ip/default.aspx?ip='+ip+'" target="_blank">McafeeTI</a>'
url = 'http://www.mcafee.com/threat-intelligence/ip/default.aspx?ip='+ip
page = urllib2.urlopen(url)
re_ct = re.compile('risk-meters')
re_ee = re.compile('-.*$')
re_we = re.compile('\..*$')
tier = ''
tiwr = ''
while 1:
	line = page.readline()
	if not line:
		break
	if re_ct.search(line):
		re_er = re.compile('^.*emailrep-')
		re_wr = re.compile('^.*webrep-')
		tier = re_er.sub('',line)
		tier = re_ee.sub('',tier)
		tiwr = re_wr.sub('',line)
		tiwr = re_we.sub('',tiwr)
		tier = tier.rstrip('\r\n')
		tiwr = tiwr.rstrip('\r\n')
		break
print '( web rep: '
if tiwr == 'high':
	print '<font color="red">'
if tiwr == 'med':
	print '<font color="orange">'
if tiwr == 'low':
	print '<font color="green">'
if tiwr == 'unv':
	print '<font color="grey">'
print tiwr+'</font> , mail rep:'
if tier == 'high':
	print '<font color="red">'
if tier == 'med':
	print '<font color="orange">'
if tier == 'low':
	print '<font color="green">'
if tier == 'unv':
	print '<font color="grey">'
print tier+'</font>)<br>' 


print '&nbsp;<a href="http://www.threatexpert.com/reports.aspx?find='+ip+'" target="_blank">Threat Expert</a>'
url = 'http://www.threatexpert.com/reports.aspx?find='+ip
page = urllib2.urlopen(url)
re_rs=re.compile('^.*<td>Results 1.*of ')
thx = ''
while 1:
	line = page.readline()
	if not line:
		break
	if re_rs.search(line):
		re_tg=re.compile('</td>.*')
		re_mx=re.compile(' \(l.*')
		thx = re_rs.sub('',line) 
		thx = re_tg.sub('',thx)
		thx = re_mx.sub('',thx)
		break
print '( reports: '
if len(thx) == 0:
	thx = '0' 
if int(thx) <= 5:
	print '<font color="green">'
if int(thx) > 5 and int(thx) <= 20:
	print '<font color="orange">'
if int(thx) > 20:
	print '<font color="red">'
if thx == '200':
	thx = 'max'
print thx+'</font>'
print ' )<br>' 


print '&nbsp;<a href="http://support.clean-mx.de/clean-mx/viruses.php?review='+ip+'" target="_blank">CleanMX</a>'
url = 'http://support.clean-mx.de/clean-mx/viruses.php?review='+ip
page = urllib2.urlopen(url)
re_td = re.compile('<td >')
cnt = 0
while 1:
	line = page.readline()
	if not line:
		break
	if re_td.search(line):
		cnt += 1
print ' ( hits: '
if cnt == 0:
	print '<font color="green">'
if cnt > 0 and cnt < 5:
	 print '<font color="orange">'
if cnt >= 5:
	 print '<font color="red">' 
print str(cnt)+'</font> )<br>'


print '&nbsp;<a href="http://www.malwaredomainlist.com/mdl.php?search='+ip+'&colsearch=IP&quantity=100&inactive=on" target="_blank">MalwareDomainList</a>'
url = 'http://www.malwaredomainlist.com/mdl.php?search='+ip
page = urllib2.urlopen(url)
re_trbg = re.compile('^<tr bgcolor')
cnt = 0 
while 1:
	line = page.readline()
	if not line:
		break
	if re_trbg.search(line):
		cnt += 1
print ' ( hits: '
if cnt == 0:
	print '<font color="green">'
if cnt > 0 and cnt < 5:
	print '<font color="orange">'
if cnt >= 5:
	print '<font color="red">'
print str(cnt)+'</font> )<br>'


print '&nbsp;<a href="http://www.dronebl.org/lookup?ip='+ip+'" target="_blank">DroneBL</a>'
url = 'http://www.dronebl.org/lookup?ip='+ip
page = urllib2.urlopen(url)
re_yes = re.compile('There have been listings')
afrm = 0
while 1:
	line = page.readline()
	if not line:
		break
	if re_yes.search(line):
		afrm = 1
if afrm == 1:
	print ' ( <font color="red">found</font> )<br>'
if afrm == 0:
	print ' ( <font color="green">null</font> )<br>' 


#print '&nbsp;<a href="http://amada.abuse.ch/?search='+ip+'" target="_blank">Amada</a>'
#url = 'http://amada.abuse.ch/?search='+ip
#page = urllib2.urlopen(url)
#re_da = re.compile('<td>Dateadded')
#cnt = 0
#while 1:
#	line = page.readline()
#	if not line:
#		break
#	if re_da.search(line):
#		cnt += 1
#print ' ( hits: '
#if cnt == 0:
#	print '<font color="green">'
#if cnt > 0 and cnt < 5:
#	print '<font color="orange">'
#if cnt >= 5:
#	print '<font color="red">'
#print str(cnt)+'</font> )<br>'


print '&nbsp;<a href="https://zeustracker.abuse.ch/monitor.php?search='+ip+'" target="_blank">Zeus</a>'
url = 'https://zeustracker.abuse.ch/monitor.php?ipaddress='+ip
page = urllib2.urlopen(url)
re_gm = re.compile('Get more information')
cnt = 0
while 1:
	line = page.readline()
	if not line:
		break
	if re_gm.search(line):
		cnt += 1
print ' ( hits: '
if cnt == 0:
	print '<font color="green">'
if cnt > 0 and cnt < 5:
	print '<font color="orange">'
if cnt >= 5:
	print '<font color="red">'
print str(cnt)+'</font> )<br>'


print '&nbsp;<a href="https://spyeyetracker.abuse.ch/monitor.php?search='+ip+'" target="_blank">SpyEye</a>'
url = 'https://spyeyetracker.abuse.ch/monitor.php?ipaddress='+ip
page = urllib2.urlopen(url)
re_sy = re.compile('onmouseover=')
cnt = 0
while 1:
	line = page.readline()
	if not line:
		break
	if re_sy.search(line):
		cnt += 1
print ' ( hits: '
if cnt == 0:
	print '<font color="green">'
if cnt > 0 and cnt < 5:
	print '<font color="orange">'
if cnt >= 5:
	print '<font color="red">'
print str(cnt)+'</font> )<br>'


print '&nbsp;<a href="http://www.malwaregroup.com/ipaddresses/details/'+ip+'" target="_blank">MalwareGroup</a>'
url = 'http://www.malwaregroup.com/ipaddresses/details/'+ip
page = urllib2.urlopen(url)
re_sh = re.compile('red-shield')
cnt = 0
while 1:
	line = page.readline()
	if not line:
		break
	if re_sh.search(line):
		cnt += 1
print ' ( hits: '
if cnt == 0:
	print '<font color="green">'
if cnt > 0 and cnt < 5:
	print '<font color="orange">'
if cnt >= 5:
	print '<font color="red">'
print str(cnt)+'</font> )<br>'

##### Other 
print '&nbsp;<a href="http://www.ipvoid.com/scan/'+ip+'/" target="_blank">IPVoid</a><br>'
print '&nbsp;<a href="http://hosts-file.net/default.asp?s='+ip+'" target="_blank">HpHosts</a><br>'
print '</td>'
print '<td>'
cip = ip.split('.')[0]+'.'+ip.split('.')[1]+'.'+ip.split('.')[2]
url = "http://www.robtex.com/ip/"+cip+".html#ip"
page = urllib2.urlopen(url)
print '<div style="width:473px; height:400px; overflow:auto">'


##### Neighbor block on right
print 'Domains(A) for IPs in the block per <a href="'+url+'" target="_blank">Robtex</a><br>'
while 1:
        line = page.readline()
        if not line:
               break
        if re_line.search(line):
                line=re_cut1.sub('\n',line)
                line=re_cut2.sub('\n',line)
                for subline in line.splitlines():
                        if re_nspn.search(subline):
                                if re_a.search(subline):
                                        subline=re_bchop.sub('',subline)
                                        subline=re_gap.sub(' ',subline)
                                        subline=re_tag.sub('',subline)
                                        print '&nbsp;&nbsp;'+subline.split()[1]+'&nbsp;&nbsp;&nbsp;'+subline.split()[0]+'</a><br>'

print '<td></tr></div></table>'
