import numpy as np
from scipy import interpolate
import sys

def spline_data(time_array,data_array):

	# values where the spline is evaluated
	time_new = np.linspace(0,10000,21)
	
	# arange data in chronological order
	time = np.array(time_array)
	data = np.array(data_array)
	time = np.append(time, [15000.])
	data = np.append(data, [data[-1]])


	#tck = interpolate.splrep(time, data)
	#spline_vals = interpolate.splev(time_new, tck)
	tck = interpolate.PchipInterpolator(time, data)
	spline_vals = tck(time_new)

	return time_new, spline_vals

def step_spline(time_array,data_array):

	# values where the spline is evaluated
	time_new = np.linspace(0,10000,21)
	
	# arange data in chronological order
	time = np.array(time_array)
	data = np.array(data_array)

	run = True
	i_d = 1
	while run == True:
		
		try: a = data[i_d]
		except:
			run = False
			continue

		if data[i_d - 1] != data[i_d]:
			data = np.insert(data, i_d, data[i_d - 1])
			time = np.insert(time, i_d, time[i_d] - 0.1)
			i_d += 1
		
		i_d += 1

	time = np.append(time, [15000.])
	data = np.append(data, [data[-1]])

	tck = interpolate.PchipInterpolator(time, data)
	spline_vals = tck(time_new)

	#import matplotlib.pyplot as plt
	#plt.plot(time_new,spline_vals)
	#plt.plot(time,data)
	#plt.show()

	return time_new, spline_vals

def next_goal_spline(goal_times_home,goal_times_away):

	# values where the spline is evaluated
	time_new = np.linspace(0,10000,21)
	next_goal_data = []
	
	# arange data in chronological order
	goals_home = np.append(np.array(goal_times_home),15000.)
	goals_away = np.append(np.array(goal_times_away),15000.)

	for i_t in range(0,len(time_new)):
		next_home = max([i for i in (time_new[i_t] - goals_home) if i < 0])
		next_away = max([i for i in (time_new[i_t] - goals_away) if i < 0])

		if next_home > next_away:
			next_goal_data.append(0)
		elif next_home == next_away and next_home == min(time_new[i_t] - goals_home):
			next_goal_data.append(1)
		elif next_home < next_away:
			next_goal_data.append(2)
		else:
			next_goal_data.append(np.inf)
	
	return time_new, next_goal_data


def check_match_data(match_data):

	wierd_teams = 0
	one_data_point = 0
	wierd_score = 0
	

	teams = ([i["teams"] for i in match_data])

	# check that the match only contains two teams, otherwise the data comes from multiple matches
	if len(np.unique(teams)) != 2:
		
		wierd_teams += 1
		return wierd_teams, one_data_point, wierd_score

	score = sorted([[float('0' + i["time"][0].replace(':','')),float(i["score"][0]),float(i["score"][1])] for i in match_data])
	
	# check that the match has more than one data point
	if len(score) <= 1:
		one_data_point += 1
		return wierd_teams, one_data_point, wierd_score

	# check that the scores in the match are rising
	for i_s in range(1,len(score)):
		if score[i_s - 1][1] > score[i_s][1] or score[i_s - 1][2] > score[i_s][2]:
			#print(score)
			wierd_score += 1
			return wierd_teams, one_data_point, wierd_score

	return wierd_teams, one_data_point, wierd_score
		