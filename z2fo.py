# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# z2fo (zip-2-FLAC+OGG)

# <codecell>

#Note: opening this file with the --script option ensures that a .py version is saved automatically that can be run
#with the bash command: z2fo (I set up an alias in .bashrc)
#
#This script unzips a zip containing FLACs and converts to OGGs

# <codecell>

import sys
import argparse
import zipfile
import os
import re
import subprocess as sp

# <codecell>

#Set dirs for FLAC backups.
outFlac = "/media/ollie/INTENSO/ollie/Sound/compressed_lossless/"
outFlac1 = "/media/ollie/INTENSO1/ollie/Sound/compressed_lossless/" 


#Handle parsing of arguements to function

#Create an instance of an arguement parser (gives us --help for free)
parser = argparse.ArgumentParser()

#Add an arguement
parser.add_argument("zipFname", help="""the filename of the zip you 
                    want to extract""")
args = parser.parse_args()
zipFname = args.zipFname

# <codecell>

#Check if file exists
if (os.path.isfile(zipFname) == False):
    print "File does not exist, aborting."
    sys.exit()
    
#Check if file is a zip
if (zipFname.endswith(".zip") == False):
    print "File " + zipFname + " is not a zip, aborting."
    sys.exit()

# <codecell>

#Get list of all FLAC files
myZip = zipfile.ZipFile(zipFname)
zippedFiles = myZip.namelist() #List of all zipped files.

#Get a sublist of just the FLAC files
flacFiles = []

for filename in zippedFiles:
    if (filename.endswith(".flac") == True):
        flacFiles.append(filename)
        
#Exit if no FLAC files are found
if not flacFiles:
    print "No FLAC files were found, aborting."
    sys.exit()

#Print found FLAC files
print str(len(flacFiles)) + " FLAC files were found"
for flac in flacFiles:
    print flac

#Extract first FLAC file (so can examine metadata)
whereExtract = "/tmp/"
metaflacFile = flacFiles[0]
myZip.extract(metaflacFile, path=whereExtract) #extract file to /tmp

#For convenience, set full path to extracted file
metaflacFullPath = whereExtract+metaflacFile

#Set up a metaflac command on extracted file 
cmd = ["metaflac","--list","--block-type=VORBIS_COMMENT",metaflacFullPath]

#Run the command using subprocess
vorbisComment = sp.check_output(cmd)

#At this point we can delete the extracted file
#sp.call(["rm","-f",metaflacFullPath])

#This output is a single string containing all the data from the VORBIS_COMMENT block
#so let's split it up by newlines to make it easier to extract the info we need.
vorbisCommentList = vorbisComment.split("\n")

#Get the artist
artistComment = [s for s in vorbisCommentList if " ARTIST=" in s]
artist = artistComment[0].split("ARTIST=")[1]

#Get the album
albumComment = [s for s in vorbisCommentList if " ALBUM=" in s]
album = albumComment[0].split("ALBUM=")[1]

artistAlNum = re.sub(r'\W+', '_', artist)
albumAlNum = re.sub(r'\W+', '_', album)

outFlacAlb = outFlac + artistAlNum + '/' + albumAlNum + '/'
outFlacAlb1 = outFlac1 + artistAlNum + '/' + albumAlNum + '/'

#Check if extraction dirs already exist, and whether they are empty or not.
#This next block asks whether you'd like to extract to dir0, if yes, check if exists, if does, ask again, if no go to next, if yes, extract, if no, 
#ask for another file name, then go to next, if don't want to extract to new file name, go to next, then either extract w/ same line of questioning
#or exit. That clear?
doExtract = raw_input("\nExtract to the following directory?\n" + outFlacAlb + "\n(Answer Y/any other key for no): ")

if doExtract == "Y":
    if (os.path.isdir(outFlacAlb)==True):
        writeToDir = raw_input("Directory" + outFlacAlb + " already exists. Proceed with extraction?\n Answer Y/any other key for no:")
        if writeToDir == "Y":
            print "Extracting files - this may take a few seconds..."
            myZip.extractall(outFlacAlb)
        else:
            doExtract1 = raw_input("\nExtract to the following directory?\n" + outFlacAlb1 + "\n(Answer Y/any other key for no): ")
            if doExtract1 == "Y":
                if (os.path.isdir(outFlacAlb1)==True):
                    writeToDir = raw_input("Directory" + outFlacAlb + " already exists. Proceed with extraction?\n Answer Y/any other key for no:")
                    if writeToDir == "Y":
                        print "Extracting files - this may take a few seconds..."
                        myZip.extractall(outFlacAlb1)
                    else:
                        print "No files extracted, continuing with meta read."
                        pass
                else:
                    print "Extracting files - this may take a few seconds..."
                    myZip.extractall(outFlacAlb1)
            else:
                newPath = raw_input("Specify alternative path (or 's' to skip to meta reading):")
                if newPath == 's':
                    pass
                else:
                    areYouSure = raw_input("Extract to the following directory?\n" + newPath + "\n(Answer Y/any other key to quit):")
                    if areYouSure == "Y":
                        myZip.extractall(newPath)
                    else:
                        pass
    else:
        print "Extracting files - this may take a few seconds..."
        myZip.extractall(outFlacAlb)
        doExtract1 = raw_input("\nExtract to the following directory?\n" + outFlacAlb1 + "\n(Answer Y/any other key for no): ")
        if doExtract1 == "Y":
            if (os.path.isdir(outFlacAlb1)==True):
                writeToDir = raw_input("Directory" + outFlacAlb + " already exists. Proceed with extraction?\n Answer Y/any other key for no:")
                if writeToDir == "Y":
                    print "Extracting files - this may take a few seconds..."
                    myZip.extractall(outFlacAlb1)
                else:
                    print "No files extracted, skipping to meta read."
                    pass
            else:
                print "Extracting files - this may take a few seconds..."
                myZip.extractall(outFlacAlb1)
        else:
            newPath = raw_input("Specify alternative path (or 's' to skip to meta read):")
            if newPath == 's':
                pass
            else:
                areYouSure = raw_input("Extract to the following directory?\n" + newPath + "\n(Answer Y/any other key to quit):")
                if areYouSure == "Y":
                    myZip.extractall(newPath)
                else:
                    pass
