#!/bin/bash

#Takes a .wav file as input and converts to a .flac and a .ogg.
#Also takes input of metadata - currently this is specified in
#this script, but should also be able to add this from a file.
#Would be good to allow lookup of metadata from online database
#e.g. MusicBrainz, or even Discogs (has a free API). Should also
# add an option to check database manually and override if
# necessary.

#Specifications#############################################################
quality=-1 #Ranges from -1 (lowest) to 10 (highest). Even -1 is good quality w/ a bitrate ~40kb/s.
#Metadata

#Read in metadata #here $1 is the path/to/file/dir/
#(can be anywhere, no need for connection w/ location of actual files).
. ${1}meta.sh

# artist=""
# album=""
# date=""
# genre=""

# tracks=(""
#         ""
# 	""
#        )

tracksClean=(${tracks[@]//[^[:alnum:]-]/_})

echo "Tracks are: ${tracksClean[@]}"
echo "Artist is: ${artist}"
echo "Album is: ${album}"

AlnumArtist=${artist//[^[:alnum:]-]/_}
AlnumAlbum=${album//[^[:alnum:]-]/_}

inputPath=${1}

picture="${inputPath}cover.jpg"


FlacHome="/home/ollie/Sound/compressed_lossless/${AlnumArtist}/${AlnumAlbum}/"
mkdir -p ${FlacHome}

OggHome="/home/ollie/Music/${AlnumArtist}/${AlnumAlbum}/"
mkdir -p ${OggHome}

flacBack="/media/ollie/INTENSO/ollie/Sound/compressed_lossless/${AlnumArtist}/${AlnumAlbum}/"
mkdir -p ${flacBack}

#echo "FUCK HERE!"
#MAIN LOOP##############################
for (( i=0; i<=$((${#tracksClean[@]}-1)); i++ ))
do
#Convert to flac format
#echo "HERE!!!!"
title=${tracks[${i}]}
index1=$(printf "%02d" $((i+1)))
echo "Converting $((i+1))/${#tracksClean[@]} ${title} to flac format."
    FileName="${index1}_${tracksClean[i]}"     
#Convert to flac using the flac encoder ("flac").

flac -f --verify -o ${FlacHome}${FileName}.flac --picture ${picture} -T "TRACKNUMBER=$((${i}+1))" -T "TITLE=${title}" -T "ARTIST=${artist}" -T "ALBUM=${album}" -T "DATE=${date}" -T "GENRE=${genre}" ${inputPath}${FileName}.wav

#Convert to ogg-vorbis using oggenc
echo "Converting $((i+1))/${#tracksClean[@]} ${title} to ogg-Vorbis format."
    FileName="${index1}_${tracksClean[i]}"     
oggenc -q ${quality} --tracknum $((${i}+1)) --title "${title}" --artist "${artist}" --album "${album}" --date "${date}" --genre "${genre}" -o ${OggHome}${FileName}.ogg ${inputPath}${FileName}.wav
~/bin/ogg-cover-art.sh ${picture} ${OggHome}${FileName}.ogg #Ogg artwork
done
#END OF LOOP############################

#Copy pic to Ogg dir
cp ${picture} ${OggHome}
#Copy to Google Drive
echo "Copying to Google Drive"
mkdir -p /home/ollie/Google\ Drive/Music/${AlnumArtist}/${AlnumAlbum}
cp ${OggHome}* /home/ollie/Google\ Drive/Music/${AlnumArtist}/${AlnumAlbum}
#Copy flac to external hard drive
echo "Copying flac to external hard drive"
cp ${FlacHome}* ${flacBack}

#Copy metadata file
echo "Copying meta data file"
cp ${1}meta.sh ${FlacHome}
cp ${1}meta.sh ${flacBack}

echo "FINISHED"

