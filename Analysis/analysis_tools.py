import numpy as np
from scipy import interpolate

def spline_data(time_array,data_array):

	# values where the spline is evaluated
	time_new = np.linspace(0,10000,21)
	
	# arange data in chronological order
	time = np.array(time_array)
	data = np.array(data_array)

	#tck = interpolate.splrep(time, data)
	#spline_vals = interpolate.splev(time_new, tck)
	tck = interpolate.PchipInterpolator(time, data)
	spline_vals = tck(time_new)

	#print(time_new, spline_vals)
	return time_new, spline_vals

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
		