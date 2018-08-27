import numpy as np
from datetime import datetime
import os

def simple_match_eval(match_data):

	time = match_data[0]
	data = match_data[1]
	odds = match_data[2]

	data_weights = [1.,1.,time[0:2] / 50.,20.,10.]
	home_score = 2
	away_score = 2

	next_goal_odds = odds[1]

	lead = 1.5 # Factor of which the leading teams score has to be higher

	if home_score / lead > away_score or away_score / lead > home_score and time > 2500:
		return True
	else: return False

def get_team_momentum():
	return 1

def load_match_data(match_save_name):
	
	time_now = datetime.now()
	data_dir = "%s/%s/%s/%s/" % (os.getcwd(),time_now.year,time_now.month,time_now.day)

	files = os.listdir(data_dir)
	print files
	
	match_data = []
	for file in files:
		if match_save_name in file:
			match_data.append(np.loadtxt(data_dir + file))


if __name__ == '__main__':
	load_match_data('AllAfr')