#Queries the discogs database via the API.
#Requires the discogs_client libaray:
#sudo pip install discogs_client
from subprocess import call
import discogs_client
d = discogs_client.Client('ExampleApplication/0.1')

#For example, get the tracklist for Syro:
#tracks = d.search('Aphex Twin','Syro')[0].tracklist

#Can now use this as a starting point for the 
#metadata given just the artist and album name.
#May also want to give the version (e.g. 
#vinyl, wav, cd etc.).

#As a function
def getMeta(artist, album):
    # artist = input('artist name:')
    # album = input('album name:')
    tracks = d.search(artist, album)[0].tracklist
    return(tracks)

tracks = getMeta(artist="Aphex Twin", album="Syro")
#To run this from the command line:
#python -c 'import discogsQuery; print discogsQuery.getMeta(artist="Aphex Twin", album="Syro")'

#Note: look in models.py for all the attributes of the discogs_client.model class
#To get just the titles of the ith track it's:
#track[i].title
#the track number is:
#track[i].position

for track in range(0,len(tracks)):
    print tracks[track].title

#Try to avoid writing the titles out - want to do everything WITHIN this one script if poss.

#Next: call up the sound files.

# call(["ls", "-l"])

# flac -f --verify -o ${FlacHome}${FileName}.flac --picture ${picture} -T "TRACKNUMBER=$((${i}+1))" -T "TITLE=${title}" -T "ARTIST=${artist}" -T "ALBUM=${album}" -T "DATE=${date}" -T "GENRE=${genre}" ${inputPath}${FileName}.wav

# #Is this actually gonna work???
# call(["flac", "-f", "--verify", "-o ${FlacHome}${FileName}.flac", "--picture ${picture}", "-T 'TRACKNUMBER=$((${i}+1))'", "-T 'TITLE=${title}'", "-T 'ARTIST=${artist}'", "-T 'ALBUM=${album}'", "-T 'DATE=${date}'", "-T 'GENRE=${genre}'", "${inputPath}${FileName}.wav"])

# call(["flac", "-f", "--verify", "-o /home/ollie/Sound/test1.flac", "-T 'TRACKNUMBER=1'", "-T 'TITLE=hello'", "-T 'ARTIST=AFX'", "-T 'ALBUM=AnalO 3'", "-T 'DATE=2005'", "-T 'GENRE=Acid'", "/home/ollie/Sound/uncompressed/Daft_Punk/Random_Access_Memories/01_Give_Life_Back_To_Music.wav"])

#"/home/ollie/Sound/compressed_lossless/AFX/Analord_03/02_Midievil_Rave.flac"


# f = open('myfile','w')
# f.write('hi there\n') # python will convert \n to os.linesep
# f.close() # you can omit in most cases as the destructor will call if

# flac -f --verify -o /home/ollie/Sound/test1.flac -T 'TRACKNUMBER=1' -T 'TITLE=hello' -T 'ARTIST=AFX' -T 'ALBUM=AnalO 3' -T 'DATE=2005' -T 'GENRE=Acid' /home/ollie/Sound/uncompressed/Daft_Punk/Random_Access_Memories/01_Give_Life_Back_To_Music.wav

call(["flac", "-f", "--verify", "-o /home/ollie/Sound/test1.flac", "-T 'TRACKNUMBER=1'", "-T 'TITLE=hello'", "-T 'ARTIST=AFX'", "-T 'ALBUM=AnalO 3'", "-T 'DATE=2005'", "-T 'GENRE=Acid'", /home/ollie/Sound/uncompressed/Daft_Punk/Random_Access_Memories/01_Give_Life_Back_To_Music.wav])
