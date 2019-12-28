#!/bin/bash

# wanikani upstream url for the race to level 60
URL="https://community.wanikani.com/posts/1085304/revisions/"

# file name suffix
SUFFIX=".json"

# target folder to save the files
TARGET="raw"

# index of the first json file (2.json) that we know exists on wanikani upstream
i=2

# first skip all files that have been downloaded already
while test -f "$TARGET/$i$SUFFIX";
do
  i=$[$i+1]
done

echo "$i is the first missing file"

# now download files until we get a 404 response code
wget_output=$(wget -q "$URL$i$SUFFIX" -P "$TARGET/")
while [ $? -eq 0 ];
do
  i=$[$i+1]
  wget_output=$(wget -q "$URL$i$SUFFIX" -P "$TARGET/")
done

echo "Downloaded files until ${i}$SUFFIX"
