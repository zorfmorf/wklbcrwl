import re
import json
import datetime
import csv
import numpy as np
import pandas as pd

output = [['Name', 'Goal', 'Starting Level']]

def find(l, elem):
    for row, i in enumerate(l):
        try:
            column = i.index(elem)
        except ValueError:
            continue
        return row, column
    return -1

for i in range(2, 833):
    with open('raw/' + str(i) + '.json') as json_file:
        data = json.load(json_file)
        #print('Name: ' + data['username'])
        output[0].append(data['created_at'])
        dateobj = datetime.datetime.strptime(data['created_at'][:13], '%Y-%m-%dT%H')
        #print(dateobj)
        info = data['body_changes']['side_by_side_markdown'].encode("utf-8")
        info = info.replace('</ins>','')
        info = info.replace('<ins>','')
        #print(info)
        matches = re.findall(r"\|(\w*)\|(..)\|joined at: *(\d\d?)\|speed.*?days\|level: *(\d\d?)", info)
        matched = []
        for match in matches:
            name = match[0].encode('utf-8')
            goal = match[1].encode('utf-8')
            startLevel = int(match[2].encode('utf-8'))
            currentLevel = int(match[3].encode('utf-8'))
            if name not in matched: # only match every name once
                matched.append(name)
                #print(match[0] + match[1] + match[2] + match[3])
                index = find(output, name)
                if index == -1:
                    print("User " + name + " joined on " + str(i))
                    newList = [name, goal, startLevel]
                    while len(newList) < i + 1:
                        newList.append(0)

                    output.append(newList)

                if index == -1:
                    index = find(output, name)
                #print(output)
                #print(index)
                #output[index][0] = name
                #output[index][1] = goal
                #output[index][2] = startLevel
                output[index[0]].append(currentLevel)

# delete all players that have removed themselves from the list
ind = 1
while ind < len(output):
    if len(output[ind]) < len(output[0]):
        print("Removing " + output[ind][0] + " from data because they deleted themselves")
        output.pop(ind)
    else:
        ind += 1

# create table for level 10 and below
dataLength = len(output[0])
lowlevel = []
highlevel = []
lowlevel.append(output[0])
highlevel.append(output[0])
for i in range(1, len(output)-1):
    row = output[i]
    if len(row) == dataLength:
        # ommit users that havent updated for a while
        oldLevel = row[len(row) - 100]
        if oldLevel <= 2 or row[-1] > oldLevel:
            print("Taking user " + row[0] + " with level " + str(row[-1]))
            if row[-1] > 10:
                highlevel.append(row)
            else:
                lowlevel.append(row)
        print("Ignoring data for user " + row[0] + " because they stopped updating")
    else:
        print("Ignoring data for user " + row[0] + " because they left the race")

with open("lowlevel.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows(lowlevel)

with open("highlevel.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows(highlevel)

with open("alldata.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows(output)


# try to generate the html file
