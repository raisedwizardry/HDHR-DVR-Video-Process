#!/usr/bin/python3

import sys
import os.path
import subprocess
import xml.dom
import datetime
import arrow
import re
from subprocess import check_output
from pytvdbapi import api
import config

class dir:
	config=sys.argv[1]
	origVideo=sys.argv[2] #/srv/samba/E5TB/Process/homerundvr/The Flash/Season 2/Run S01E01.mpg

def pathFind():
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
	try:
		leftonlist=sys.argv[3]
		setattr(dir, "leftonlist", leftonlist)
	except IndexError:
		leftonlist=None
		setattr(dir, "leftonlist", leftonlist)

def begin():
	stripName()
	logfile=str(dir.work) + str(dir.videoFileName)+".log" #/DVR/grave/OriginalFilename.log
	thelog= open(str(logfile), 'w')
	setattr(dir, "thelog", thelog)
	today= arrow.utcnow().format('YYYYMMDD HHmmss')
	if dir.leftonlist is not None:
		print("Videos remaining to process: " + dir.leftonlist, file=dir.thelog)
	print ("Next video process started at " + today, file=dir.thelog)
	print ("Pre-processing started now", file=dir.thelog)
	newname=simpleName(dir.videoFileName)
	setattr(dir, "newname", newname)
	grave= str(dir.grave) + str(today) + " " + str(dir.newname) + "/"
	setattr(dir, "grave", grave)
	print("creating grave directory", file=dir.thelog)
	print(dir.grave, file=dir.thelog)
	subprocess.call(["mkdir", dir.grave])
	print("copying Video to grave and work folders", file=dir.thelog)
	if os.path.isfile(str(dir.work)+str(dir.videoFileName)+".mpg") is False:
		subprocess.call(["cp", str(dir.origVideo), str(dir.work)]) #copy original file to mux dir
	subprocess.call(["cp", str(dir.origVideo), str(dir.grave)]) #copy original file to mux dir
	print("Main processing will now start", file=dir.thelog)
	dir.thelog.close()
	newlogfile=str(dir.grave) + str(newname)+".log"
	setattr(dir, "newlogfile", newlogfile)
	subprocess.call(["mv", str(logfile), str(dir.newlogfile)])
	#thelog= open(str(dir.newlogfile), 'a')
	#setattr(dir, "thelog", thelog)

def processNow():
	python= str(dir.tools)+"notranscom.py"
	with open(str(dir.newlogfile) ,'a') as f:
		subprocess.call(["python3", str(python), str(dir.config), str(dir.origVideo),
			str(dir.videoFileName), str(dir.newname), str(dir.grave), str(dir.thelog)],
			#"2>&1", "|", "tee", "-a", str(dir.thelog)])
			stdout=f, stderr=f)

def stripName():
	videoFileNoExt = dir.origVideo.split('.')[0] #/srv/samba/E5TB/Process/homerundvr/The Flash/Season 2/Run S01E01
	if videoFileNoExt.split('/')[-2]=="Movies":
		vidtype=0
		setattr(dir, "vidtype", vidtype)
	else:
		vidtype=1
		setattr(dir, "vidtype", vidtype)
	videoFileName = videoFileNoExt.split('/')[-1] #Run S01E01
	setattr(dir, "videoFileName", videoFileName)

