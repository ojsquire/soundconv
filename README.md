soundconv
=========

The main routine (in fact only active routine) is z2fo.py. This takes a zip,
checks its contents for FLAC files. If finds them, will rename them according
to a particular pattern, convert them to OGG, and copy both the FLAC and OGG
to various backup locations. 

To add next: 
1. Support for MP3 (detect, transcode down, backup).
2. Storage of metadata in MySQL db (incompletely implemented currently).
3. Full support for compilations.