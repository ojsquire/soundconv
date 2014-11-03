#!/bin/bash

#z2fo (zip2flac+ogg)
#OJS - 03/11/2014
#This script takes a zip dir containing FLAC files (usually an image file too),
#unzips it, moves the FLACs to archive (external hard-disk), converts them to
#compressed format (.ogg), and makes copies of the .oggs on Google Drive.

#Set default parameters
zipPath="/home/ollie/Sound/Downloaded_Zips"
artist=""
album=""
set -- "${1:-zipPath}" "${2:-'default 2'}" "${3:-'default 3'}"

${parameter:-word}
