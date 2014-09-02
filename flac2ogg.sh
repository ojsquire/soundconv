#!/bin/bash
#This script re-tags flacs based on contents of meta.sh then converts flac to ogg.

quality=-1 #Quality ranging from -1 (lowest, smallest) to 9 (highest, largest) of ogg from flac.

#Read in metadata #here $1 is the path/to/file/dir/
. ${1}/meta.sh

AlnumArtist=${artist//[^[:alnum:]-]/_}
AlnumAlbum=${album//[^[:alnum:]-]/_}

FlacHome=${1}
OggHome="/home/ollie/Music/${AlnumArtist}/${AlnumAlbum}/"
mkdir -p ${OggHome}

#Number of tracks on album
ntracks=$(ls ${FlacHome}*.flac -1 | wc -l)

#Loop over all tracks in album
for (( i=0; i<=$((${ntracks}-1)); i++ ))
do
index1=$(printf "%02d" $((i+1)))
FlacName=$(ls ${FlacHome}${index1}*)
#metaflac --show-tag=TITLE ${FlacName} > out.txt
#title=$(sed -n 's/TITLE=//p' out.txt)

#it is possible flac can have id3 tags - need to remove these for conversion to ogg to work.
id3v2 --delete-all ${FlacName} 

metaflac --remove-all-tags ${FlacName} #remove all vorbis comment tags
metaflac --set-tag=ARTIST="${artist}" ${FlacName}
metaflac --set-tag=ALBUM="${album}" ${FlacName}
metaflac --set-tag=GENRE="${genre}" ${FlacName}
metaflac --set-tag=DATE="${year}" ${FlacName}
metaflac --set-tag=TITLE="${title[${i}]}" ${FlacName}
metaflac --set-tag=TRACKNUMBER=$((i+1)) ${FlacName}

metaflac --remove --block-type=PICTURE ${FlacName} #remove picture
metaflac --import-picture-from=${FlacHome}${AlnumAlbum}.jpg ${FlacName} #set new picture

#CONVERT TO .OGG
titleAlNum=${title[${i}]//[^[:alnum:]-]/_}
OggName="${index1}_${titleAlNum}.ogg"     
#Export picture from flac METADATA_BLOCK_PICTURE to jpeg
echo "Exporting picture from flac METADATA_BLOCK_PICTURE to jpeg"
metaflac --export-picture-to=${OggHome}${AlnumAlbum}.jpg ${FlacName}
#Encode to flac - automatically copies all meta tags except picture
echo "Encoding from flac to ogg"
oggenc -q ${quality} -o ${OggHome}${OggName} ${FlacName}
#Embed picture extracted from flac.
echo "Embedding jpg picture into ogg"
~/bin/ogg-cover-art.sh ${OggHome}${AlnumAlbum}.jpg ${OggHome}${OggName}
done
#End loop

#Copy to Google Drive
echo "Copying to Google Drive"
mkdir -p /home/ollie/Google\ Drive/Music/${AlnumArtist}/${AlnumAlbum}
cp ${OggHome}* /home/ollie/Google\ Drive/Music/${AlnumArtist}/${AlnumAlbum}

echo "FINISHED"

