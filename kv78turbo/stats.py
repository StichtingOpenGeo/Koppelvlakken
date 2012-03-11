import os
from pylab import *
import matplotlib as mpl
import matplotlib.pyplot as plt
import datetime as dt

files = os.listdir('/tmp/KV8')

aggr = {}

for filename in files:
    filename = float(filename)
    thisbin = int(filename - (filename % 60))
    if thisbin not in aggr:
        aggr[thisbin] = 1
    else:
        aggr[thisbin] += 1

t = arange(min(aggr.keys()), max(aggr.keys()), 60)
y = []
for x in t:
    if x in aggr:
        y.append(aggr[x])
    else:
        y.append(0)

fig = plt.figure(num=1, figsize=(10, 5))
ax = fig.add_subplot(111)
date_1 = dt.datetime.fromtimestamp(min(aggr.keys()))
date_2 = dt.datetime.fromtimestamp(max(aggr.keys()))
delta = dt.timedelta(seconds=60)
dates = mpl.dates.drange(date_1, date_2, delta)

ax.plot_date(dates, y, fmt='b', linestyle='-', linewidth=1.0);
dateFmt = mpl.dates.DateFormatter('%H:%S')
ax.xaxis.set_major_formatter(dateFmt)
hoursLoc = mpl.dates.HourLocator()
ax.xaxis.set_major_locator(hoursLoc)
#ax.set_xlim(min(aggr.keys()), max(aggr.keys()))
fig.autofmt_xdate(bottom=0.18)
plt.title('Inkomende KV78turbo berichten per minuut')

fig.savefig('/home/projects/openov/htdocs/stats.svg')
