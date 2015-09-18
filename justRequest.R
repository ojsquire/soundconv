#Accept args from cmd line
args <- commandArgs(trailingOnly = TRUE)
narg = length(args)
if(narg==0){
  stop("No arguments given - two needed: 1. Artist, 2. Album")
} else if(narg==1){
  stop("Only one argument given - two needed: 1. Artist, 2. Album")  
} else if(narg>2){
  stop("Greater than two args given -  exactly two required: 1. Artist, 2. Album")
}

#Will get all meta for tracks etc. given an album and an artist
artistIn <- args[1]
albumIn <- args[2]

artistIn <- "Radiohead"
albumIn <- "Amnesiac"

print(paste("Artist = ", artistIn))
print(paste("Album = ", albumIn))

library(RCurl, quietly = T)
library(RJSONIO, quietly = T)

#Token
token <- "AkAeDGIQjISRDcHBbFBbPxIBEfClBZeyyPtDcxLS"

album <- gsub(" ", "+", albumIn)
artist <- gsub(" ", "+", artistIn)

website <- "https://api.discogs.com/database/search"

type <- "master"

request <- paste0(website, "?release_title=", album, "&artist=", artist, "&type=", type ,"&token=", token)

#Note: why do I do "master" THEN "release"?
getFromDiscogs <- function(request){
  result <- getURL(request,
       .opts = list(ssl.verifypeer = FALSE, followlocation=TRUE),
       httpheader = c('User-Agent' = "findMusicPM/1.0"))
  return(result)
}

#Try query
attemptCount=1
print(paste("Attempt",attemptCount))
data.search = try(getFromDiscogs(request), silent=TRUE)
                  
#Repeat query until we don't get an error
while(is(data.search,'try-error')){
  print(paste("Attempt",attemptCount))
  data.search = try(getFromDiscogs(request), silent=TRUE)
}

data.search.clean <- fromJSON(data.search)
 
#Check if search has found anything
#Issue here is that could be a release but no master.
#Way to only query once...?
if(length(data.search.clean$results)<1){
  #Try type = release
  type = "release"
  request <- paste0(website, "?release_title=", album, "&artist=", artist, "&type=", type ,"&token=", token)
  
  data.search <- getURL(request,
                        .opts = list(ssl.verifypeer = FALSE, followlocation=TRUE),
                        httpheader = c('User-Agent' = "findMusicPM/1.0"))
  data.search.clean <- fromJSON(data.search)
  if(length(data.search.clean$results)<1){
    stop(paste0("No results found for artist=\"", args[1],"\" and album=\"",args[2],"\""))
  }
}


#Get master ID
master.id <- data.search.clean$results[[1]]$id
print(master.id)
if(type=="master"){
  master.url <- paste0("https://api.discogs.com/masters/", master.id)
} else{
  master.url <- paste0("https://api.discogs.com/releases/", master.id)
}
#sslversion="SSLVERSION_SSLv3"
data <- getURL(master.url, .opts = list(ssl.verifypeer = FALSE, followlocation=TRUE),
               httpheader = c('User-Agent' = "findMusicPM/1.0"))

data.clean <- fromJSON(data)

#Get artwork

#Artist - keep this as input - multiple artists for same name so may get nos otherwise
#artist <- data.clean$artists[[1]]$name

#Album
album <- data.clean$title

#Year
year <- data.clean$year

#Genre (I will use style as genre as it's more informative)
genre <- data.clean$styles[1]

#Tracks
tracks <- data.clean$tracklist
track.names <- unlist(lapply(1:length(tracks), function(i) tracks[[i]][["title"]]))
track.positions <- unlist(lapply(1:length(tracks), function(i) tracks[[i]][["position"]]))
track.durations <- unlist(lapply(1:length(tracks), function(i) tracks[[i]][["duration"]]))

album.data <- data.frame(number = track.positions, track = track.names, duration = track.durations,
           artist = artist, album = album, year = year, genre = genre)

#Create filenames from track names
track.names.clean <- gsub("[^[:alnum:]]","_", album.data$track)

file.names <- paste(sort(sprintf("%02d", album.data$number)),"_",track.names.clean, ".mp3", sep="")

#Rename files based on new names based on meta
#Read in old names, should automatically be in correct order
print(file.names)
