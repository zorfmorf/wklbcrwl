from __future__ import print_function
import re
import json
import datetime
import csv
import os

output = []
with open('output/output.csv', 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
        output.append(row)

# first simplify datefield to only contain days, we don't care about exact timestamps
for i in range(3, len(output[0])):
    output[0][i] = output[0][i][:10]

# merge entries so we only have one per day. should speed up things in the browser
# and make this thing long term sustainable
i = 3
while i < len(output[0]):
    # find first index of next day
    j = i + 1
    while j < len(output[0]) and output[0][i] == output[0][j]:
        j = j + 1
    # now delete columns i to j - 2 if necessary
    if i < j - 1:
        for _ in range(j - 1 - i):
            for row in output:
                row.pop(i)
    i += 1

# create a table with all active users
dataLength = len(output[0])
active = []
active.append(output[0])
for i in range(1, len(output)):
    row = output[i]
    # ommit users that havent updated for a while
    oldLevel = int(row[len(row) - 70]) # active in the last 60 days
    currentLevel = int(row[-1])
    if currentLevel == 60 or currentLevel > oldLevel:
        print("Taking user " + row[0] + " with level " + str(row[-1]))
        active.append(row)
    else:
        print("Ignoring data for user " + row[0] + " because they stopped updating [ " + str(oldLevel) + " " + row[-1] + " ]")

# write raw data out
with open("output/filteredData.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows(active)

htmlHeader = """
<html>
<head>
  <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
  <script type="text/javascript">
    google.charts.load('current', {'packages':['corechart']});
    google.charts.setOnLoadCallback(drawChart);

    function drawChart() {
      var data = google.visualization.arrayToDataTable([
"""

htmlFooter = """
    ]);

      var options = {
        title: 'Race to Your Goal December 2020',
        selectionMode: 'multiple',
        dataOpacity: 0.0,
        legend: { position: 'right' },
        width: 1024,
        height: 800,
        explorer: { actions: ['dragToZoom', 'rightClickToReset'] },
        vAxis: {
            title: 'Level',
            viewWindow: {
                min: 1,
                max: 60
            }
        },
        hAxis: {
            title: 'Date'
        }
      };

      var chart = new google.visualization.LineChart(document.getElementById('curve_chart'));

      chart.draw(data, options);
    }
  </script>
</head>
<body>
  <p>Updated on <script>document.write(new Date().toISOString().slice(0, 10))</script></p>
  <p> Drag a rectangle to zoom in. Rightclick to zoom out again.</p>
  <div id="curve_chart" style="width: 900px; height: 500px"></div>
</body>
</html>
"""

# try to generate the html file for the active dataset
with open('output/index.html', 'w') as f:
    print(htmlHeader, file=f)
    for j in range(0, len(active[0])):
        if j == 0 or j >= 3: # ignore column goal and starting level
            tstr = "["
            for i in range(0, len(active)):
                if i > 0 and j >= 3:
                    tstr += "," + str(active[i][j])
                else:
                    val = str(active[i][j])
                    if j == 0 and i > 0:
                        tstr += ","
                    tstr += "'" + val + "'"
            tstr += "]"
            if j < len(active[0])-1:
                tstr += ","
            # replace 0s
            tstr = tstr.replace(',0,', ',,')
            tstr = tstr.replace(',0,', ',,')
            tstr = tstr.replace(',0]', ',,]')
            print(tstr, file=f)
    print(htmlFooter, file=f)