def simpleName(videoFileName):
	split=str.split(videoFileName)
	datepattern = re.compile(r'^[1,2][9,0,1]\d\d[0,1]\d[0-3]\d$')
	seasonpattern = re.compile(r'^[S,s]\d\d[E,e]\d\d$') #S03E20
	abpattern = re.compile(r'^[E,e][P,p][0-9]+$') 
	seasoninfo, title, aired, seasonepisode, newfilename,season,episode,apepi,absolute=None,None, None, None, None, None, None, None, None
	exclude=[':','#','%','&','{','}','\\','<','>','*','?','/','$','!',"'",'/','"','@','+','|','=','.',',','-']
	sc = set(exclude)
	if int(dir.vidtype)==1:
		print("Video is a TV Show", file=dir.thelog)
		for i in range(0, len(split)):
			if seasonpattern.match(split[i]) is not None:
				seasoninfo=split[i]
				season = seasoninfo[1:3]
				episode = seasoninfo[4:]
				title=" ".join(split[:i])
		if seasoninfo is None:
			for i in range(0, len(split)):	
				if abpattern.match(split[i]) is not None:
					title=" ".join(split[:i])
					apepi=split[i]
					absolute=apepi[1:]
				if datepattern.match(split[i]) is not None:
					aired=split[i]
					if apepi is None:
						title=" ".join(split[:i])
		if title is not None:
			print("Found video title", file=dir.thelog)
			db = api.TVDB(TVDB_APIKEY)
			show=None
			result = db.search(str(title), "en")
			try:
				show = result[0]
			except IndexError:
				print("no match found in TVDB with name", file=dir.thelog)
				show=None
			if show is not None:
				print("match found in TVDB", file=dir.thelog)
				if seasoninfo is not None:
					print("season info found in name", file=dir.thelog)
					try:
						season=show[int(season)]
					except IndexError:
						print("Episode Error: no season found for this show", file=dir.thelog)
						show=None
					try:
						episode=season[int(episode)]
					except IndexError:
						print("Episode Error: no episode found within season", file=dir.thelog)
						show=None
					if show is not None:
						newshowname=show.SeriesName
						newepisodename=None
						newepisodename=''.join([c for c in str(episode.EpisodeName) if c not in sc])
						newshowname=''.join([c for c in str(newshowname) if c not in sc])
						newfilename= str(newshowname)+"-S"+str(format(episode.SeasonNumber, '02'))+"E"+str(format(episode.EpisodeNumber,'02'))+"-"+str(newepisodename)
				elif seasoninfo is None:
					print("show and season info not found in name", file=dir.thelog)
					if aired is not None:
						print("using airdate to find episode info", file=dir.thelog)
						newshowname=show.SeriesName
						match= datetime.datetime.strptime(aired, "%Y%m%d").date()
						episodes = show.filter(key=lambda ep: ep.FirstAired == match)
						newepisodename=None
						for ep in episodes:
							season=ep.SeasonNumber
							episode=ep.EpisodeNumber
							newepisodename=ep.EpisodeName
						if newepisodename is not None and season is not None and episode is not None:
							newepisodename=''.join([c for c in str(newepisodename) if c not in sc])
							newshowname=''.join([c for c in str(newshowname) if c not in sc])
							newfilename= str(newshowname)+"-S"+str(format(season, '02'))+"E"+str(format(episode,'02'))+"-"+str(newepisodename)
						else:
							print("no episode found by airdate", file=dir.thelog)
							print("using airdate only", file=dir.thelog)
							newshowname=''.join([c for c in str(title) if c not in sc])
							newfilename= str(newshowname)+"-"+str(aired)
					elif aired is None:
						print("no matches season, episode, or airdate", file=dir.thelog)
						newshowname=''.join([c for c in str(videoFileName) if c not in sc])
						newfilename= str(newshowname)
			if show is None:
				print("no match found manually", file=dir.thelog)
				if seasoninfo is not None:
					print("show and season info found in name", file=dir.thelog)
					newshowname=''.join([c for c in str(title) if c not in sc])
					newfilename= str(newshowname)+"-"+str(seasoninfo)
				elif seasoninfo is None:
					print("show and season info not found in name", file=dir.thelog)
					if aired is not None:
						print("using airdate only", file=dir.thelog)
						newshowname=''.join([c for c in str(title) if c not in sc])
						newfilename= str(newshowname)+"-"+str(aired)
					elif aired is None:
						print("no matches season, episode, or airdate", file=dir.thelog)
						newshowname=''.join([c for c in str(videoFileName) if c not in sc])
						newfilename= str(newshowname)
		else:
			print("no title found filename not changed", file=dir.thelog)
			title=" ".join(split[:i])
			newshowname=''.join([c for c in str(videoFileName) if c not in sc])
			newfilename= str(newshowname)
	elif int(dir.vidtype)==0:
		print("video is a Movie", file=dir.thelog)
		for i in range(0, len(split)):
			if datepattern.match(split[i]) is not None:
				print("using movie date to find title only", file=dir.thelog)
				title=" ".join(split[:i])
				newfilename= str(title)
		if title is None:
			print("no title found filename not changed", file=dir.thelog)
			newshowname=''.join([c for c in str(videoFileName) if c not in sc])
			newfilename= str(newshowname)
	return newfilename

try:
	pathFind()
	begin()
	processNow()
except IndexError:
	print("Index Error occurred closed")
