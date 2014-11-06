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
import glob

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
whereExtract = "/tmp/z2fo/"

for filename in zippedFiles:
    myZip.extract(filename, path=whereExtract) #extract files to /tmp

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

#Next step is to rename all extracted files in the dir according to each files specific metadata and some pattern.

#Create new file names in desired format
newTrackNames = []
for tracks in allMeta:
    tn = "%02d" % int(tracks['TRACKNUMBER'])
    trAlNum = re.sub(r'\W+', '_', tracks['TITLE'])
    newFname = tn + '_' + trAlNum + '.flac'
    newTrackNames.append(newFname)
    
#Check file names with user
print "\nRename tracks as follows?"
for track in newTrackNames:
    print track
    
rename = raw_input("\nAnswer Y/any other no: ")
        
if rename == "Y":
    #Rename files to my desired style (note use of zip)
    for oldName, newName in zip(flacFiles, newTrackNames):
        cmd = ["mv", whereExtract + oldName, whereExtract + newName]
        sp.call(cmd)
else:
    pass

# <codecell>

#Next is to convert to OGG.
#oggConvert = raw_input("Convert to OGG? 'Y' to convert, any other key to exit.")

#Need root name without ending, as will use for both .flac and .ogg
newTrackRoot = []
for tracks in allMeta:
    tn = "%02d" % int(tracks['TRACKNUMBER'])
    trAlNum = re.sub(r'\W+', '_', tracks['TITLE'])
    newFname = tn + '_' + trAlNum
    newTrackRoot.append(newFname)

#Set quality of ogg (1 = lowest quality, highest compression - still sounds v. good)
quality = 1

#Create list to hold all commands (one for each track)
cmds = []

#Set output dir for oggs.
outdir = "/home/ollie/Music/" + artistAlNum + "/" + albumAlNum + "/"

#Create each command for each track, looping through each metadata item for each tracks
#(this way the ogg will have EXACT same metadata as FLAC and won't be missing any).
for meta, name in zip(allMeta,newTrackRoot):
    cmd = ["oggenc","-q",str(quality)]
    for key in meta:
        cmd.append("-c")
        if key == 'TRACKNUMBER': #For OGGs, 'TRACKNUMBER' should be 'track' 
            meta['track'] = meta.pop(key)
            cmd.append(str('track') + '=' + str(meta['track']))
        else:
            cmd.append(str(key) + '=' + str(meta[key]))
    cmd.append("-o")
    cmd.append(outdir + name + '.ogg') #output file
    cmd.append(whereExtract + name + '.flac') #input file
    cmds.append(cmd)

#print args
#for i in cmds: print i

print "convert to OGG?"
convert2ogg = raw_input("Answer 'Y' to convert, any other key to skip: ")

if convert2ogg == 'Y':
    #Execute
    for cmd in cmds:
        sp.call(cmd)
else:
    pass

#Cover art
#Need to select cover art if there is more than one image file in zip.
artwork = []
for filename in zippedFiles:
    if (filename.endswith((".jpg",".jpeg",".png",".svg",".gif")) == True):
        artwork.append(filename)

if artwork:
    if len(artwork) > 1:
        print "select artwork from the following images: "
        for art in artwork: print art.index() + art
        sys.exit() #come back to this option
    else:
        print "Adding artwork"
        cmds = []
        for name in newTrackRoot:
            cmd = ["/home/ollie/bin/ogg-cover-art.sh",whereExtract + artwork[0],outdir + name + '.ogg']
            sp.call(cmd)    
else:
    print "No artwork found, aborting"
    sys.exit()

#Copy cover art to /home/ollie/Music/
for filename in artwork:
    sp.call(["cp",whereExtract + filename, outdir])

#Now we can cp ogg and flac to all the right places.
#Don't forget artwork
#~/bin/ogg-cover-art.sh ${picture} ${OggHome}${FileName}.ogg #Ogg artwork
#done

#Further things:
#1) interface with MySQL and send all metadata to MySQL table - can then create a nice API-GUI to sit on top of 
#table to display collection (al-la discogs).
#2) Could also embed a player / use HTML5 player to play tracks via a browser - sweet! - this would be the basis of the
#website.

# <codecell>

#Check what external drives are connected. If none are connected, ask to extract locally, else exit.

