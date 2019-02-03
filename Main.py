from datetime import datetime, date

import psycopg2 as psycopg2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from numpy.matlib import rand

connection = psycopg2.connect(host="10.114.22.30",database="callcenter", user="postgres", password="123")
cur = connection.cursor()
cur.execute(" select count(*), datetime::date as date from callcenter.cards "
    "where id in (select cardid from callcenter.cardsufferers) "
    "and description similar to '%(обмороз|обморож|отмор)%' "
    "and datetime between '2016-1-1'::timestamp::date and '2019-1-1'::timestamp::date "
    "group by date order by date")

#cur.execute("select datetime::date as date, count(*) from callcenter.cards where id in "
#            "(select cardid from callcenter.cardfires) and description similar to '%(трав|куст)%' "
#            "group by date order by date")

dates = []
counts = []

for row in cur:
    dates.append(row[1])
    counts.append(row[0])
datesTemp = []
minTemp = []
maxTemp = []
chillblaines = []
cur.execute("select weather.date, min(temperature), max(temperature), max(cardsCounter) from callcenter.weather "
    "left join (select datetime::date as date, count(1) as cardsCounter from callcenter.cards "
    "where id in (select cardid from callcenter.cardsufferers) "
    "and  description similar to '%(обмороз|обморож|отмор)%' group by date) as cards "
    "on cards.date=weather.date "
    "where weather.date between '2016-11-1'::timestamp::date and '2019-1-1'::timestamp::date "
    "group by weather.date order by weather.date")
for row in cur:
    datesTemp.append(row[0])
    minTemp.append(float(row[1]))
    maxTemp.append(float(row[2]))
    chillblaines.append(int(row[3] or 0))

df = pd.DataFrame(np.column_stack([datesTemp, minTemp, maxTemp]), columns=['date', 'max', 'min'])
ax = df.plot(kind = 'bar', stacked=True)
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=range(1,13), bymonthday=1, interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
ax.figure.show()

plt.plot(dates, counts, 'b-')
plt.plot(x = datesTemp, y = maxTemp, kind='bar')
plt.show()

