from __future__ import print_function
import re
import json
import datetime
import csv
import numpy as np
import pandas as pd
import os

def find(l, elem):
    for row, i in enumerate(l):
        try:
            column = i.index(elem)
        except ValueError:
            continue
        return row, column
    return -1

highestIndex = 0
for r, d, f in os.walk("raw/"):
    for file in f:
        if '.json' in file:
            num = file.replace(".json", "")
            if int(num) > highestIndex:
                highestIndex = int(num)

print("Creating plot for " + str(highestIndex) + " files")
output = [['Name', 'Goal', 'Starting Level']]
for i in range(2, highestIndex):
    with open('raw/' + str(i) + '.json') as json_file:
        data = json.load(json_file)
        #print('Name: ' + data['username'])
        output[0].append(data['created_at'])
        dateobj = datetime.datetime.strptime(data['created_at'][:13], '%Y-%m-%dT%H')
        #print(dateobj)
        info = data['body_changes']['side_by_side_markdown'].encode("utf-8")
        info = info.replace('</ins>','')
        info = info.replace('<ins>','')
        info = info.replace('</del>','')
        info = info.replace('<del>','')
        info = info.replace('?', '0') # circumvent weird matching issues with questionmarks as speed
        #if i == 832:
        #    print(info)
        matches = re.findall(r"\?|([\w-]*)\|(..)\|joined at ?: *(\d\d?) ?\| ?speed.*?\| ?level: *(\d\d?)", info)
        matched = []
        for match in matches:
            name = match[0].encode('utf-8')
            goal = match[1].encode('utf-8')
            startLevel = match[2].encode('utf-8')
            currentLevel = match[3].encode('utf-8')
            if len(currentLevel) == 0:
                print("###########FUCK###############    " + name)
                print(match)
                print(info)
            else:
                if name not in matched:  # only match every name once
                    matched.append(name)
                    index = find(output, name)
                    if index == -1:
                        print("User " + name + " joined on " + str(i))
                        newList = [name, goal, startLevel]
                        while len(newList) < len(output[0]) - 1:
                            newList.append(0)
                        output.append(newList)
                        index = [ len(output)-1 ]
                    output[index[0]].append(currentLevel)
                else:
                    index = find(output, name)
                    if output[index[0]][3] < currentLevel:
                        output[index[0]][3] = currentLevel


# delete all players that have removed themselves from the list
ind = 1
while ind < len(output):
    if len(output[ind]) < len(output[0]):
        print("Removing " + output[ind][0] + " from data because they deleted themselves")
        output.pop(ind)
    else:
        ind += 1

# write raw data out
with open("output.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows(output)
