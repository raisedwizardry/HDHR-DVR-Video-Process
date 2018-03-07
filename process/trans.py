#!/usr/bin/python3

import sys
import os.path
import subprocess
import xml.dom
import datetime
import re
from subprocess import check_output
from pytvdbapi import api
import omdb

class dir:
	config=sys.argv[1]
	video=sys.argv[2]

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
		rate=sys.argv[3]
		setattr(dir, "rate", rate)
	except IndexError:
		rate=getrate(dir.video)
		setattr(dir, "rate", rate)

def encodenow():
	newname= getName(dir.video)
	width= getWidth(dir.video)
	format= getFormat(dir.video, dir.rate, width)
	encodeTime(format, dir.video, dir.rate, width, dir.temp)
	subprocess.call(["mv", str(dir.temp), str(newname)])

def getrate(video):
	out= subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0",
		"-show_entries", "stream=r_frame_rate", "-of", "default=noprint_wrappers=1:nokey=1",
		str(video)])
	fps=str(out.decode("utf-8").split('\n')[0])
	rate= fps.split('/')
	rate= str(format(float(rate[0])/float(rate[1]),'.5g'))
	return rate

def getName(video):
	output=None
	videoFileNoExt = video.split('.')[0] #/srv/samba/E5TB/Process/homerundvr/The Flash/Season 2/Run S01E01
	videoFileName = videoFileNoExt.split('/')[-1]
	split=videoFileName.split('-')
	if len(split)==3:
		newname=str(split[0])+ "." + str(split[1]) + "." + str(split[2]) + ".mkv"
		output=str(dir.tvout) + str(newname)
	elif len(split)==2:
		newname=str(split[0])+ "." + str(split[1])+".mkv"
		output=str(dir.tempout) + str(newname)
	elif len(split)==1:
		search = omdb.search(videoFileName)
		newname=str(search[0].title)+" ("+str(search[0].year)+").mkv"
		output=str(dir.movieout) + str(newname)
	elif len(split)>3:
		newname=str(split[0])+ "." + str(split[1])+".mkv"
		output=str(dir.tempout) + str(newname)
	else:
		newname=videoFileName
		output=str(dir.manualout) + str(newname)
	temp=str(dir.tempout)+str(newname)
	setattr(dir, "temp", temp)
	return output

def getWidth(currentFile):
	width=check_output(["mediainfo", "--Inform=Video;%Width%\\n", str(currentFile)])
	return str(width.decode("utf-8").strip('\n').split('\n')[0])

def getFormat(video, rate, width):
	if float(rate) == 29.97:
		if int(width) > 1280:
			format= "fullthirty"
		elif int(width) == 1280:
			format= "hdthirty"
		elif int(width) < 1280:
			format= "sdthirty"
	elif float(rate) == 59.94:
		if int(width) > 1280:
			format= "fullsixty"
		elif int(width) == 1280:
			format= "hdsixty"
		elif int(width) < 1280:
			format= "sdsixty"
	else:
		format="strange"
	return format

def encodeTime(format, video, rate, width, output):
	if format == "fullthirty" or format == "hdthirty" or format == "sdthirty" or format == "fullsixty" or format == "hdsixty":
		detel= "--detelecine"
		rate= "23.976"
	if format == "sdsixty" or format =="strange":
		detel= "--cfr"
		rate= str(rate)
	if format == "fullsixty" or format == "fullthirty":
		width=1280
		quality="24.0"
	if format == "hdsixty" or format == "hdthirty":
		width=width
		quality="22.0"
	if format == "fullthirty" or format == "hdthirty" or format == "fullsixty" or format == "hdsixty":
		subprocess.call(["HandBrakeCLI", "-i", str(video),	"-s", "1", "-m",  
		"-e", "x264", "-q", str(quality), "-E", "copy", "--audio-fallback", "av_aac",
		"--keep-display-aspect", "--modulus", "16", "--crop",  "<0:0:0:0>",
		"-w", str(width), "-r", str(rate), str(detel), 
		"--h264-level", "4.1", "--x264-preset", "veryfast", "--x264-tune", "film", "--x264-profile", "high",
		"-o", str(output)])
	if format == "strange" or format =="sdthirty" or format =="sdsixty":
		quality="18.0"
		subprocess.call(["HandBrakeCLI", "-i", str(video),	"-s", "1", "-m",  
		"-e", "x264", "-q", str(quality), "-E", "copy", "--audio-fallback", "av_aac",
		"-r", str(rate),  str(detel), "--keep-display-aspect", "--modulus", "16", 
		"--h264-level", "4.1", "--x264-preset", "veryfast", "--x264-profile", "high",
		"-o", str(output)])

pathFind()
encodenow()
