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
import MySQLdb as sql

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

#Here want to add capability to handle MP3 file.
#i.e. if no FLAC are found, but MP3 found instead, rename MP3, transcode, copy to Music, backup untranscoded.
#Actually, the majority of the script would be exactly the same, would just need to add a few options to deal
#with MP3. Note: tagging would be different, as dealing with ID3 tags rather than Vorbis.
#I think we should put this on hold for the moment.

#Print found files
print "\n" + str(len(zippedFiles)) + " files were found:"
for filename in zippedFiles:
    print filename
    
#Extract all FLAC files to /tmp (so can examine metadata)
whereExtract = "/tmp/z2fo/"

print "\nExtracting into" + whereExtract + " and determining new file names. One moment..."
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

##Next is to convert to OGG.
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
    #Check if ogg files already exist
    doesExist = []
    for name in newTrackRoot:
        doesExist.append(os.path.isfile(outdir + name + '.ogg'))
    if any(doesExist) == True:
        print "OGG files already exist in specified output directory. Continue with conversion?"
        doConvert = raw_input("Press 'Y' to start conversion, any other key to pass: ")
        if doConvert == 'Y':
            #Execute
            for cmd in cmds:
                sp.call(cmd)
        else:
            pass
    else:
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
        print "Multiple artwork found. Please select from the following images: "
        for art in artwork: 
            print "Press " + str(artwork.index(art)) + " for " + art
        artOpt = raw_input("Please choose an option: " )
        artOpt = int(artOpt) #Convert from string to integer
        for art in artwork:
            if artOpt == artwork.index(art): #Check if user innput matches image
                print "Adding artwork"
                #If image is a png, convert to jpg (ogg-cover-art.sh only excepts jpg).
                if artwork[artOpt].endswith(".png"):
                    sp.call(["convert", whereExtract + artwork[artOpt], whereExtract + artwork[artOpt].split('.')[0] + '.jpg'])
                    artwork = [artwork[artOpt].split('.')[0] + '.jpg']
                else:
                    pass
                cmds = []
                for name in newTrackRoot:
                    cmd = ["/home/ollie/bin/ogg-cover-art.sh",whereExtract + artwork[artOpt],outdir + name + '.ogg']
                    sp.call(cmd)
                break                
            else:
                continue
        else: #This else belongs to the for loop, i.e. if reach end of loop w/out match 
            print "No artwork corresponding to that option, aborting."
            sys.exit()
    else:
        print "Adding artwork"
        #If image is a png, convert to jpg (ogg-cover-art.sh only excepts jpg).
        if artwork[0].endswith(".png"):
            sp.call(["convert", whereExtract + artwork[0], whereExtract + artwork[0].split('.')[0] + '.jpg'])
            artwork = [artwork[0].split('.')[0] + '.jpg']
        else:
            pass
        cmds = []
        for name in newTrackRoot:
            cmd = ["/home/ollie/bin/ogg-cover-art.sh",whereExtract + artwork[0],outdir + name + '.ogg']
            sp.call(cmd)    
else:
    print "No artwork found, aborting"
    sys.exit()

#Copy cover art to /home/ollie/Music/ note: only want to copy the cover art used, NOT the others
print "Copying cover art"
if len(artwork) > 1:
    sp.call(["cp",whereExtract + artwork[artOpt], outdir])
else:
    sp.call(["cp",whereExtract + artwork[0], outdir])

#Further things:
#1) interface with MySQL and send all metadata to MySQL table - can then create a nice API-GUI to sit on top of 
#table to display collection (al-la discogs).
#MySQL interface

# <codecell>

#Read in data to connect to MySQL db from non-tracked file
addToMySQL = raw_input("add data to MySQL db? Answer 'Y' to add, any other key to pass: ")
if addToMySQL == 'Y':
    sys.path.insert(0, '/home/ollie/Sound/conversion_scripts/soundconv_secure/')
    import z2foConfig

    db = sql.connect(host=z2foConfig.host, # your host, usually localhost
                     user=z2foConfig.user, # your username
                     passwd=z2foConfig.password, # your password
                     db=z2foConfig.db) # name of the data base

    #Create cursor to execute queries
    cur = db.cursor()

    #Add genre
    #genre = allMeta[0]['GENRE']
    addGenre = "This doesn't work yet, nothing added!"

    #cur.execute(addMetaSQL)
    print addGenre
else:
    pass

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
    doExtractExt = raw_input("Press 'Y' to copy, any other key to pass: ")
    if doExtractExt == 'Y':
        for drive in connectedDrives:
            #Check if flac files already exist on device
            doesExist = []
            for name in newTrackRoot:
                doesExist.append(os.path.isfile(drive + name + '.flac'))
            if any(doesExist) == True:
                print "FLAC files already exist in " + drive + ". Continue with conversion?"
                doConvert = raw_input("Press 'Y' to start conversion, any other key to pass: ")
                if doConvert == 'Y':
                    #Execute
                    print "Copying to " + drive + " this may take a few seconds..."
                    sp.call(["mkdir","-p",drive])
                    sp.call(['cp', '-t', drive] + glob.glob(whereExtract + '*'))
                else:
                    pass
            else:          
                print "Copying to " + drive + " this may take a few seconds..."
                sp.call(["mkdir","-p",drive])
                sp.call(['cp', '-t', drive] + glob.glob(whereExtract + '*'))
    else:
        pass
