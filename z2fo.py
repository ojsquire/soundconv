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

#Print found files
print "\n" + str(len(zippedFiles)) + " files were found:"
for filename in zippedFiles:
    print filename

#Extract all FLAC files to /tmp (so can examine metadata)
whereExtract = "/tmp/"

for flac in flacFiles:
    myZip.extract(flac, path=whereExtract) #extract files to /tmp

#Get all metadata from FLAC files extracted to /tmp/
vorbisComments = []
for filename in flacFiles:
    #Set up a metaflac command on extracted file 
    cmd = ["metaflac","--list","--block-type=VORBIS_COMMENT",whereExtract + filename]
    
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

#At this point, we have extracted all of the metadata and so can delete the extracted files from /tmp/
for filename in zippedFiles:
    cmd = ["rm","-f",whereExtract + filename]
    sp.call(cmd)

#Compilation test (test if artist tag is the same for all files)
def all_same(items):
    return all(x == items[0] for x in items)

artists = []
for track in allMeta:
    artists.append(track['ARTIST'])
    
#Run test
if all_same(artists) == True:
    artist = artists[0]
else:
    print "This is a compilation, exiting until I can handle this properly"
    exit.sys()

#Create alpha-numeric-only versions of the artist and album, for directory structure.
album = allMeta[0]['ALBUM']

artistAlNum = re.sub(r'\W+', '_', artist)
albumAlNum = re.sub(r'\W+', '_', album)

# <codecell>

#Check what external drives are connected. If none are connected, ask to extract locally, else exit.

#The Dir where external drives appear if connected
externalDir = "/media/ollie/"

#List them
cmd = ["ls",externalDir]
extDri = [externalDir + i + '/' for i in sp.check_output(cmd).splitlines()]

#Add rules for known external drives and folders I'd typically like to write to
ruleIntenso = "Sound/compressed_lossless/"
ruleIntenso1 = "Sound/compressed_lossless/"
ruleIomega = "Ollie/compressed_lossless/"

connectedDrives = []
    
#Check for connected drives and use extracted artist/album info to 
if [x for x in extDri if x in "/media/ollie/INTENSO/"]:
    connectedDrives.append([x for x in extDri if x in "/media/ollie/INTENSO/"][0] + ruleIntenso + artistAlNum + '/' + albumAlNum + '/')
else:
    pass

if [x for x in extDri if x in "/media/ollie/INTENSO1/"]:
    connectedDrives.append([x for x in extDri if x in "/media/ollie/INTENSO1/"][0] + ruleIntenso1 + artistAlNum + '/' + albumAlNum + '/')
else:
    pass

if [x for x in extDri if x in "/media/ollie/8A9C1DFF9C1DE68B/"]:
    connectedDrives.append([x for x in extDri if x in "/media/ollie/8A9C1DFF9C1DE68B/"][0] + ruleIomega + artistAlNum + '/' + albumAlNum + '/')
else:
    pass

#Set local extraction directory
localExtDir = "/ollie/Sound/compressed_lossless/" + artistAlNum + '/' + albumAlNum + '/'

# <codecell>

#Carry out extraction to all connected drives, or locally if none connected.
if connectedDrives:
    print '\nExtract to the following external locations? '
    for i in connectedDrives: print i
    doExtractExt = raw_input("Press 'Y' to extract, any other key to abort: ")
    if doExtractExt == 'Y':
        for drive in connectedDrives:
            print "Extracting to " + drive + " this may take a few seconds..."
            myZip.extractall(drive)
    else:
        sys.exit()
else:
    print 'No external FLAC archive dirs found. Write locally to' + localExtDir +'instead?'
    writeLocal = raw_input("Press 'Y' to write locally, any other key to exit: ")
    if writeLocal == "Y":
        print 'Extracting to ' + localExtDir + ' this may take a few seconds...'
    else:
        sys.exit()

# <codecell>

#Next step is to rename all extracted files in the dir according to each files specific metadata and some pattern.

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
    
rename = raw_input("\nAnswer Y/any other no: ")
        
if rename == "Y":
    #Rename files to my desired style.
    for drive in connectedDrives:
        for oldName, newName in zip(flacFiles, newTrackNames):
            cmd = ["mv", drive + oldName, drive + newName]
            sp.call(cmd)
else:
    pass

# <codecell>

#Next is to convert to OGG.
#raw_input("Convert to OGG?")
#Convert to ogg-vorbis using oggenc
#echo "Converting $((i+1))/${#tracksClean[@]} ${title} to ogg-Vorbis format."
#    FileName="${index1}_${tracksClean[i]}"     
#oggenc -q ${quality} --tracknum $((${i}+1)) --title "${title}" --artist "${artist}" --album "${album}" --date "${date}" --genre "${genre}" -o ${OggHome}${FileName}.ogg ${inputPath}${FileName}.wav
#~/bin/ogg-cover-art.sh ${picture} ${OggHome}${FileName}.ogg #Ogg artwork
#done

#Further things:
#1) interface with MySQL and send all metadata to MySQL table - can then create a nice API-GUI to sit on top of 
#table to display collection (al-la discogs).
#2) Could also embed a player / use HTML5 player to play tracks via a browser - sweet! - this would be the basis of the
#website.

# <codecell>


