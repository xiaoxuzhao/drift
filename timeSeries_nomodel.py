'''
draw temp change of one specific turtle data and model data.
'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime, timedelta
import netCDF4
from turtleModule import str2list, str2ndlist, np_datetime, bottom_value, closest_num, dist
import watertempModule as wtm   # A module of classes that using ROMS, FVCOM.
def getModTemp(modTempAll, obsTime, obsLayer, obsNearestIndex, starttime, oceantime):
    '''
    Return the mod temp corresponding to observation based on layers, not depth
    '''
    ind = closest_num((starttime -datetime(2013,5,18)).total_seconds()/3600, oceantime)
    modTemp = []
    l = len(obsLayer.index)
    for i in obsLayer.index:
        print(i, l)
        timeIndex = closest_num((obsTime[i]-datetime(2013,5,18)).total_seconds()/3600, oceantime)-ind
        modTempTime = modTempAll[timeIndex]
        # modTempTime[modTempTime.mask] = 10000
        t = [modTempTime[obsLayer[i][j],obsNearestIndex[i][0], obsNearestIndex[i][1]] \
             for j in range(len(obsLayer[i]))]
        modTemp.append(t)
    modTemp = np.array(modTemp)
    return modTemp
def smooth(v, e):
    '''
    Smooth the data, get rid of data that changes too much.
    '''
    for i in range(2, len(v)-1):
        a, b, c = v[i-1], v[i], v[i+1]
        diff1 = abs(b - c) #diff1 is not used
        diff2 = abs(b - a)
        if diff2>e:
            v[i] = a
    return v
#########################################################
obsData = pd.read_csv('ctdWithModTempByDepth.csv', index_col=0)
tf_index = np.where(obsData['TF'].notnull())[0]
obsData = obsData.ix[tf_index]
id = obsData['PTT'].drop_duplicates().values
#print('turtle id:', id)
tID = id[3]                    # 0~4, 6,7,8,9, turtle ID.
layers = pd.Series(str2ndlist(obsData['modDepthLayer'], bracket=True), index=obsData.index) # If str has '[' and ']', bracket should be True.
modNearestIndex = pd.Series(str2ndlist(obsData['modNearestIndex'].values, bracket=True), index=obsData.index)
obsTemp = pd.Series(str2ndlist(obsData['TEMP_VALS'].values), index=obsData.index)
obsTime = pd.Series(np_datetime(obsData['END_DATE'].values), index=obsData.index)
modTemp = pd.Series(str2ndlist(obsData['modTempByDepth'].values,bracket=True), index=obsData.index)
layers = layers[obsData['PTT']==tID]
modNearestIndex = modNearestIndex[obsData['PTT']==tID]
time = obsTime[obsData['PTT']==tID]
temp = obsTemp[obsData['PTT']==tID]
#modTemp=pd.Series(str2ndlist(obsData['TEMP_VALS'][temp.index],bracket=True), index=temp.index)
'''
starttime, endtime=np.amin(time), np.amax(time)+timedelta(hours=1)
modObj = wtm.waterCTD()
url = modObj.get_url(starttime, endtime)    #something wrong with ROMS website
oceantime = netCDF4.Dataset(url).variables['ocean_time']
modTempAll = netCDF4.Dataset(url).variables['temp']
modTemp = getModTemp(modTempAll, obsTime, layers, modNearestIndex, starttime, oceantime)
modTemp = pd.Series(modTemp, index=temp.index)
'''
obsMaxTemp, obsMinTemp = [], []
modMaxTemp, modMinTemp = [], []
for i in temp.index:  #this loop calculate min & max temperature of each dive
    obsMaxTemp.append(max(temp[i]))
    obsMinTemp.append(min(temp[i]))
    modMaxTemp.append(max(modTemp[i]))
    modMinTemp.append(min(modTemp[i]))
data = pd.DataFrame({'time':time.values, 'obsMaxTemp':obsMaxTemp, 'obsMinTemp':obsMinTemp,
                    'modMaxTemp': modMaxTemp, 'modMinTemp': modMinTemp}, index=range(len(time)))
data = data.sort_index(by='time')

data['obsMinTemp'] = smooth(data['obsMinTemp'].values, 5)
data['modMinTemp'] = smooth(data['modMinTemp'].values, 5)
# data['time'] = smooth(data['time'].values, timedelta(days=20))
'''
for i in range(1, len(data['obsMinTemp'])):
    obsMin = data['obsMinTemp'][i]
    obsMax = data['obsMaxTemp'][i]
    modMin = data['modMinTemp'][i]
    modMax = data['modMaxTemp'][i]
    if obsMin==obsMax:
        data['obsMinTemp'][i]=data['obsMaxTemp'][i-1]
    if modMin==modMax:
        data['modMinTemp'][i]=data['modMaxTemp'][i-1]
'''
Date=[]
for i in data.index:
    Date.append(data['time'][i])
fig = plt.figure()
ax = fig.add_subplot(111)
plt.plot(Date, data['obsMaxTemp'], color='b', linewidth=2,label='max')
plt.plot(Date, data['obsMinTemp'],'--', color='b', linewidth=2, label='min')
#ax.plot(Date, data['modMaxTemp'], color='r', linewidth=2)
#ax.plot(Date, data['modMinTemp'], color='r', linewidth=2, label='modeled')
plt.legend()
plt.xlabel('Time(2013)', fontsize=14)
plt.ylabel('Temperature(degc)', fontsize=14)

dates = mpl.dates.drange(np.amin(time), np.max(time), timedelta(days=30))
dateFmt = mpl.dates.DateFormatter('%b')
ax.set_xticks(dates)
ax.xaxis.set_major_formatter(dateFmt)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.title('Time series of temp for turtle:{0}'.format(tID), fontsize=14)
plt.savefig('timeSeries.png', dpi=200)
plt.show()
'''
fig = plt.figure()
ax2 = fig.add_subplot(212)
for i in temp.index:
    # ax2.plot(([time[i]+timedelta(hours=5)])*len(temp[i]), temp[i],color='b')
    ax2.plot([time[i]]*len(temp[i]), modTemp[i], color='r')
ax2.set_xlabel('Time', fontsize=20)
ax2.set_ylabel('Temperature', fontsize=20)
dates = mpl.dates.drange(np.amin(time), np.max(time), timedelta(days=30))
dateFmt = mpl.dates.DateFormatter('%b,%Y')
ax2.set_xticks(dates)
ax2.xaxis.set_major_formatter(dateFmt)
ax2.set_title('Model', fontsize=20)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)


ax1 = fig.add_subplot(211)
for i in temp.index:
    ax1.plot([time[i]]*len(temp[i]), temp[i], color='b')
ax1.set_ylabel('Temperature', fontsize=20)
ax1.set_xticks(dates)
ax1.xaxis.set_major_formatter(dateFmt)
ax1.set_title('Observation', fontsize=20)
plt.xticks(fontsize=10)
plt.yticks(fontsize=20)
fig.suptitle('Time series of temp for turtle:{0}'.format(tID), fontsize=25)
ax2.set_yticks(ax1.get_yticks())
plt.show()
'''
