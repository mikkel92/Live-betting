import numpy as np
import os, sys
import json
import traceback
from plotting_tools import *
from analysis_tools import *
from data_loader import *

def get_relevant_data(match_data,match_time):
	
	# perform basic checks on data before using it
	if np.count_nonzero(check_match_data(match_data)) != 0:
		return

	# get entries in statistics list	
	data_entries = match_data[0]["stats"].keys()
	
	# get match times for scraped data
	data_home = []
	data_away = []
	time = sorted([float('0' + i["time"][0].replace(':','')) for i in match_data])
	score = sorted([[float('0' + i["time"][0].replace(':','')),float(i["score"][0]),float(i["score"][1])] for i in match_data])
	
	# get number of data points in match earlier than the time of bet
	used_times = [i for i in time if i < match_time] # data points where time < match_time
	# define how many datapoints there should be at least
	if len(used_times) < int(match_time/700.):
		return

	# get the data point closest to the match_time
	time_distance = [abs(match_time - i) for i in time]
	time_index = time_distance.index(min(time_distance))

	# get the home and away data at different times
	
	for keys in data_entries:
		if keys == "possession": continue
		#if keys != "shots on target": continue # Used for faster testing
		data_home.append(sorted([float(i["stats"][keys][0]) for i in match_data]))
		data_away.append(sorted([float(i["stats"][keys][1]) for i in match_data]))
	

	# Many matches don't have possession stat
	"""
	# possession cant be arange from lower to higher number as the other stats, but has to be sorted in time
	possession = sorted([[float(i["time"][0].replace(':','')),float(i["stats"]["possession"][0]),float(i["stats"]["possession"][1])] for i in match_data])
	data_home.append([i[1] for i in possession])
	data_away.append([i[2] for i in possession])
	"""

	# add extra point for splining if first point is not at 0.0
	if time[0] > 0.:
		score.insert(0,[0.0, 0.0, 0.0])

	# arange the score in a step spline
	spline_time = [i[0] for i in score]
	home_score = [i[0:2] for i in score]
	away_score = [[i[0],i[2]] for i in score]
	for i_s in range(0,len(score) - 1):
		if score[i_s][1] > score[i_s + 1][1] or score[i_s][2] > score[i_s + 1][2]:
			return
		if home_score[i_s][1] != home_score[i_s + 1][1]:
			home_score[i_s][0] = home_score[i_s + 1][0] - 0.01
		if away_score[i_s][1] != away_score[i_s + 1][1]:
			away_score[i_s][0] = away_score[i_s + 1][0] - 0.01

	home_time = [i[0] for i in home_score]
	home_score = [i[1] for i in home_score]
	away_time = [i[0] for i in away_score]
	away_score = [i[1] for i in away_score]
	try:
		score_home_spline = spline_data(home_time,home_score)
		score_away_spline = spline_data(away_time,away_score)
	except:
		print(home_time, home_score)
		sys.exit()
	"""
	plt.scatter(home_time,home_score,s=20,alpha= 0.7)
	plt.plot(score_home_spline[0],score_home_spline[1])
	plt.scatter(away_time,away_score,s=20,alpha= 0.7)
	plt.plot(score_away_spline[0],score_away_spline[1])
	plt.grid()
	plt.show(block=False)
	raw_input('...')
	plt.close()
	sys.exit()
	"""
	# array for the features
	ML_data = []

	# spline the data, making all data points trained on correspond to the same time in a match
	for row in range(0,len(data_home)):
		if time[0] > 0.:
			data_home[row].insert(0,0.0)
			data_away[row].insert(0,0.0)
		home_spline = spline_data(spline_time,data_home[row])
		away_spline = spline_data(spline_time,data_away[row])
		
		for i_time in range(0,len(home_spline[0])):
			# only train on data that is available at that time in matches
			if home_spline[0][i_time] > match_time: break
			#if row == 0: # only append score once
				#ML_data.append(score_home_spline[1][i_time])
				#ML_data.append(score_away_spline[1][i_time])
			ML_data.append(home_spline[1][i_time])
			ML_data.append(away_spline[1][i_time])

	# print(ML_data)

	return ML_data

	
	# spline the data

	#get odds sorted after time
	

	#plot_match_data(match_data[0])

