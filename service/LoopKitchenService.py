from service.Connection import session
from datetime import datetime, timedelta, date
import csv
from models.Updates import Update
from models.Timings import Timings
from models.Zones import Zones
from models.Report import Report
from sqlalchemy import update
from dateutil import tz
from uuid import uuid4
import asyncio

def getData():
    with open('Data\store status.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        header=True
        for row in csv_reader:
            if header:
                header=False
            else:
                update = Update(store_id=row[0], status=row[1], timestamp_utc=row[2])
                session.add(update)
                
    with open('Data\Menu hours.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        header=True
        for row in csv_reader:
            if header:
                header=False
            else:
                timing = Timings(store_id=row[0], day=row[1], start=row[2], end=row[3])
                session.add(timing)

    with open('Data\\bq-results-20230125-202210-1674678181880.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        header=True
        for row in csv_reader:
            if header:
                header=False
            else:
                zone = Zones(store_id=row[0], zone=row[1])
                session.add(zone)
    # print('3')
    session.commit()
    return "success"

def getMaxUptime(cycle):
    totalUpTime=timedelta(days=0)
    maxUpTimeWeek=timedelta(days=0)
    maxUpTimeDay=timedelta(days=0)
    maxUpTimeHour=timedelta(hours=0)
    
    for i in range(len(cycle)):
        if(cycle[i][2]=='start'):
            continue
        timeDiff=datetime.combine(date.min, cycle[i][1]) - datetime.combine(date.min, cycle[i-1][1])
        if(timeDiff<timedelta(days=0)):
            timeDiff+=timedelta(days=1)

        totalUpTime+=timeDiff

        if(cycle[i][2]=='week'):
            maxUpTimeWeek=totalUpTime
        elif(cycle[i][2]=='day'):
            maxUpTimeDay=totalUpTime
        elif(cycle[i][2]=='hour'):
            maxUpTimeHour=totalUpTime
    
    # print(totalUpTime, maxUpTimeWeek, maxUpTimeDay, maxUpTimeHour)
    if(maxUpTimeWeek-maxUpTimeDay>timedelta(days=0)):
        maxUpTimeDay=maxUpTimeWeek-maxUpTimeDay
    else:
        maxUpTimeDay=totalUpTime-(maxUpTimeDay-maxUpTimeWeek)

    if(maxUpTimeWeek-maxUpTimeHour>timedelta(days=0)):
        maxUpTimeHour=maxUpTimeWeek-maxUpTimeHour
    else:
        maxUpTimeHour=totalUpTime-(maxUpTimeHour-maxUpTimeWeek)

    return totalUpTime, maxUpTimeDay, maxUpTimeHour

def getRealUptime(cycle):
    upTimeWeek=timedelta(days=0)
    upTimeDay=timedelta(days=0)
    upTimeHour=timedelta(days=0)
    totalUpTime=timedelta(days=0)
    for i in range(len(cycle)):
        timeDiff=datetime.combine(date.min, cycle[i][1]) - datetime.combine(date.min, cycle[i-1][1])
        if(timeDiff<timedelta(days=0)):
            timeDiff+=timedelta(days=1)
        if(cycle[i-1][2]=='active'):
            totalUpTime+=timeDiff
        if(cycle[i-1][2]=='start'):
            if(cycle[i][2]=='active'):
                totalUpTime+=timeDiff
            elif(cycle[i][2]=='inactive'):
                continue
            else:
                if(cycle[(i+1)%len(cycle)]=='active'):
                    totalUpTime+=timeDiff

        if(cycle[i][2]=='week'):
            upTimeWeek=totalUpTime
            cycle[i][2]=cycle[i-1][2]
        if(cycle[i][2]=='day'):
            upTimeDay=totalUpTime
            cycle[i][2]=cycle[i-1][2]
        if(cycle[i][2]=='hour'):
            upTimeHour=totalUpTime
            cycle[i][2]=cycle[i-1][2]

    if(upTimeWeek-upTimeDay>timedelta(days=0)):
        upTimeDay=upTimeWeek-upTimeDay
    else:
        upTimeDay=totalUpTime-(upTimeDay-upTimeWeek)

    if(upTimeWeek-upTimeHour>timedelta(days=0)):
        upTimeHour=upTimeWeek-upTimeHour
    else:
        upTimeHour=totalUpTime-(upTimeHour-upTimeWeek)

    return totalUpTime, upTimeDay, upTimeHour

def insertTimingsToCycle(storeId, lastWeek, lastDay, lastHour, cycle):
    for day in range(0,7):
        time = session.query(Timings).filter_by(store_id=storeId).filter_by(day=day).all()
        if(len(time)==0):
            start=datetime.strptime("00:00:00", '%H:%M:%S').time()
            end=datetime.strptime("23:59:59", '%H:%M:%S').time()
            cycle.append([day,start,'start'])
            cycle.append([day,end,'end'])
            continue
        
        for timing in time:
            start=datetime.strptime(timing.start, '%H:%M:%S').time()
            end=datetime.strptime(timing.end, '%H:%M:%S').time()
            cycle.append([day,start,'start'])
            cycle.append([day,end,'end'])

    cycle.append([lastWeek.weekday(),lastWeek.time(),'week'])
    cycle.append([lastDay.weekday(),lastDay.time(),'day'])
    cycle.append([lastHour.weekday(),lastHour.time(),'hour'])
    cycle.sort()

def insertUpdatedsToCycle(storeId, curr, delta, lastWeek, cycle):
    entries = session.query(Update.timestamp_utc, Update.status).filter_by(store_id=storeId).filter(Update.timestamp_utc>curr-delta).all()
    entries.sort()
    statusWeek='inactive'
    diffWeek = timedelta(days=7)
    
    entriesToRemove=[]

    for entry in entries:
        currDelta = curr-entry[0]
        if(currDelta>timedelta(days=7) and currDelta-timedelta(days=7)<diffWeek):
            diffWeek=currDelta-timedelta(days=7)
            statusWeek=entry[1]

        if(entry[0]<lastWeek):
            entriesToRemove.append(entry)

    for e in entriesToRemove:
        entries.remove(e)

    entries.append([lastWeek-timedelta(microseconds=1),statusWeek])

    storeZone = session.query(Zones.zone).filter_by(store_id=storeId).first()
    if(storeZone==None):
        zone='America/Chicago'
    else:
        zone=storeZone[0]
    
    for entry in entries:
        status=entry[1]
        to_zone=tz.gettz(zone)
        date = entry[0].astimezone(to_zone)
        day = date.weekday()
        time = date.time()
        cycle.append([day,time,status])
    
    cycle.sort()

# async def storeReport(storeId, lastWeek, lastDay, lastHour):
#     pass


def makeReport():
    curr=datetime.now().astimezone(tz.tzlocal())
    delta = timedelta(days=7, hours=2)
    lastWeek=curr-timedelta(days=7)
    lastDay=curr-timedelta(days=1)
    lastHour=curr-timedelta(hours=1)
    stores = session.query(Update.store_id).filter(Update.timestamp_utc>curr-delta).distinct().all()
    reportId=uuid4()
    # print(len(stores))
    for store in stores:
        cycle=[]
        insertTimingsToCycle(store[0], lastWeek, lastDay, lastHour, cycle)
        
        maxUpTimeWeek, maxUpTimeDay, maxUpTimeHour = getMaxUptime(cycle)
        # print(maxUpTimeWeek, maxUpTimeDay, maxUpTimeHour)

        insertUpdatedsToCycle(store[0], curr, delta, lastWeek, cycle)
        
        UpTimeWeek, UpTimeDay, UpTimeHour = getRealUptime(cycle)

        report=Report(report_id=reportId, store_id=store[0],uptime_last_hour=UpTimeHour/timedelta(minutes=1),uptime_last_day=UpTimeDay/timedelta(hours=1),
                      uptime_last_week=UpTimeWeek/timedelta(hours=1),downtime_last_hour=(maxUpTimeHour-UpTimeHour)/timedelta(minutes=1),
                      downtime_last_day=(maxUpTimeDay-UpTimeDay)/timedelta(hours=1),downtime_last_week=(maxUpTimeWeek-UpTimeWeek)/timedelta(hours=1))

        session.add(report)
    session.commit()
    return reportId

def getReport(reportId):
    reportData=session.query(Report).filter_by(report_id=reportId).all()
    if(len(reportData)==0):
        return "ReportId Invalid"
    
    with open('Reports\{}.csv'.format(reportId), 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)

        csv_writer.writerow(["store_id", "uptime_last_hour(in minutes)", "uptime_last_day(in hours)", "uptime_last_week(in hours)",
                             "downtime_last_hour(in minutes)", "downtime_last_day(in hours)", "downtime_last_week(in hours)"])
        for data in reportData:
            csv_writer.writerow([data.store_id,data.uptime_last_hour,data.uptime_last_day,data.uptime_last_week,
                                 data.downtime_last_hour, data.downtime_last_day, data.downtime_last_week])
        
    return "Success"

async def helper(tasks):
  v = await asyncio.gather(*tasks)
  return v