import matplotlib.pyplot as plt
import numpy as np
from data_loader import *
from analysis_tools import *
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
	
	
def plot_scrape_succes(year,month):
	
	print("loading file...")
	script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
	file = script_path + "/%s_%s_month_data.json" %(year,month)

	with open(file) as f:
		data = json.load(f)

	print("success")

	plotting_data = {
					"matches":[],
					"entire matches":[],
					}

	wierd_teams = 0
	one_data_point = 0
	wierd_score = 0
	

	for day in data:
		# test
		
		try: 
			nr_matches = np.shape(data[day][0])[0]
			plotting_data["matches"].append(nr_matches)
		except:
			plotting_data["matches"].append(0)
			continue

		for match in data[day][0]:
			checked_data = check_match_data(match)
			wierd_teams += checked_data[0]
			one_data_point += checked_data[1]
			wierd_score += checked_data[2]
			

			if np.count_nonzero(check_match_data(match)) == 0:
				
				plotting_data["entire matches"].append(len(match))	
				#print(score[:,1])
				
				#print(len(match))
				#break
			
	print(wierd_teams,wierd_score,one_data_point)
	print(max(plotting_data["entire matches"]))

	"""
	for count,hist in enumerate(month_hist):
		label = "missing data points: %i" % (count)
		plt.hist(hist,histtype='step',bins=np.array(days) - 0.5,label=label,linewidth=2,alpha=0.8)
	"""
	plot_title = "Statistics for web scraping. Nr of matches: %i" %sum(plotting_data["matches"])
	fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(16, 12))
	plt.suptitle(plot_title)

	fig1 = ax1.hist(plotting_data["entire matches"],bins=np.linspace(0,30,30),histtype="step",linewidth=2)
	ax1.set_title("Data points in match")

	fig2 = ax2.plot(plotting_data["matches"],label="matches")
	ax2.set_title("Matches per day")

	ax2.set_xlabel("day")
	ax2.set_xlim(0,32)
	ax2.grid()
	ax2.set_ylabel("count")
	ax2.legend()
		
	save_title = "%s_%s_scrape_validation.png" %(year,month)
	plt.savefig("plots/" + save_title)
	plt.close()



if __name__ == "__main__":
	#plot_match_data(match_data=load_match(match='AliMil',date='2018/9/5'))
	plot_scrape_succes(year='2018',month='10')