#The Dir where external drives appear if connected
externalDir = "/media/ollie/"

#List them
cmd = ["ls",externalDir]
extDri = [externalDir + i + '/' for i in sp.check_output(cmd).splitlines()]

#Add rules for known external drives and folders I'd typically like to write to
ruleIntenso = "ollie/Sound/compressed_lossless/"
ruleIntenso1 = "ollie/Sound/compressed_lossless/"
ruleIomega = "Ollie/compressed_lossless/"

ruleIntensoLossy = "ollie/Music/"
ruleIntenso1Lossy = "ollie/Music/"
ruleIomegaLossy = "Ollie/Music/"

connectedDrives = []
connectedDrivesLossy = []

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

#Repeat for Lossy (I'm sure there's a better way to do this, but right now too tired to think of it).
if [x for x in extDri if x in "/media/ollie/INTENSO/"]:
    connectedDrivesLossy.append([x for x in extDri if x in "/media/ollie/INTENSO/"][0] + ruleIntensoLossy + artistAlNum + '/' + albumAlNum + '/')
else:
    pass

if [x for x in extDri if x in "/media/ollie/INTENSO1/"]:
    connectedDrivesLossy.append([x for x in extDri if x in "/media/ollie/INTENSO1/"][0] + ruleIntenso1Lossy + artistAlNum + '/' + albumAlNum + '/')
else:
    pass

if [x for x in extDri if x in "/media/ollie/8A9C1DFF9C1DE68B/"]:
    connectedDrivesLossy.append([x for x in extDri if x in "/media/ollie/8A9C1DFF9C1DE68B/"][0] + ruleIomegaLossy + artistAlNum + '/' + albumAlNum + '/')
else:
    pass

#Set local extraction directory
localExtDir = "/home/ollie/Sound/compressed_lossless/" + artistAlNum + '/' + albumAlNum + '/'

# <codecell>

#Make backups of lossless files
if connectedDrives:
    print '\nCopy FLAC files to the following external locations? '
    for i in connectedDrives: print i
    doExtractExt = raw_input("Press 'Y' to copy, any other key to abort: ")
    if doExtractExt == 'Y':
        for drive in connectedDrives:
            print "Copying to " + drive + " this may take a few seconds..."
            sp.call(["mkdir","-p",drive])
#            sp.call(["cp",whereExtract + "*",drive])
            sp.call(['cp', '-t', drive] + glob.glob(whereExtract + '*'))
    else:
        pass
else:
    print 'No external FLAC archive dirs found. Copy locally to' + localExtDir +'instead?'
    writeLocal = raw_input("Press 'Y' to copy locally, any other key to exit: ")
    if writeLocal == "Y":
        print 'Copying to ' + localExtDir + ' this may take a few seconds...'
        sp.call(["mkdir","-p",localExtDir])
#        sp.call(["cp",whereExtract + "*",localExtDir])
        sp.call(['cp', '-t', localExtDir] + glob.glob(whereExtract + '*'))

    else:
        pass

#Set Google Drive location for backup of OGG.
googleD = '/home/ollie/Google Drive/Music/' + artistAlNum + '/' + albumAlNum + '/'

#Make backups of lossy files
if connectedDrivesLossy:
    print '\nCopy OGG files to the following external locations? '
    for i in connectedDrivesLossy: print i
    print googleD
    doExtractExt = raw_input("Press 'Y' to copy, any other key to abort: ")
    if doExtractExt == 'Y':
        for drive in connectedDrivesLossy:
            print "Copying to " + drive + " this may take a few seconds..."
            sp.call(["mkdir","-p",drive])
#            sp.call(["cp",outdir + "*",drive])
            sp.call(['cp', '-t', drive] + glob.glob(whereExtract + '*'))

        print "Copying to " + googleD
        sp.call(["mkdir","-p",googleD])
#        sp.call(["cp",outdir + "*",googleD])
        sp.call(['cp', '-t', googleD] + glob.glob(whereExtract + '*'))

    else:
        pass
else:
    pass

#sp.call(['cp', '-t', drive] + glob.glob(whereExtract + '*'))

print "Finished"

# <codecell>

#At this point, we have extracted all of the metadata and so can delete the extracted files from /tmp/
for filename in zippedFiles:
    cmd = ["rm","-f",whereExtract + filename]
    sp.call(cmd)

