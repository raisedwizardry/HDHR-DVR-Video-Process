#!/usr/bin/python3

import sys
import os.path
import subprocess
import xml.dom
import datetime
import re
from subprocess import check_output

class dir:
	filename=sys.argv[1]
	namenoext=sys.argv[2]
	grave=sys.argv[3]
	tempout="/srv/samba/E5TB/Video/DVR/sort/"
	out="/srv/samba/E5TB/Video/DVR/sort/tv/"

def encodenow():
	newname= getName(str(dir.filename))
	width= getWidth(str(dir.filename))
	rate=getrate(str(dir.filename))
	format= getFormat(str(dir.filename), rate, width)
	encodeTime(format, str(dir.filename), rate, width, str(dir.temp))
	subprocess.call(["mv", str(dir.temp), str(newname)])
	subprocess.call(["mv", str(dir.filename), str(dir.mvgrave)])
	subprocess.call(["chown", "-R", "nobody", str(dir.grave)])

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
	newname=str(dir.namenoext)+".mkv"
	print(newname)
	output=str(dir.out) + str(newname)
	temp=str(dir.tempout)+str(newname)
	setattr(dir, "temp", temp)
	mvgrave=str(dir.grave)+str(newname)
	setattr(dir, "mvgrave", mvgrave)
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

encodenow()
