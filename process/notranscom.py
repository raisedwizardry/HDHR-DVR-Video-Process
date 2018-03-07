#!/usr/bin/python3

import sys
import os.path
import subprocess
import xml.dom
import datetime
import re
from subprocess import check_output
from pytvdbapi import api

class dir:
	config=sys.argv[1]
	origVideo=sys.argv[2] #/srv/samba/E5TB/Process/homerundvr/The Flash/Season 2/Run S01E01.mpg
	videoFileName=sys.argv[3]
	newname=sys.argv[4]
	thegrave=sys.argv[5]
	thelog=sys.argv[6]

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
	filename= str(dir.work) + str(dir.newname)
	setattr(dir, "filename", filename)
	
def processVideo():
	fps=getFrame(str(dir.origVideo))
	mkvfps="0:"+str(fps)+"fps"
	rate= fps.split('/')
	rate= str(format(float(rate[0])/float(rate[1]),'.5g'))
	
	createSrt()
	demuxVideo()
	muxVideo(mkvfps)
	createEdl()
	if os.path.isfile(str(dir.filename)+".edl") is True:
		createChap(mkvfps)
		removeCom(mkvfps)
	else:
		subprocess.call(["mv", str(dir.filename)+"-wcom.mkv", str(dir.filename)+".mkv"])
	python= str(dir.tools) + "trans.py"
	subprocess.call(["python3", str(python), str(dir.config), str(dir.filename)+".mkv", str(rate)])
	subprocess.call(["rm", str(dir.filename)+".mkv"])
	subprocess.call(["rm", str(dir.origVideo)])
	subprocess.call(["chown", "-R", "nobody", str(dir.thegrave)])

def getFrame(filename):
	out= subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0",
		"-show_entries", "stream=r_frame_rate", "-of", "default=noprint_wrappers=1:nokey=1",
		str(filename)])
	return str(out.decode("utf-8").split('\n')[0])

def createSrt():
	subprocess.call(["/opt/ccextractor/ccextractor" , str(dir.work)+str(dir.videoFileName)+".mpg"]) #runccextractor on copied file in mux dir
	subprocess.call(["mv", str(dir.work)+str(dir.videoFileName)+".srt", str(dir.filename)+".srt"])
	subprocess.call(["rm", str(dir.work)+str(dir.videoFileName)+".mpg"]) #remove extracted copy file from the mux dir

def demuxVideo(): #demux audio and video using projectx output to mux directory
	vid=check_output(["mediainfo", "--Inform=Video;%ID%\\n", str(dir.thegrave)+str(dir.videoFileName)+".mpg"])
	vid=vid.decode("utf-8").strip('\n').split('\n')
	aid=check_output(["mediainfo", "--Inform=Audio;%ID%\\n", str(dir.thegrave)+str(dir.videoFileName)+".mpg"])
	aid=aid.decode("utf-8").strip('\n').split('\n')
	theids=str(vid[0]) + "," + str(aid[0])
	print(theids)
	subprocess.call(["projectx", "-demux", str(dir.thegrave)+str(dir.videoFileName)+".mpg", "-id", str(theids), "-out", str(dir.work), "-name", str(dir.newname)])

def muxVideo(mkvfps): #mux audio, video, and subtitle using mkvmerge 
	subprocess.call(["mkvmerge", "-o", str(dir.filename)+"-wcom.mkv", 
		"--default-duration", str(mkvfps), 
		str(dir.filename)+".m2v", str(dir.filename)+".ac3"])

def createEdl():  #run comskip with specified comskip.ini and output a usable edl file
	subprocess.call(["comskip", "--ini="+str(dir.tools)+"comskip.ini", "--output="+str(dir.work), str(dir.filename)+"-wcom.mkv"])
	subprocess.call(["rm", str(dir.filename) + "_log.txt"])	
	subprocess.call(["rm", str(dir.filename) + "-wcom.log"])
	subprocess.call(["rm", str(dir.filename) + "-wcom.logo.txt"]) 
	subprocess.call(["rm", str(dir.filename) + "-wcom.txt"]) #remove all but the edl file
	subprocess.call(["mv", str(dir.filename) + "-wcom.edl", str(dir.filename)+".edl"])
	subprocess.call(["rm", str(dir.filename) + "-wcom.mkv"])

