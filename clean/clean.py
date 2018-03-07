#!/usr/bin/python3

import os
import subprocess
import sys
import datetime
import arrow
import re

#crontab entry:
#3 20 * * * /usr/bin/python3 /srv/samba/E5TB/Video/DVR/convert/tools/clean.py /srv/samba/E5TB/Video/DVR/convert/tools/config/config.txt

class dir:
	config=sys.argv[1]

def pathFind():
	configdir = list()
	with open(str(dir.config)) as inf: #load edl file into list
		for line in inf:
			thisline=line.rstrip('\n')
			configdir.append(thisline)
		for i in range(0, len(configdir), 1):
			line=configdir[i].split('=')
			name=str(line[0])
			value=str(line[1])
			setattr(dir, name, value)
pathFind()
utcyesterday=arrow.utcnow().replace(days=-1).format('YYYYMMDD')
for path, dirs, files in os.walk(str(dir.recordings)):
	for name in files:
		if path == str(dir.recordings):
			fullfile=os.path.join(path, name)
			cha=os.path.splitext(str(name))[0]
			match=arrow.get(cha, 'YYYYMMDD').format('YYYYMMDD')
			if match <= utcyesterday:
				#subprocess.call(["mv", os.path.join(path, name)])
				subprocess.call(["mv", str(fullfile), str(dir.logarchive)])

utctwodays=arrow.utcnow().replace(days=-2).format('YYYYMMDD')
for path, dirs, files in os.walk(str(dir.grave)):
	for name in dirs:
		if path == str(dir.grave):
			fullfile=os.path.join(path, name)
			cha=name.split()[0]
			match=arrow.get(cha, 'YYYYMMDD').format('YYYYMMDD')
			if match < utctwodays:
				subprocess.call(["rm", "-r", str(fullfile)])

correct=list()
pathFind()
with open(str(dir.cleanlib)) as inf:
	for line in inf:
		thisline=line.rstrip('\n')
		correct.append(thisline)

seasonpattern = re.compile(r'^[S,s]\d\d[E,e]\d\d') #S03E20
filelist=list()
for i in range(0, len(correct), 1):
	high=None
	filelist[:] = []
	scompare=0
	ecompare=0
	show=str(dir.library)+str(correct[i])+"/"
	for root, directories, filenames in os.walk(str(show)):
		for filename in filenames:
			filelist.append(os.path.join(root,filename))
	
	if len(filelist)>0:
		for h in range(0,len(filelist),1):
			split=filelist[h].split(".")
			for j in range(0, len(split),1):
				if seasonpattern.match(split[j]) is not None:
					seasoninfo=split[j]
					season = seasoninfo[1:3]
					episode = seasoninfo[4:]
					if int(season)>=int(scompare) and int(episode)>int(ecompare):
						high=filelist[h]
						scompare=season
						ecompare=episode
	split=high.split(".")
	seasoninfo,episode,seasonc=None,None,None
	for j in range(0, len(split),1):
		if seasonpattern.match(split[j]) is not None:
			seasoninfo=split[j]
			seasonc = seasoninfo[1:3]
			episode = seasoninfo[4:]
	starte=int(episode)-5
	if starte<1:
		starte=1
	ende=int(episode)
	
	savelist=list()
	for j in range(0, len(filelist), 1):
		split=filelist[j].split(".")
		for h in range(0, len(split),1):
			if seasonpattern.match(split[h]) is not None:
				seasoninfo=split[h]
				season = seasoninfo[1:3]
				episode = seasoninfo[4:]			
				if int(season) == int(seasonc):
					if (int(starte) <= int(episode) <= int(ende)):
						savelist.append(j)
	savelist=savelist[::-1]
	for j in range(0, len(savelist), 1):
		del filelist[savelist[j]]
	if len(filelist)>0:
		for i in range(0, len(filelist), 1):
			subprocess.call(["rm", str(filelist[i])])
