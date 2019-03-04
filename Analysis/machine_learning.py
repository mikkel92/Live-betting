import numpy as np
import os, sys
import json
import traceback
from plotting_tools import *
from analysis_tools import *
from data_loader import *

def get_relevant_data(match_data):
	
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
	
	# return the bin content of data for the match aranged in times steps
	has_data = np.histogram(time,bins=np.linspace(0,9000,19))[0]

	# get the home and away data at different times
	
	for keys in data_entries:
		if keys == "possession": continue
		if keys == "yellow cards": continue
		if keys == "red cards": continue
		if keys == "corners": continue
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
	home_score = [i[1] for i in score]
	away_score = [i[2] for i in score]
	#print(score)

	try:
		score_home_spline = step_spline(spline_time,home_score)
		score_away_spline = step_spline(spline_time,away_score)
	except:
		print( home_score)
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

	# add zero point for splining, if first point is not t=0
	for row in range(0,len(data_home)):
		if time[0] > 0.:
			data_home[row].insert(0,0.0)
			data_away[row].insert(0,0.0)

	#array for all splines
	splines = []

	splines.append(score_home_spline[1])
	splines.append(score_away_spline[1])
	for row in range(0,len(data_home)):
		home_spline = spline_data(spline_time,data_home[row])
		away_spline = spline_data(spline_time,data_away[row])			
		splines.append(home_spline[1])
		splines.append(away_spline[1])


	for i_time in range(1,len(splines[0])):
		for i_spline in range(0,len(splines)):
		
			ML_data.append(splines[i_spline][i_time])

	return ML_data, has_data

	
	# spline the data

	#get odds sorted after time
	

	#plot_match_data(match_data[0])

def reagrange_month_data(data,debug=False):
	
	matches = 0

	fails = []
	training = []
	data_points = []

	for day in data:
		# test
		
		try: 
			nr_matches = np.shape(data[day][0])[0]
		except:
			continue

		for match in data[day][0]:
			matches += 1
			#try:
			match_data = get_relevant_data(match_data=match)
			
			if match_data is None:
				fails.append(matches)
				match_data = [np.full(2,np.inf)]

			if np.isfinite(match_data[0]).all() : # check that data is not Nan or inf
				training.append(match_data[0])
				data_points.append(match_data[1])

			else: 
				fails.append(matches)
				match_data = [np.full(2,np.inf)]
				data_points.append(np.inf)
				training.append(match_data)
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
		
	#print("number of matches in dataset: ", matches)
	#print("matches with incomplete or bad data: ", len(fails))

	return training, data_points, fails

def get_month_bet_info(data,match_time,debug=False,bet_type="next goal"):

	matches = 0

	fails = []
	results = []
	odds = []

	for day in data:
		# test
		
		try: 
			nr_matches = np.shape(data[day][0])[0]
		except:
			continue

		for match in data[day][0]:
			matches += 1
			

			# check for empty match data
			if match == []:
				fails.append(matches)
				bet_data = [np.full(len(odds[-1]),np.inf),np.inf]#np.full(len(results[-1]),np.inf)]
			
			else:
				if bet_type == "asian":
					bet_data = betting_type(match_data=match,match_time=match_time).asian_line()
				elif bet_type == "next goal":
					bet_data = betting_type(match_data=match,match_time=match_time).next_goal()
			
			if matches == 1:
				print(bet_data)
			if bet_data is None:
				
				fails.append(matches)
				if bet_type == "asian":
					bet_data = [np.full(2,np.inf),np.inf]#np.full(len(results[-1]),np.inf)]
				elif bet_type == "next goal":
					bet_data = [np.full(3,np.inf),np.inf]#np.full(len(results[-1]),np.inf)]
				

			odds.append(bet_data[0])
			results.append(bet_data[1])
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
		
	#print("number of matches in dataset: ", matches)
	#print("matches that couldn't be used for this betting type: ", len(fails))

	return results, odds, fails

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

