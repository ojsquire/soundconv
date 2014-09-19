#Specifications#############################################################
quality=-1 #Ranges from -1 (lowest) to 10 (highest). Even -1 is good quality w/ a bitrate ~40kb/s.
#Metadata

artist="Boards Of Canada"
album="Music Has The Right To Children"
date="1998"
genre="Ambient"

tracks=("Wildlife Analysis"
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

