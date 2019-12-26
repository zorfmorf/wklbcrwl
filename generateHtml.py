from __future__ import print_function
import re
import json
import datetime
import csv
import numpy as np
import pandas as pd
import os

output = []
with open('output/output.csv', 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
        output.append(row)

# TODO:
# merge entries so we only have one per day. should speed up things in the browser
# and make this thing long term sustainable

# create a table with all active users
dataLength = len(output[0])
active = []
active.append(output[0])
for i in range(1, len(output)-1):
    row = output[i]
    # ommit users that havent updated for a while
    oldLevel = row[len(row) - 200] # update date calculation once data merging has been implemented
    if row[-1] > oldLevel:
        print("Taking user " + row[0] + " with level " + str(row[-1]))
        active.append(row)
    else:
        print("Ignoring data for user " + row[0] + " because they stopped updating")

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
        curveType: 'function',
        selectionMode: 'multiple',
        dataOpacity: 0.0,
        legend: { position: 'right' },
        width: 1024,
        height: 1024
      };

      var chart = new google.visualization.LineChart(document.getElementById('curve_chart'));

      chart.draw(data, options);
    }
  </script>
</head>
<body>
  <div id="curve_chart" style="width: 900px; height: 500px"></div>
</body>
</html>
"""

# try to generate the html file for the active dataset
with open('output/plot.html', 'w') as f:
    print(htmlHeader, file=f)
    for j in range(0, len(active[0])-1):
        if j == 0 or j >= 3:
            tstr = "["
            for i in range(0, len(active)-1):
                if i > 0 and j >= 3:
                    tstr += "," + str(active[i][j])
                else:
                    val = str(active[i][j])
                    if len(val) > 10:
                        val = val[:10]
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
