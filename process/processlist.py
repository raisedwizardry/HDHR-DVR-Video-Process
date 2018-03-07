#!/usr/bin/python3

import os
import subprocess
import sys
import arrow
import datetime
import time
import urllib.request as urllib2
from bs4 import BeautifulSoup
import requests

#the crontab entry:
#10,40 * * * * run-one /usr/bin/python3 /srv/samba/E5TB/Video/DVR/convert/tools/processlist.py /srv/samba/E5TB/Video/DVR/convert/tools/config/config.txt
#3 20 * * * /usr/bin/python3 /srv/samba/E5TB/Video/DVR/convert/tools/clean.py /srv/samba/E5TB/Video/DVR/convert/tools/config/config.txt

#command to start DVR:
#sudo /srv/samba/E5TB/Video/DVR/app/hdhomerun_record start --conf /srv/samba/E5TB/Video/DVR/convert/tools/hdhomerun.conf

class dir:
	config=sys.argv[1]

page = requests.get("http://192.168.1.38/tuners.html")
soup = BeautifulSoup(page.content, 'html.parser')
tuner0 = soup.select('body div table tr td')[1].string
tuner1 = soup.select('body div table tr td')[3].string
if tuner0 == 'none'and tuner1 == 'none':
	print('tuners are free')
else:
	print('tuners are busy')
	sys.exit()

configdir = list()
with open(str(dir.config)) as inf: #load edl file into list
	for line in inf:
		oneLine = line.split()
		configdir.append(oneLine)
	for i in range(0, len(configdir), 1):
		line=configdir[i]
		start=str(line[0]).split('=')
		name=start[0].strip("[]'")
		value=start[1].strip("[]'")
		setattr(dir, name, value)

filelist=list()
for root, directories, filenames in os.walk(str(dir.recordings)):
	for filename in filenames:
		filelist.append(os.path.join(root,filename))

encodelist=list()
for i in range(0, len(filelist), 1):
	if filelist[i].lower().endswith('.mpg'):
		encodelist.append(filelist[i])

python= str(dir.tools)+"startprocess.py"
if len(encodelist)>0:
	for i in range(0, len(encodelist), 1):
		subprocess.call(["python3", str(python), str(dir.config), str(encodelist[i])])

wmc="/srv/samba/E5TB/Video/DVR/sort/mcebudtv/"
wmcencode=str(dir.tools)+"wmctrans.py"
wmclist=list()
for root, directories, filenames in os.walk(str(wmc)):
	for filename in filenames:
		wmclist.append(os.path.join(root,filename))
if len(wmclist)>0:
	for i in range(0, len(wmclist), 1):
		today= arrow.utcnow().format('YYYYMMDD HHmmss')
		videoname=wmclist[i].split('/')[-1]
		noext=os.path.splitext(str(videoname))[0]
		thegrave=str(dir.grave) + str(today) + " " + str(noext) + "/"
		subprocess.call(["mkdir", str(thegrave)])
		thelog=str(thegrave)+str(noext)+".log"
		with open(str(thelog) ,'w') as f:
			subprocess.call(["python3", str(wmcencode), str(wmclist[i]), str(noext), str(thegrave)], stdout=f, stderr=f)