else:
    print 'No external FLAC archive dirs found. Copy locally to' + localExtDir +'instead?'
    writeLocal = raw_input("Press 'Y' to copy locally, any other key to pass: ")
    if writeLocal == "Y":
        #Check if flac files exist locally
        doesExist = []
        for name in newTrackRoot:
            doesExist.append(os.path.isfile(localExtDir + name + '.flac'))
        if any(doesExist) == True:
            print "FLAC files already exist in " + localExtDir + ". Continue with conversion?"
            doConvert = raw_input("Press 'Y' to start conversion, any other key to pass: ")
            if doConvert == 'Y':
                #Execute
                print 'Copying to ' + localExtDir + ' this may take a few seconds...'
                sp.call(["mkdir","-p",localExtDir])
                sp.call(['cp', '-t', localExtDir] + glob.glob(whereExtract + '*'))
            else:
                pass
        else:
            print 'Copying to ' + localExtDir + ' this may take a few seconds...'
            sp.call(["mkdir","-p",localExtDir])
            sp.call(['cp', '-t', localExtDir] + glob.glob(whereExtract + '*'))
    else:
        pass

#Set Google Drive location for backup of OGG.
googleD = '/home/ollie/Google Drive/Music/' + artistAlNum + '/' + albumAlNum + '/'

#Make backups of lossy files
if connectedDrivesLossy:
    print '\nCopy OGG files to the following locations? '
    for i in connectedDrivesLossy: print i
    print googleD
    doExtractExt = raw_input("Press 'Y' to copy, any other key to pass: ")
    if doExtractExt == 'Y':
        for drive in connectedDrivesLossy:
            #Check if flac files already exist on device
            doesExist = []
            for name in newTrackRoot:
                doesExist.append(os.path.isfile(drive + name + '.ogg'))
            if any(doesExist) == True:
                print "OGG files already exist in " + drive + ". Continue with conversion?"
                doConvert = raw_input("Press 'Y' to start conversion, any other key to pass: ")
                if doConvert == 'Y':
                    #Execute
                    print "Copying to " + drive + " this may take a few seconds..."
                    sp.call(["mkdir","-p",drive])
                    sp.call(['cp', '-t', drive] + glob.glob(outdir + '*'))
                else:
                    pass
            else:         
                print "Copying to " + drive + " this may take a few seconds..."
                sp.call(["mkdir","-p",drive])
                sp.call(['cp', '-t', drive] + glob.glob(outdir + '*'))
        #Google Drive
        doesExist = []
        for name in newTrackRoot:
            doesExist.append(os.path.isfile(googleD + name + '.ogg'))
        if any(doesExist) == True:
            print "OGG files already exist in " + googleD + ". Continue with conversion?"
            doConvert = raw_input("Press 'Y' to start conversion, any other key to pass: ")
            if doConvert == 'Y':
                #Execute
                print 'Copying to ' + googleD + ' this may take a few seconds...'
                sp.call(["mkdir","-p",googleD])
                sp.call(['cp', '-t', googleD] + glob.glob(outdir + '*'))
            else:
                pass
        else:
            print "Copying to " + googleD
            sp.call(["mkdir","-p",googleD])
            sp.call(['cp', '-t', googleD] + glob.glob(outdir + '*'))
    else:
        pass
else:
    print '\nCopy OGG files to Google Drive?'
    print 'Drive location: ' + googleD
    doExtractExt = raw_input("Press 'Y' to copy, any other key to pass: ")
    if doExtractExt == 'Y':
        doesExist = []
        for name in newTrackRoot:
            doesExist.append(os.path.isfile(googleD + name + '.ogg'))
        if any(doesExist) == True:
            print "OGG files already exist in " + googleD + ". Continue with conversion?"
            doConvert = raw_input("Press 'Y' to start conversion, any other key to pass: ")
            if doConvert == 'Y':
                #Execute
                print 'Copying to ' + googleD + ' this may take a few seconds...'
                sp.call(["mkdir","-p",googleD])
                sp.call(['cp', '-t', googleD] + glob.glob(outdir + '*'))
            else:
                pass
        else:
            print "Copying to " + googleD        
            sp.call(["mkdir","-p",googleD])
            sp.call(['cp', '-t', googleD] + glob.glob(outdir + '*'))
    else:
        pass

# <codecell>

#At this point, we have extracted all of the metadata and so can delete the extracted files from /tmp/
print "deleting temporary files from" + whereExtract

for filename in zippedFiles:
    cmd = ["rm","-f",whereExtract + filename]
    sp.call(cmd)

deleteZip = raw_input("""Would you like to delete the original Zip file?\n
Note: if you paid for it, might want to keep it!\nAnswer 'Y' to delete, any other key to keep: """)

if deleteZip == 'Y':
    sp.call(["rm", "-rf", zipFname])
    print "Original zip file deleted"
else:
    pass

print "Finished"

