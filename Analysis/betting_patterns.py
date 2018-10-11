import numpy as np
import os, sys
import json
from machine_learning import *
from sklearn import model_selection
import pickle

script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
file = script_path + "/tmp_month_data.json"
print file
with open(file) as f:
	data = json.load(f)

#json.loads(file.read())
data, results, odds = reagrange_month_data(data=data,match_time=3000,debug=False)
print len(data), len(odds)
#for train_fraction in np.linspace(0.05,0.65,61):
test_size = 0.50
all_data = np.column_stack((data,odds))
X_train, X_test, Y_train, Y_test = model_selection.train_test_split(all_data, results, test_size=test_size)#, random_state=1337)
test_odds = X_test[:,-1] # get the odds rearange in the same way as training data
X_train = np.delete(X_train,-1,1)
X_test = np.delete(X_test,-1,1)

adaboost_learning(training_data=X_train,training_results=Y_train,odds=odds) # dumps a file

loaded_model = pickle.load(open(script_path + '/Adaboost_dump.sav', 'rb'))
print "Approximate model accuracy", loaded_model.score(X_test, Y_test)

boosted_decisions = loaded_model.decision_function(X_test)

succes = []
fails = []
bins = np.linspace(-1,1,21)
#print test_odds[0]


for bdt_cut in np.linspace(0,0.5,11):

	winnings = 0
	bets = 0
	#print bdt_cut
	for match in range(0,len(boosted_decisions)):
		if test_odds[match] == "failed":
			continue

		if float(test_odds[match]["home next goal"][0]) < 2.0:
			continue

		if Y_test[match] == 1:
			if bdt_cut == 0:
				succes.append(boosted_decisions[match])
			if boosted_decisions[match] > bdt_cut:
				#print test_odds[match]
				winnings += float(test_odds[match]["home next goal"][0])
				bets += 1

		if Y_test[match] == 0:
			if bdt_cut == 0:
				
				fails.append(boosted_decisions[match])
			if boosted_decisions[match] > bdt_cut:
				bets += 1.
	
	print "winnings: ", winnings, "bets: ", bets

for safety in bins:
	confusion_matrix = [[0,0],[0,0]]
	for match in range(0,len(Y_test)):
		if boosted_decisions[match] > safety and Y_test[match] == 1:
			confusion_matrix[0][0] += 1
		elif boosted_decisions[match] < safety and Y_test[match] == 0:
			confusion_matrix[0][1] += 1
		elif boosted_decisions[match] < safety and Y_test[match] == 1:
			confusion_matrix[1][0] += 1
		else: 
			confusion_matrix[1][1] += 1 
			

	print confusion_matrix


plt.hist(succes,bins=bins,histtype='step',label='succes',linewidth=2)
plt.hist(fails,bins=bins,histtype='step',label='fail',linewidth=2)
plt.legend()
plt.xlabel("BDT score")
plt.ylabel("Frequency")
plt.show(block=False)
raw_input('...')
	
