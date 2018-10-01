import numpy as np
import os, sys
import json
from sklearn.ensemble import AdaBoostRegressor
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeRegressor
from sklearn.tree import DecisionTreeClassifier
from sklearn.grid_search import GridSearchCV
from data_loader import *

def get_match_data(match_data):
	

	data_entries = match_data[0][0]["stats"].keys()
	print data_entries
	time = sorted([float(i["time"][0].replace(':','')) for i in match_data])
	for keys in data_entries:
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

def reagrange_training_data(data,match_time):

	master_array = []
	for day in data:
		for match in data[day]:
			data = get_match_data(match)
			break
				






def adaboost_training():
	# Initiate the AdaBoostClassifier
	reg = AdaBoostClassifier(DecisionTreeClassifier(max_depth=5), n_estimators=50, learning_rate=1.0, 
	                         algorithm='SAMME')    

	reg.fit(train_matches[0], train_outcome_h) # train on the training sample
	print reg.feature_importances_
	boosted_decisions = reg.decision_function(decide_matches)



if __name__ == "__main__":
	file = os.path.dirname(os.path.realpath(sys.argv[0])) + "/tmp_month_data.json"
	print file
	with open(file) as f:
		data = json.load(f)
	
	#json.loads(file.read())
	reagrange_training_data(data=data,match_time=4000)
	