else:
    newPath = raw_input("Specify alternative path (or 's' to skip to next extraction dir):")
    if newPath == 's':
        doExtract1 = raw_input("\nExtract to the following directory?\n" + outFlacAlb1 + "\n(Answer Y/any other key for no): ")
        if doExtract1 == "Y":
            if (os.path.isdir(outFlacAlb1)==True):
                writeToDir = raw_input("Directory" + outFlacAlb + " already exists. Proceed with extraction?\n Answer Y/any other key for no:")
                if writeToDir == "Y":
                    print "Extracting files - this may take a few seconds..."
                    myZip.extractall(outFlacAlb1)
                else:
                    print "No files extracted, skipping to meta read."
                    pass
            else:
                print "Extracting files - this may take a few seconds..."
                myZip.extractall(outFlacAlb1)
        else:
            newPath = raw_input("Specify alternative path (or 's' to skip to meta read):")
            if newPath == 's':
                pass
            else:
                areYouSure = raw_input("Extract to the following directory?\n" + newPath + "\n(Answer Y/any other key to quit):")
                if areYouSure == "Y":
                    myZip.extractall(newPath)
                else:
                    pass
    else:
        areYouSure = raw_input("Extract to the following directory?\n" + newPath + "\n(Answer Y/any other key to quit):")
        if areYouSure == "Y":
            myZip.extractall(newPath)
        else:
            pass

# <codecell>

#Next step is to rename all extracted files in the dir according to each files specific metadata and some pattern.
#Pull all metadata

vorbisComments = []
for filename in flacFiles:
    #Set up a metaflac command on extracted file 
    cmd = ["metaflac","--list","--block-type=VORBIS_COMMENT",outFlacAlb + filename]
    
    #Run the command using subprocess
    vorbisComments.append(sp.check_output(cmd))

#create a dictionary to hold key/value pairs
allMeta = []
for comV in vorbisComments:
    comVSplit = comV.split("\n")
    trackComments = {}
    for comment in comVSplit:
        p = re.compile(r"    comment\[\d*\]: ")
        m = p.match(comment)
        if m == None:
            pass
        else:
            mm = m.group()
            trackComments[comment.split(mm)[1].split('=',1)[0]] = comment.split(mm)[1].split('=',1)[1]
    allMeta.append(trackComments)

#Create new file names in desired format
newTrackNames = []
for tracks in allMeta:
    tn = "%02d" % int(tracks['TRACKNUMBER'])
    trAlNum = re.sub(r'\W+', '_', tracks['TITLE'])
    newFname = tn + '_' + trAlNum + '.flac'
    newTrackNames.append(newFname)

#Check file names with user
print "Rename tracks as follows?\n"
for track in newTrackNames:
    print track
raw_input("\nAnswer Y/any other no: ")

#Rename files to my desired style.
for i in range(0,len(allMeta)):
    tn = "%02d" % int(allMeta[i]['TRACKNUMBER'])
    trAlNum = re.sub(r'\W+', '_', allMeta[i]['TITLE'])
    newFname = outFlacAlb + tn + '_' + trAlNum + '.flac'
    newFname1 = outFlacAlb1 + tn + '_' + trAlNum + '.flac'
    cmd = ["mv",outFlacAlb + flacFiles[i], newFname]
    sp.call(cmd)
    cmd1 = ["mv",outFlacAlb1 + flacFiles[i], newFname]
    sp.call(cmd1)

#Next is to convert to OGG.

# <codecell>

#Further things:
#1) interface with MySQL and send all metadata to MySQL table - can then create a nice API-GUI to sit on top of 
#table to display collection (al-la discogs).
#2) Could also embed a player / use HTML5 player to play tracks via a browser - sweet! - this would be the basis of the
#website.

# <codecell>


