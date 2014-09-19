#!/bin/bash

#Takes a .wav file as input and converts to a .flac and a .ogg.
#Also takes input of metadata - currently this is specified in
#this script, but should also be able to add this from a file.
#Would be good to allow lookup of metadata from online database
#e.g. CDDB  - only thing is CDDB works only by matching CD data
#and not file data - need to find something that does this.
#Also, this script works on a full release basis rather than a
#track-by-track basis, so could just specify Artist and Album
#and this should be enough to do an online lookup of all other
#relevant data (e.g. track titles, genre etc). Should also add
#an option to check database manually and override if necessary.

#Specifications#############################################################
quality=-1 #Ranges from -1 (lowest) to 10 (highest). Even -1 is good quality w/ a bitrate ~40kb/s.
#Metadata

artist=""
album=""
date=""
genre=""

tracks=(""
        ""
	""
       )

tracksClean=(${tracks[@]//[^[:alnum:]-]/_})

AlnumArtist=${artist//[^[:alnum:]-]/_}
AlnumAlbum=${album//[^[:alnum:]-]/_}

picture="/home/ollie/old_m4a/${AlnumArtist}/${AlnumAlbum}/${AlnumAlbum}.jpg"
inputPath="/home/ollie/Sound/uncompressed/${AlnumArtist}/${AlnumAlbum}/"

FlacHome="/home/ollie/Sound/compressed_lossless/${AlnumArtist}/${AlnumAlbum}/"
mkdir -p ${FlacHome}

OggHome="/home/ollie/Music/${AlnumArtist}/${AlnumAlbum}/"
mkdir -p ${OggHome}

#MAIN LOOP##############################
for (( i=0; i<=$((${#tracksClean[@]}-1)); i++ ))
do
#Convert to flac format
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

echo "FINISHED"

