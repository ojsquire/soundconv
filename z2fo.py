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

outFlac = "/media/ollie/INTENSO/ollie/Sound/compressed_lossless/"

outFlacAlb = outFlac + artistAlNum + '/' + albumAlNum + '/'

#Read from command line
doExtract = raw_input("\nExtract to the following directory?\n" + outFlacAlb + "\n(Answer Y/any other key for no): ")

#If doExtract = "Y", then do the extraction to the specified dir
if doExtract == "Y":
    print "Extracting files - this may take a few seconds..."
    myZip.extractall(outFlacAlb)
else:
    newPath = raw_input("Specify alternative path (or 'q' to quit):")
    if newPath == 'q':
        sys.exit()
    else:
        areYouSure = raw_input("Extract to the following directory?\n" + newPath + "\n(Answer Y/any other key to quit):")
        if areYouSure == "Y":
            myZip.extractall(newPath)
        else:
            sys.exit()
            

    

# <codecell>