def reagrange_month_data(data,match_time,debug=False,bet_type="next goal"):
	matches, fails = 0,0

	training = []
	results = []
	odds = []
	plotting_data = []

	for day in data:
		# test
		
		try: 
			nr_matches = np.shape(data[day][0])[0]
		except:
			continue

		for match in data[day][0]:
			matches += 1
			#try:
			match_data = get_relevant_data(match_data=match,match_time=match_time)
			if match_data is None:
				fails += 1
				continue

			#print(type(match_data))
			if bet_type == "asian":
				bet_data = betting_type(match_data=match,match_time=match_time).asian_line()
			elif bet_type == "next goal":
				bet_data = betting_type(match_data=match,match_time=match_time).next_goal()
			
			if bet_data is None:
				fails += 1
				continue

			if np.isfinite(match_data[0]).all() : # check that data is not Nan or inf

				odds.append(bet_data[0])
				results.append(bet_data[1])
				training.append(match_data)
			else: fails += 1
			"""	
			except Exception as err:
				fails += 1
				if debug:
					print(match_data)
					print(bet_data[0], bet_data[1])
					print(err)
					#traceback.print_exc()
					sys.exit()
			"""
		

	print("number of matches in dataset: ", matches)
	print("matches that couldn't be used for this betting type: ", fails)
	# Still uses matches with incomplete data: TODO sort
	return training, results, odds#, plotting_data


def adaboost_learning(training_data,training_results,odds):

	from sklearn.ensemble import AdaBoostRegressor
	from sklearn.ensemble import AdaBoostClassifier
	from sklearn.tree import DecisionTreeRegressor
	from sklearn.tree import DecisionTreeClassifier
	from sklearn.grid_search import GridSearchCV
	import pickle
	# Initiate the AdaBoostClassifier
	

	reg = AdaBoostClassifier(DecisionTreeClassifier(max_depth=4), n_estimators=30, learning_rate=0.5, 
	                         algorithm='SAMME', random_state=1)    
	#reg = XGBClassifier(DecisionTreeClassifier(max_depth=4)) 
	"""
	parameters = { 'base_estimator' : [DecisionTreeClassifier(max_depth=1),
					DecisionTreeClassifier(max_depth=2),DecisionTreeClassifier(max_depth=3),
					DecisionTreeClassifier(max_depth=4),DecisionTreeClassifier(max_depth=5)],
					'n_estimators' : [10,20,30],
					'learning_rate' : [0.1,0.5,1.0,2.0]
					}
	print("grid search")
	grid_search = GridSearchCV(reg, param_grid=parameters)
	grid_search.fit(train_data, train_results) # train on the training sample
	print(grid_search.best_estimator_)
	boosted_decisions = grid_search.decision_function(test_data)
	"""

	reg.fit(training_data, training_results) # train on the training sample
	#print("Feature importance: \n", reg.feature_importances_)
	filename = os.path.dirname(os.path.realpath(sys.argv[0])) + '/Adaboost_dump.sav'
	pickle.dump(reg, open(filename, 'wb'))

def XGBoost_learning(training_data,training_results,test_data,test_results,odds,max_depth=3):

	import xgboost as xgb
	import pickle

	reg = xgb.XGBClassifier(max_depth=max_depth,learning_rate=0.05,n_estimators=200,objective='binary:logistic',seed=42)

	reg.fit(training_data,training_results,
			eval_set=[(training_data,training_results),(test_data,test_results)],
			verbose=False,early_stopping_rounds=50)

	#print("Feature importance: \n", reg.feature_importances_)

	filename = os.path.dirname(os.path.realpath(sys.argv[0])) + '/XGBoost_dump.sav'
	pickle.dump(reg, open(filename, 'wb'))

