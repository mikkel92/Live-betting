import matplotlib.pyplot as plt
import numpy as np
from data_loader import *
import sys

def plot_match_data(match_data):

	time = [float(i["time"][0].replace(':','')) for i in match_data]
	attacks_home = [i["stats"]["attacks"][0] for i in match_data]
	attacks_away = [i["stats"]["attacks"][1] for i in match_data]
	
	plt.plot(time,attacks_home,'.',label="home")
	plt.plot(time,attacks_away,'.',label="away")
	plt.xlabel("time [wierd unit]")
	plt.xlim(0,max(time) + 200)
	plt.ylabel("attacks")
	plt.legend()
	plt.grid()
	plt.show(block=False)
	raw_input('...')

	plt.close_all()

def get_day_succes(day_data):

	enough_data = [0,0,0,0,0]
	bins = np.linspace(0,9000,16)
	
	
	for count, match_data in enumerate(day_data):
		match_times = []
		for times in match_data:
			
			#print times["time"][0], str('45:00')
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
		#print np.histogram(match_times,bins=bins)[0]
	#print enough_data, len(day_data)
	return np.array(enough_data) / float(len(day_data))
	
	
def plot_scrape_succes(year,month):

	
	days = range(1,32)
	
	month_hist = [[],[],[],[],[]]
	for day in days:

		print "loading day %i" %day
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
	plot_scrape_succes(year='2018',month='9')






