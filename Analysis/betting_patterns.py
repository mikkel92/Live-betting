import numpy as np
import os, sys
import json
from machine_learning import *
from sklearn import model_selection
import pickle

def next_goal_eval(bdt_cut,boosted_decisions,eval_results,eval_odds,bet_limit):
	
	#boosted_decisions = boosted_decisions[:,0]

	succes = []
	fails = []
	"""
	for match in range(0,len(boosted_decisions)):
		if eval_results[match] == 1:
			succes.append(boosted_decisions[match])
		else:
			fails.append(boosted_decisions[match])
	"""
	winnings = 0
	bets = 0
	#print bdt_cut
	for match in range(0,len(boosted_decisions)):

		max_decision = np.where(boosted_decisions[match] == max(boosted_decisions[match]))[0][0]
		
		if eval_odds[match] == "failed":
			continue
		
		if eval_odds[match][max_decision] < bet_limit:
			continue

		if max(boosted_decisions[match]) < bdt_cut:
			continue

		if eval_results[match] == max_decision:
			succes.append(boosted_decisions[match])
			winnings += float(eval_odds[match][max_decision])
			bets += 1.
			#if boosted_decisions[match]
		else:
			fails.append(boosted_decisions[match])
			bets += 1.

		if winnings == "home vs all": # TODO make a one vs all type
			print "WTF"
			if eval_results[match] == 0 and boosted_decisions[match][0] > bdt_cut:
				#print eval_odds[match]
				winnings += float(eval_odds[match][0])
				bets += 1

			if eval_results[match] == 0 and boosted_decisions[match][0] > bdt_cut:
				bets += 1.
				

	return  succes, fails, winnings, bets

def asian_line_eval(bdt_cut,boosted_decisions,eval_results,eval_odds,bet_limit):
			
	succes = []
	fails = []

	winnings = 0
	bets = 0
	#print bdt_cut
	for match in range(0,len(boosted_decisions)):
		if eval_odds[match] == "failed":
			continue

		if max(boosted_decisions[match]) < bdt_cut:
			continue

		if boosted_decisions[match][0] > bdt_cut and boosted_decisions[match][0] == max(boosted_decisions[match]):
			if float(eval_odds[match]["home asian line"][0]) < bet_limit:
				continue
			bets += 1
			if  eval_results[match] == 0:
				succes.append(max(boosted_decisions[match]))
				winnings += float(eval_odds[match]["home asian line"][0])
			else:
				fails.append(max(boosted_decisions[match]))

		elif eval_results[match] == 1 and boosted_decisions[match][1] > bdt_cut and boosted_decisions[match][1] == max(boosted_decisions[match]):
			winnings += 0
			bets += 0

		elif boosted_decisions[match][2] == max(boosted_decisions[match]) and boosted_decisions[match][2] > bdt_cut:
			if float(eval_odds[match]["away asian line"][0]) < bet_limit:
				continue
			bets += 1
			if eval_results[match] == 2:
				succes.append(max(boosted_decisions[match]))
				winnings += float(eval_odds[match]["away asian line"][0])
			else:
				fails.append(max(boosted_decisions[match]))

		else:
			continue

	return  succes, fails, winnings, bets



match_time = 3000
bet_limit = 2.0
random_states = 10
#bet_type = "asian"
bet_type = "next goal"


# Load the data
script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
file1 = script_path + "/2018_9_month_data.json"
file2 = script_path + "/2018_10_month_data.json"
with open(file1) as f:
	train_data = json.load(f)

with open(file2) as f:
	eval_data = json.load(f)