class betting_type():

	def __init__(self, match_data, match_time):
		"""
		score: array with n entries containing [time, goals_home, goals_away] in that order
		
		time_index: the index of the datapoint in the match, which is closest to that of the live match

		odds: array where all of the odds were saved when scraped
		"""
		time = sorted([float('0' + i["time"][0].replace(':','')) for i in match_data])
		time_distance = [abs(match_time - i) for i in time]
		time_index = time_distance.index(min(time_distance))

		score = sorted([[float('0' + i["time"][0].replace(':','')),float(i["score"][0]),float(i["score"][1])] for i in match_data])
		odds = sorted([[float('0' + i["time"][0].replace(':','')),(i["extra odds"])] for i in match_data])
		
		self.match_time = match_time
		self.score = score
		self.time_index = time_index
		self.odds = odds

	def next_goal(self):

		#if bet_type == "next goal":
			#print(odds_next_goal)

		# get the time at which different teams score
		score_time_home = []
		score_time_away = []
		for i_time in range(1,len(self.score)):
			if self.score[i_time][1] != self.score[i_time - 1][1] and self.score[i_time][2] == self.score[i_time - 1][2]: 
				score_time_home.append(self.score[i_time][0])
			elif self.score[i_time][1] == self.score[i_time - 1][1] and self.score[i_time][2] != self.score[i_time - 1][2]:	
				score_time_away.append(self.score[i_time][0])
			else: continue

		bet_next_goal_home = 0

		# get next score from match time:
		goals_home = np.array(score_time_home) - self.match_time
		goals_away = np.array(score_time_away) - self.match_time
		next_goals = [0,0]

		try: 
			next_goals[0] = min(goals_home[goals_home >= 0])
		except: next_goals[0] = np.inf
		try: 
			next_goals[1] = min(goals_away[goals_away >= 0])
		except: next_goals[1] = np.inf

		# return None maybe, when it is unknown who scored next goal
		if next_goals[0] == next_goals[1] and next_goals[0] == np.inf:
			bet_next_goal_home = 1
		elif next_goals[0] == min(next_goals):
			bet_next_goal_home = 0
		elif next_goals[0] == next_goals[1]:
			return
		else: 
			bet_next_goal_home = 2


		all_odds = self.odds[self.time_index]
		next_goal = int(self.score[self.time_index][1] + self.score[self.time_index][2] + 1)

		for odds_type in all_odds[1]:
			search_str = "%i. m\\u00e5l" % next_goal

			if str(search_str) == str(odds_type[0]):
				try: 
					odds = [float(odds_type[2]), float(odds_type[4]), float(odds_type[6])]
					#time[time_index]
					
					return odds, bet_next_goal_home

				except: return 

		return 

	def asian_line(self):

		# get current score and end result of match
		current_goals_home = self.score[self.time_index][1]
		current_goals_away = self.score[self.time_index][2]
		end_score_home = self.score[-1][1]
		end_score_away = self.score[-1][2]

		bet_asian = 0

		if end_score_home - current_goals_home > end_score_away - current_goals_away:
			bet_asian = 0
		if end_score_home - current_goals_home == end_score_away - current_goals_away:
			bet_asian = 1
		if end_score_home - current_goals_home < end_score_away - current_goals_away:
			bet_asian = 2


		all_odds = self.odds[self.time_index]
		next_goal = int(self.score[self.time_index][1] + self.score[self.time_index][2] + 1)

		for odds_type in all_odds[1]:
			search_str = "Asian handicap"

			if str(search_str) == str(odds_type[0])[0:14]:

				both_odds = []
				for count, bets in enumerate(odds_type):
					if bets == "0.0":
						both_odds.append(odds_type[count + 1])

				try: 
					odds = {
							"home asian line":[float(both_odds[0])],
							"away asian line":[float(both_odds[1])]
							}
					
					return odds, bet_asian

				except: return 

		return 


	



if __name__ == "__main__":

	file = os.path.dirname(os.path.realpath(sys.argv[0])) + "/tmp_month_data.json"
	print(file)
	with open(file) as f:
		data = json.load(f)
	
	#json.loads(file.read())
	data, results, odds = reagrange_month_data(data=data,match_time=3000,debug=False)
	adaboost_learning(data,results,odds)

















