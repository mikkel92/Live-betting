import matplotlib.pyplot as plt
import numpy as np
from data_loader import *
from analysis_tools import spline_data
import sys

def plot_match_data(match_data):

	data_str = "shots on target"
	time = sorted([float(i["time"][0].replace(':','')) for i in match_data])
	data_home = sorted([float(i["stats"][data_str][0]) for i in match_data])
	data_away = sorted([float(i["stats"][data_str][1]) for i in match_data])
	goals_home = sorted([int(i["score"][0]) for i in match_data])
	goals_away = sorted([int(i["score"][1]) for i in match_data])

	# add the data point 0,0
	extra_point = np.array([0.0])
	time = np.concatenate((extra_point,time))
	data_home = np.concatenate((extra_point,data_home))
	data_away = np.concatenate((extra_point,data_away))
	goals_home = np.concatenate((extra_point,goals_home))
	goals_away = np.concatenate((extra_point,goals_away))

	
	for data_point in range(1,len(time)):

		if goals_home[data_point] > goals_home[data_point - 1]:
			plt.vlines(time[data_point],-100,1000,linewidth=2,linestyle='dashed',colors='r')
		if goals_away[data_point] > goals_away[data_point - 1]:
			plt.vlines(time[data_point],-100,1000,linewidth=2,linestyle='dashed',colors='g')
	

	plt.hlines(100,0,32,linewidth=2,linestyle='dashed',colors='k')
	plt.plot(time,data_home,'.',label="home")
	plt.plot(time,data_away,'.',label="away")

	#print(type(time), type(data_home[0]))
	#splined data
	spline_data_home = spline_data(time,data_home)
	spline_data_away = spline_data(time,data_away)

	plt.plot(spline_data_home[0],spline_data_home[1],label="home",c='r')
	plt.plot(spline_data_away[0],spline_data_away[1],label="away",c='g')


	plt.xlabel("time [wierd unit]")
	plt.xlim(-100,max(time) + 200)
	plt.ylabel("attacks")
	plt.ylim(-2,max(np.concatenate((data_home,data_away))))
	plt.legend()
	plt.grid()
	plt.show(block=False)
	raw_input('...')

	

def get_day_succes(day_data):

	enough_data = [0,0,0,0,0]
	bins = np.linspace(0,9000,16)
	
	
	for count, match_data in enumerate(day_data):
		match_times = []
		for times in match_data:
			
			#print(times["time"][0], str('45:00'))
			#break
			if times["time"][0] == str('45:00'):
				continue

			elif len(times["time"][0]) > 1:
				match_times.append(float(times["time"][0].replace(':','')))
			
			else: match_times.append(1)
		
		if np.count_nonzero(np.histogram(match_times,bins=bins)[0]) >= len(bins) - 1:
			enough_data[0] += 1
		if np.count_nonzero(np.histogram(match_times,bins=bins)[0]) >= len(bins) - 2:
			enough_data[1] += 1
		if np.count_nonzero(np.histogram(match_times,bins=bins)[0]) >= len(bins) - 3:
			enough_data[2] += 1
		if np.count_nonzero(np.histogram(match_times,bins=bins)[0]) >= len(bins) - 4:
			enough_data[3] += 1
		if np.count_nonzero(np.histogram(match_times,bins=bins)[0]) >= len(bins) - 5:
			enough_data[4] += 1
		#print(np.histogram(match_times,bins=bins)[0])
	#print(enough_data, len(day_data))
	return np.array(enough_data) / float(len(day_data))
	
	
def plot_scrape_succes(year,month): # TODO change to use the load month function

	
	days = range(1,32)
	
	month_hist = [[],[],[],[],[]]
	for day in days:

		print("loading day %i" %day)
		day_str = "%s/%s/%s" %(year,month,day)

		try:
			day_succes = get_day_succes(day_data=load_one_day(date=day_str))
			for tests in range(0,len(day_succes)):

				for percent in range(0,int(day_succes[tests] * 100)):
					month_hist[tests].append(day)
		except:
			for tests in range(0,len(month_hist)):
				month_hist[tests].append(0)
	for count,hist in enumerate(month_hist):
		label = "missing data points: %i" % (count)
		plt.hist(hist,histtype='step',bins=np.array(days) - 0.5,label=label,linewidth=2,alpha=0.8)
	plt.hlines(100,0,32,linewidth=2,linestyle='dashed',colors='k')
	plt.xlabel("day")
	plt.xlim(0,32)
	plt.ylabel("succes rate [%]")
	plt.legend()
		
	plt.show(block=False)
	raw_input('...')



if __name__ == "__main__":
	plot_match_data(match_data=load_match(match='AliMil',date='2018/9/5'))
	#plot_scrape_succes(year='2018',month='9')






