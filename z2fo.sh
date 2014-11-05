#!/bin/bash

#Set default directories for file extraction
#paramters=""

#If no arguements are set, issue some short help and info about function
if [[ $# -eq 0 ]]
    then
    cat << EOF
=====================================================================
z2fo - Command-line tool for unzipping audio zips version 0.0

This program is free software, you can redistribute it and/or
modify it under the terms of the CC BY-NC-SA license. 
=====================================================================

To unzip, move audio to archive/compress, convert lossless to lossy:
   z2fo INPUTFILE OUTLOSSLESS OUTLOSSY

Here INPUTFILE must be the path to a zip file - can only handle one
zip at a time. OUTLOSSLESS is the destination for the extracted 
FLACs. OUTLOSSY is the destination for the compressed OGGs.
EOF
exit 0
fi

#Check number of parameters given - if more than one param given will exit
#(if zero params, will print message above).
if [ "$#" -ne 1 ]; then
    echo "Function only takes 1 parameter, $# given. Aborting."
    exit 0
fi

#If variable set, test to see if file actually exists
if [[ ! -f "${1}" ]] ; then
    echo "File ${1} does not exist, aborting."
    exit 0
fi

#Exit if file is not a zip.
if [[ ${1} != *.zip ]]; then
    echo "File ${1} is not a zip, aborting."
    exit 0
fi

#Get list of all FLAC files
contentFlac=$(unzip -Z1 "${1}" | grep '.flac$')

#Get list of all potential artwork files
contentArtwork=$(unzip -Z1 "${1}" | grep '.png$\|.jpg$\|.gif$\|.svg$')

#Get list of all other files found
contentOther=$(unzip -Z1 "${1}" | grep -v '.flac$\|.png$\|.jpg$\|.gif$\|.svg$')

#Exit if no FLAC files found
if [ -z "$contentFlac" ]; then
    echo "This zip contains no FLAC files, aborting"
    exit 0
fi

cat << EOF
The following FLAC files were found:
${contentFlac}
The following artwork files were found:
${contentArtwork}
EOF

if [ -z "$contentOther" ]
then
    cat << EOF
No other files were found
EOF
else
    cat << EOF
The following files were also found:
${contentOther}
EOF
fi

#Extracting files of a certain type only:
#unzip Downloaded_Zips/David\ Ezra\ Brown\ -\ David\ Ezra\ Brown.zip *.jpg -d hello

#So let's try just extracting the first file to get the metadata 
#(maybe try and do this within a pipe).
#Get first match
firstFlac=$(unzip -Z1 "${1}" | grep -m 1 '.flac$')

echo "${firstFlac}"

#Unzip first file locally to extract metadata (should be quick)
unzip "${1}" "${firstFlac}" 
metaflac --list --block-type=VORBIS_COMMENT "${firstFlac}"

#Use sed to get artist and album, from which we can construct outpath.
#echo "FLAC files will be extracted to"
