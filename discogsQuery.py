#Queries the discogs database via the API.
#Requires the discogs_client libaray:
#sudo pip install discogs_client

import discogs_client
d = discogs_client.Client('ExampleApplication/0.1')

#For example, get the tracklist for Syro:
d.search('Aphex Twin','Syro')[0].tracklist

#Can now use this as a starting point for the 
#metadata given just the artist and album name.
#May also want to give the version (e.g. 
#vinyl, wav, cd etc.).
