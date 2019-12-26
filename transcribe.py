from __future__ import print_function
import re
import json
import datetime
import csv
import numpy as np
import pandas as pd
import os

# custom search function that returns the row for an item
# we use this to find the corresponding row for a user
def find(l, elem):
    for row, i in enumerate(l):
        try:
            column = i.index(elem)
        except ValueError:
            continue
        return row # no exception -> value was found in current row
    return -1

highestIndex = 0

# blacklist for changes that fucked the whole leaderboard
blacklist = [ 836, 837, 838, 839, 840 ]

for r, d, f in os.walk("raw/"):
    for file in f:
        if '.json' in file:
            num = file.replace(".json", "")
            if int(num) > highestIndex:
                highestIndex = int(num)

print("Creating plot for " + str(highestIndex) + " files")
output = [['Name', 'Goal', 'Starting Level']]
for i in range(2, highestIndex + 1):
    if i not in blacklist:
        with open('raw/' + str(i) + '.json') as json_file:
            
            # read data from json first
            data = json.load(json_file)
            output[0].append(data['created_at'])
            dateobj = datetime.datetime.strptime(data['created_at'][:13], '%Y-%m-%dT%H')
            info = data['body_changes']['side_by_side_markdown'].encode("utf-8")
            info = info.replace('</ins>','')
            info = info.replace('<ins>','')
            info = info.replace('</del>','')
            info = info.replace('<del>','')
            info = info.replace('?', '0') # circumvent weird matching issues with questionmarks as speed
            
            # match all user level ups based on this fancy matching regex
            matches = re.findall(r"\?|([\w-]*)\|(..)\|joined at ?: *(\d\d?) ?\| ?speed.*?\| ?level: *(\d\d?)", info)
            matched = []
            
            # go through all matches and write these to data
            for match in matches:
                
                # extract match data
                name = match[0].encode('utf-8')
                goal = match[1].encode('utf-8')
                startLevel = match[2].encode('utf-8')
                currentLevel = match[3].encode('utf-8')
                
                # if the level is not set correctly, something went wrong
                if len(currentLevel) == 0:
                    print("###########FUCK###############    " + name)
                    print(match)
                    print(info)
                else:
                    if name in matched:
                        # we matched this already, so only update the level
                        # and only if it's higher than the one we currently have
                        # This is necessary, because if this name was edited 
                        # this i, it appears twice in matches (old and new level)
                        index = find(output, name)
                        if output[index][-1] < currentLevel:
                            output[index][-1] = currentLevel
                    else:
                        matched.append(name)
                        
                        # new match for this i, so first check if its new
                        index = find(output, name)
                        if index == -1:
                            # new user, so we create data for this guy
                            print("User " + name + " joined on " + str(i))
                            output.append([name, goal, startLevel])
                            index = len(output) - 1 # index of new entry is last item in the list
                        
                        # now append a bunch of zeros if the data list is too small.
                        # necessary for users that joined later (so nearly all of them)
                        # also catches cases where users left and rejoined the 
                        # race (so a bunch of values are missing for them)
                        while len(output[index]) < len(output[0]) - 1:
                            output[index].append(0)
                        output[index].append(currentLevel)


    else:
        print("Omitting " + str(i) + " because it's blacklisted")

# delete all players that have removed themselves from the list
ind = 1
while ind < len(output):
    # missing updates or no valid level? -> out of the race
    if len(output[ind]) < len(output[0]) or output[ind][-1] < 1:
        print("Removing " + output[ind][0] + " from data because they deleted themselves")
        output.pop(ind)
    else:
        ind += 1

# write raw data out
with open("output/output.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows(output)