def XGBoost_learning(training_data,training_results,test_data,test_results,max_depth=3):

	import xgboost as xgb
	import pickle

	reg = xgb.XGBClassifier(max_depth=max_depth,learning_rate=0.05,n_estimators=200,objective='binary:logistic',seed=42)

	reg.fit(training_data,training_results,
			eval_set=[(training_data,training_results),(test_data,test_results)],
			verbose=10,early_stopping_rounds=50)

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
		
		self.time = time
		self.match_time = match_time
		self.score = score
		self.time_index = time_index
		self.odds = odds

	def next_goal(self):

		#if bet_type == "next goal":
			#print(odds_next_goal)

		# return if the closest odds data point is more than 5 minutes away
		if abs(self.time[self.time_index] - self.match_time) > 500:
			return 

		# get the time at which different teams score
		score_time_home = []
		score_time_away = []
		
		# Get a vector with information of who scores next throughout the match
		for i_time in range(1,len(self.score)):
			# don't use matches where goals are not aranged in time order. These could be half time fuck ups or discarded goals
			if self.score[i_time][1] != self.score[i_time - 1][1] and self.score[i_time][1] < self.score[i_time - 1][1]:
				return
			if self.score[i_time][2] != self.score[i_time - 1][2] and self.score[i_time][2] < self.score[i_time - 1][2]:
				return

			if self.score[i_time][1] != self.score[i_time - 1][1]:# and self.score[i_time][2] == self.score[i_time - 1][2]: 
				for i_goals in range(0,int(abs(self.score[i_time][1] - self.score[i_time - 1][1]))): 
					score_time_home.append(self.score[i_time][0])
			if self.score[i_time][2] != self.score[i_time - 1][2]:# self.score[i_time][1] == self.score[i_time - 1][1] and self.score[i_time][2] != self.score[i_time - 1][2]:	
				for i_goals in range(0,int(abs(self.score[i_time][2] - self.score[i_time - 1][2]))): 
					score_time_away.append(self.score[i_time][0])
		
		next_goal_odds = []
		
		next_goal_bet =  next_goal_spline(score_time_home,score_time_away)[1]

		#print(all_odds)


		for i_o in range(0,len(self.odds)):

			found_odds = False			
			next_goal = len(np.unique(np.where(np.concatenate((score_time_away,score_time_home)) <= self.odds[i_o][0]))) + 1
			search_str = "%i. m\\u00e5l" % next_goal

			for odds_type in self.odds[i_o][1]:

				if str(search_str) == str(odds_type[0]):
					found_odds = True
					try: 
						odds = [self.odds[i_o][0], float(odds_type[2]), float(odds_type[4]), float(odds_type[6])]
						next_goal_odds.append(odds)

					except: 
						try:
							#print("exception1!")
							odds = [self.odds[i_o][0], next_goal_odds[-1][1], next_goal_odds[-1][2], next_goal_odds[-1][3]]
							#print(odds)
							next_goal_odds.append(odds)
							continue
						except:
							#print("exception1!")
							return
			
			if found_odds == False:
				try:	
					#print("exception2!")
					odds = [self.odds[i_o][0], next_goal_odds[-1][1], next_goal_odds[-1][2], next_goal_odds[-1][3]]
					#print(odds)
					next_goal_odds.append(odds)
					continue
				except:
					#print("exception2!")
					return

		try:
			next_goal_odds = np.stack(next_goal_odds)
		except: return
		try:
			odds_home_spline = step_spline(self.time,next_goal_odds[:,1])
			odds_nogoal_spline = step_spline(self.time,next_goal_odds[:,2])
			odds_away_spline = step_spline(self.time,next_goal_odds[:,3])
			odds_splines = [odds_home_spline[1], odds_nogoal_spline[1], odds_away_spline[1]]
	
		except:
			return
			"""
			[print(a) for a in self.odds]
			[print(a[0]) for a in self.odds]
			
			print(len(self.odds))
			print("\n", self.time)
			print(next_goal_odds)
			print(self.score)
			print(search_str)
			raise Exception
			"""

		return odds_splines, next_goal_bet

	def asian_line(self):
		print("Check asian_line function in machine_learning.py before using it: Needs to be updated. Stopping script....")
		sys.exit()
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

