def createChap(mkvfps):
	edllist = list()
	with open(str(dir.filename)+".edl") as inf: #load edl file into list
		if os.stat(str(dir.filename)+".edl").st_size > 0:
			for line in inf:
				oneLine = line.split()
				edllist.append(toHHMMSS(float(oneLine[1])))
				print(edllist)
		else:
			return
	chapter=open(str(dir.filename)+".txt", 'w')
	chapter.write('CHAPTER01=00:00:00.00\n')
	chapter.write('CHAPTER01NAME=Chapter 1\n')
	for i in range (0, len(edllist), 1):
		chapter.write('CHAPTER'+str(format((i+2), '02'))+'='+ str(edllist[i]) + '\n')
		chapter.write('CHAPTER'+str(format((i+2), '02'))+'NAME=Chapter '+ str(i+2) +'\n')
	chapter.close()

def removeCom(mkvfps): #perform advertisment cutting using the edl file
	edllist = list()
	with open(str(dir.filename)+".edl") as inf: #load edl file into list
		if os.stat(str(dir.filename)+".edl").st_size > 0:
			for line in inf:
				oneLine = line.split()
				edllist.append(oneLine[0])
				edllist.append(oneLine[1])
		else:
			subprocess.call(["mkvmerge", "-o", str(dir.filename)+".mkv", "--default-duration", str(mkvfps), 
				str(dir.filename)+".m2v", str(dir.filename)+".ac3", str(dir.filename)+".srt"]) 
			subprocess.call(["rm", str(dir.filename)+".m2v"]) #archive the audio and video file
			subprocess.call(["rm", str(dir.filename)+".ac3"])
			subprocess.call(["mv", str(dir.filename)+".edl", str(dir.thegrave)]) #archive the edl file
			subprocess.call(["mv", str(dir.filename)+".srt", str(dir.thegrave)]) #archive the sub file
			return
	for x in range(0,len(edllist), 2):
		if x is 0: #first segment
			cmd = "00:00:00.00-" + toHHMMSS(float(edllist[x]))
		elif x is len(edllist): #last segment
			cmd = cmd + ",+" + toHHMMSS(float(edllist[-1])) + "-"
		else:
			cmd = cmd + ",+" + toHHMMSS(float(edllist[x-1])) + "-" + toHHMMSS(float(edllist[x]))
	subprocess.call(["mkvmerge", "-o", str(dir.filename)+".mkv", "--default-duration", str(mkvfps), 
		"--split", "parts:"+str(cmd), "--chapters", str(dir.filename)+".txt", 
		str(dir.filename)+".m2v", str(dir.filename)+".ac3", str(dir.filename)+".srt"])
	subprocess.call(["rm", str(dir.filename)+".m2v"]) #archive the audio and video file
	subprocess.call(["rm", str(dir.filename)+".ac3"])
	subprocess.call(["mv", str(dir.filename)+".srt", str(dir.thegrave)]) #archive the sub file
	subprocess.call(["mv", str(dir.filename)+".txt", str(dir.thegrave)]) #archive the sub file
	subprocess.call(["mv", str(dir.filename)+".edl", str(dir.thegrave)]) #archive the edl file

def toHHMMSS(floatVal): #turns seconds into an ffmpeg compatible HHMMSS string
	m, s = divmod(floatVal, 60)
	h, m = divmod(m, 60)
	hms = "%02d:%02d:%02d" % (h, m, s)
	return hms + "." + str(floatVal).split(".")[1] #always returns two digits

try:
	pathFind()
	processVideo()
except IndexError:
	print("Index Error occurred closed")