for match_time in np.linspace(2000,9000,15):

	bdt_bins = [round(i,2) for i in np.linspace(0.3,0.8,26)]
	test_size_bins = [round(i,2) for i in np.linspace(0.05,0.50,10)]
	bets_array = np.zeros([len(bdt_bins),len(test_size_bins)])
	winnings_array = np.zeros([len(bdt_bins),len(test_size_bins)])
	model_acc_array = []

	# Rearange data for machine learning
	data1, results1, odds1 = reagrange_month_data(data=train_data,match_time=match_time,debug=False,bet_type=bet_type)
	data2, results2, odds2 = reagrange_month_data(data=eval_data,match_time=match_time,debug=False,bet_type=bet_type)
	all_data = np.concatenate((data1,data2))
	all_results = np.concatenate((results1,results2))
	all_odds = np.concatenate((odds1,odds2))
	all_data = np.column_stack((all_data,all_odds))
	for i_size, test_size in enumerate(test_size_bins):

		model_acc = 0
		for i_rand in range(0,random_states): # loop over random states

			
			X_data, X_valid, Y_data, Y_valid = model_selection.train_test_split(all_data, all_results, test_size=0.4,random_state=i_rand)
			X_train, X_test, Y_train, Y_test = model_selection.train_test_split(X_data, Y_data, test_size=test_size,random_state=i_rand)
 			
 			n_features = len(X_data[0])
 			train_odds = X_data[:,-3:]
			eval_odds = X_valid[:,-3:] # get the odds rearange in the same way as training data
			#X_train = np.delete(X_train,[n_features,n_features-1,n_features-2],axis=1)
			#X_test = np.delete(X_test,[n_features,n_features-1,n_features-2],axis=1)
			#X_valid = np.delete(X_valid,[n_features,n_features-1,n_features-2],axis=1)

			evaluation_data = X_valid
			eval_results = Y_valid

			for max_depth in [3]:
				XGBoost_learning(training_data=X_train,training_results=Y_train
					,test_data=X_test,test_results=Y_test,odds=odds1,max_depth=max_depth)

				#adaboost_learning(training_data=X_train,training_results=Y_train,odds=odds) # dumps a file

				loaded_model = pickle.load(open(script_path + '/XGBoost_dump.sav', 'rb'))
				#print "Approximate model accuracy", loaded_model.score(X_test, Y_test)
				model_acc += loaded_model.score(X_test, Y_test)

				boosted_decisions = loaded_model.predict_proba(evaluation_data)
				
				bins = np.linspace(0,1,21)
				#print eval_odds[0]


				for i_cut, bdt_cut in enumerate(bdt_bins):

					if bet_type == "asian":
						succes, fails, winnings, bets = asian_line_eval(bdt_cut=bdt_cut,boosted_decisions=boosted_decisions,eval_results=eval_results,eval_odds=eval_odds,bet_limit=bet_limit)
					elif bet_type == "next goal":
						succes, fails, winnings, bets = next_goal_eval(bdt_cut=bdt_cut,boosted_decisions=boosted_decisions,eval_results=eval_results,eval_odds=eval_odds,bet_limit=bet_limit)
					
					bets_array[i_cut][i_size] += bets
					winnings_array[i_cut][i_size] += winnings
					#print "BDT cut: ", bdt_cut, "winnings: ", winnings, "bets: ", bets
		model_acc_array.append(model_acc)
		"""
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
		"""



	print np.array(model_acc_array) / random_states * 100.
	plot_title = "Home next goal. Odds min: %1.2f. Match time: %1.1f min" %(bet_limit,match_time/100.)
	fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 6))
	fig1 = ax1.imshow((winnings_array.T - bets_array.T),vmin=-random_states*15,vmax=random_states*15,cmap='PuOr')
	fig.colorbar(fig1, ax=ax1, shrink=0.45)
	fig2 = ax2.imshow((winnings_array.T / bets_array.T),vmin=0.5,vmax=1.5,cmap='PuOr')
	fig.colorbar(fig2, ax=ax2, shrink=0.45)
	plt.suptitle(plot_title)

	ax3.plot(test_size_bins, np.array(model_acc_array) / random_states * 100.)
	ax3.set_xlabel("test size")
	ax3.set_ylabel("model acc")
	for plot in (ax1, ax2):
		plot.set_xticks(range(0,len(bdt_bins)))
		
		plot.set_xticklabels(bdt_bins, rotation=90)
		plot.set_yticks(range(0,len(test_size_bins)))
		plot.set_yticklabels(test_size_bins)
		plot.set_xlabel("bdt cut")
		plot.set_ylabel("test size %")

	save_title = "Winnings_HNG_MO_%1.2f_MT_%1.1f_RS_%i.png" %(bet_limit,match_time/100.,random_states)
	plt.savefig("plots/" + save_title)
	plt.close()



bdt_cut = 0
if bet_type == "asian":
	succes, fails, winnings, bets = asian_line_eval(bdt_cut=bdt_cut,boosted_decisions=boosted_decisions,eval_results=eval_results,eval_odds=eval_odds,bet_limit=bet_limit)
elif bet_type == "next goal":
	succes, fails, winnings, bets = next_goal_eval(bdt_cut=bdt_cut,boosted_decisions=boosted_decisions,eval_results=eval_results,eval_odds=eval_odds,bet_limit=bet_limit)

plt.hist(succes,bins=bins,histtype='step',label='succes',linewidth=2)
plt.hist(fails,bins=bins,histtype='step',label='fail',linewidth=2)
plt.legend()
plt.vlines(0.5,0,150,linestyles="dashed",linewidth=2)
plt.xlim(-0.05,1.05)
plt.ylim(0,90)
plt.xlabel("BDT score")
plt.ylabel("Frequency")
plt.show(block=False)
raw_input('...')

