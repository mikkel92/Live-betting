import numpy as np
import os, sys
import json
from machine_learning import *
from sklearn import model_selection
import pickle

def next_goal_eval(bdt_cut,boosted_decisions,eval_results,eval_odds,bet_limit,bet_result='all'):
	
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
	won = 0
	winnings = 0
	bets = 0
	bet_every_match = [0,0,0]
	matches = 0
	#print bdt_cut
	for match in range(0,len(boosted_decisions)):

		max_decision = np.where(boosted_decisions[match] == max(boosted_decisions[match]))[0][0]
		
		if eval_odds[match] == "failed":
			continue

		
		bet_every_match[eval_results[match]] += eval_odds[match][eval_results[match]]
		matches += 1
		
		if eval_odds[match][max_decision] < bet_limit:
			continue

		if max(boosted_decisions[match]) < bdt_cut:
			continue

		if bet_result != "all":
			if max_decision != bet_result:
				continue

		if bdt_cut == 0.6:
			print("1, x, 2 odds: ", eval_odds[match])
			print("machine learning estimation: ", boosted_decisions[match])
			print("machine learning guess: ", max_decision, "actual outcome: ", eval_results[match], "\n")


			

		if eval_results[match] == max_decision:
			if max_decision != bet_result:
				print(max_decision, bet_result)
			succes.append(boosted_decisions[match][bet_result])
			winnings += float(eval_odds[match][max_decision])
			won += 1.
			bets += 1.
			#if boosted_decisions[match]
		else:
			fails.append(boosted_decisions[match][bet_result])
			bets += 1.

		if winnings == "home vs all": # TODO make a one vs all type
			print("WTF")
			if eval_results[match] == 0 and boosted_decisions[match][0] > bdt_cut:
				#print(eval_odds[match])
				winnings += float(eval_odds[match][0])
				bets += 1

			if eval_results[match] == 0 and boosted_decisions[match][0] > bdt_cut:
				bets += 1.
				

	return  succes, fails, winnings, bets, won, bet_every_match, matches

def asian_line_eval(bdt_cut,boosted_decisions,eval_results,eval_odds,bet_limit):
			
	succes = []
	fails = []

	winnings = 0
	bets = 0
	#print(bdt_cut)
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


def get_ML_data(files,debug=False):

	if len(files) == 1:
		print("dont use the get_ML_data function, just call reagrange_month_data")

	print("loading data from %i files..." %len(files))
	failed_matches = []

	with open(files[0]) as f:
		data = json.load(f)
		data, data_points, fails = reagrange_month_data(data=data,debug=debug)
		failed_matches.append(fails)

	for file in files[1:]:

		with open(file) as f:
			tmp_data = json.load(f)
			tmp_data, tmp_data_points, fails = reagrange_month_data(data=tmp_data,debug=debug)
			failed_matches.append(fails)
			data = np.concatenate((data,tmp_data))
			data_points = np.concatenate((data_points,tmp_data_points))

	print("done loading data")

	return data, data_points, failed_matches

def get_bet_data(files,match_time,bet_type,debug=False):

	if len(files) == 1:
		print("dont use the get_ML_data function, just call reagrange_month_data")

	print("loading odds + results from %i files..." %len(files))
	failed_matches = []

	with open(files[0]) as f:
		data = json.load(f)
		results, odds, fails = get_month_bet_info(data=data,match_time=match_time,bet_type=bet_type,debug=debug)
		failed_matches.append(fails)

	for file in files[1:]:

		with open(file) as f:
			tmp_data = json.load(f)
			tmp_results, tmp_odds, tmp_fails = get_month_bet_info(data=tmp_data,match_time=match_time,bet_type=bet_type,debug=debug)
			failed_matches.append(fails)

			results = np.concatenate((results,tmp_results))
			odds = np.concatenate((odds,tmp_odds))

	print("done loading odds")

	return results, odds, failed_matches


def clean_ML_data(ML_data,data_points,odds,results):

	#Clean for missing data points.
	#TODO, rewrite "get_month_bet_info" function in machine_learning.py to not return np.inf in results if odds are missing
	print("Number of matches: ", np.shape(odds)[0])

	bad_data = []

	for i_data_point in range(0, np.shape(odds)[0]):

		if not np.isfinite(odds[i_data_point]).all():
			bad_data.append(i_data_point)
		elif not np.isfinite(ML_data[i_data_point]).all():
			bad_data.append(i_data_point)
		elif not np.isfinite(results[i_data_point]).all():
			bad_data.append(i_data_point)

	
	odds = np.delete(odds,bad_data,0)
	ML_data = np.delete(ML_data,bad_data,0)
	results = np.delete(results,bad_data,0)
	data_points = np.delete(data_points,bad_data,0)

	print("Number of matches after cleaning: ", np.shape(odds)[0])

	return np.array(ML_data), np.array(data_points), np.array(odds), np.array(results)


# define parameters
bet_limit = 2.0
random_states = 1
test_size = 0.25
#bet_type = "asian"
bet_type = "next goal"

bdt_bins = [round(i,2) for i in np.linspace(0.3,0.8,26)]
match_time_bins = [int(i) for i in np.linspace(1000,9000,17)]


# Load the data
script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
file1 = script_path + "/2018_9_month_data.json"
file2 = script_path + "/2018_10_month_data.json"
#file3 = script_path + "/2018_11_month_data.json"

files = [file1, file2]#, file3]

ML_data, data_points, data_fails = get_ML_data(files=files)




for bet_result in [0]:#,1,2,'all']:

	# arrays for plotting
	bets_array = np.zeros([len(bdt_bins),len(match_time_bins)])
	winnings_array = np.zeros([len(bdt_bins),len(match_time_bins)])
	model_acc_array = []
	win_percent_array = np.zeros([len(bdt_bins),len(match_time_bins)])

	for i_time, match_time in enumerate(match_time_bins):

		results, odds, odds_fails = get_bet_data(files=files,match_time=match_time,bet_type=bet_type,debug=False)
		ML_data, data_points, odds, results =  clean_ML_data(ML_data, data_points, odds, results)
		
		"""
		# Rearange data for machine learning
		data1, results1, odds1 = reagrange_month_data(data=train_data,match_time=match_time,debug=False,bet_type=bet_type)
		data2, results2, odds2 = reagrange_month_data(data=eval_data,match_time=match_time,debug=False,bet_type=bet_type)
		all_data = np.concatenate((data1,data2))
		all_results = np.concatenate((results1,results2))
		all_odds = np.concatenate((odds1,odds2))
		all_data = np.column_stack((all_data,all_odds))
		all_data = all_data[:,-13:]
		# sample for applying model
		data3, results3, odds3 = reagrange_month_data(data=nov_data,match_time=match_time,debug=False,bet_type=bet_type)
		nextlvl_data = np.column_stack((data3,odds3))
		nextlvl_data = nextlvl_data[:,-13:]
		"""
		model_acc = 0

		for i_rand in range(0,random_states): # loop over random states

			for i in range(1,len(ML_data)):
				if len(ML_data[i]) != len(ML_data[i-1]):
					print(len(ML_data[i]))
			print(np.shape(ML_data))
			ML_data = np.array(np.column_stack((ML_data,odds)))
			print(ML_data[0])
			print(np.shape(ML_data))
			X_data, X_valid, Y_data, Y_valid = model_selection.train_test_split(ML_data, results, test_size=0.4,random_state=i_rand)
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
					,test_data=X_test,test_results=Y_test,max_depth=max_depth)

				#adaboost_learning(training_data=X_train,training_results=Y_train,odds=odds) # dumps a file

				loaded_model = pickle.load(open(script_path + '/XGBoost_dump.sav', 'rb'))
				#print("Approximate model accuracy", loaded_model.score(X_test, Y_test))
				model_acc += loaded_model.score(X_test, Y_test)

				boosted_decisions = loaded_model.predict_proba(evaluation_data)
				
				bins = np.linspace(0,1,21)
				#print(eval_odds[0])


				for i_cut, bdt_cut in enumerate(bdt_bins):

					if bet_type == "asian":
						succes, fails, winnings, bets, won = asian_line_eval(bdt_cut=bdt_cut,boosted_decisions=boosted_decisions,eval_results=eval_results,eval_odds=eval_odds,bet_limit=bet_limit)
					elif bet_type == "next goal":
						#succes, fails, winnings, bets, won, bet_every_match, matches = next_goal_eval(bdt_cut=bdt_cut,boosted_decisions=boosted_decisions,eval_results=eval_results,eval_odds=eval_odds,bet_limit=bet_limit,bet_result=bet_result)
						boosted_decisions = loaded_model.predict_proba(nextlvl_data)
						succes, fails, winnings, bets, won, bet_every_match, matches = next_goal_eval(bdt_cut=bdt_cut,boosted_decisions=boosted_decisions,eval_results=results3,eval_odds=odds3,bet_limit=bet_limit,bet_result=bet_result)
					
					bets_array[i_cut][i_time] += bets
					winnings_array[i_cut][i_time] += winnings
					win_percent_array[i_cut][i_time] += won
					#print("BDT cut: ", bdt_cut, "winnings: ", winnings, "bets: ", bets)

			# test model
			"""
			boosted_decisions = loaded_model.predict_proba(nextlvl_data)
			succes, fails, winnings, bets, won, bet_every_match, matches = next_goal_eval(bdt_cut=0,boosted_decisions=boosted_decisions,eval_results=results3,eval_odds=odds3,bet_limit=bet_limit,bet_result=bet_result)
			plt.hist(succes,bins=bdt_bins,histtype='step',linewidth=2,label="succes")
			plt.hist(fails,bins=bdt_bins,histtype='step',linewidth=2,label="fails")
			plt.legend()
			plt.xlabel("ML score")
			plt.ylabel("frequency")
			plt.show()
			"""

		model_acc_array.append(model_acc)
		print(bet_every_match)
		print(matches)
		
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


	"""
	print(np.array(model_acc_array) / random_states * 100.)
	print(winnings_array)
	print(bets_array)
	"""
	plot_title = "Home next goal. Odds min: %1.2f. Match time: %1.1f min" %(bet_limit,match_time/100.)
	fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(16, 12))
	plt.suptitle(plot_title)

	fig1 = ax1.imshow((winnings_array.T - bets_array.T) / random_states,vmin=-(np.amax(winnings_array) - np.amax(bets_array)) / random_states,
	vmax=(np.amax(winnings_array) - np.amax(bets_array)) / random_states,cmap='PuOr')
	fig.colorbar(fig1, ax=ax1, shrink=0.45)
	ax1.set_title("winnings - bets")

	fig2 = ax2.imshow(((winnings_array.T / random_states) / (bets_array.T / random_states)) ,vmin=0.5,vmax=1.5,cmap='PuOr')
	fig.colorbar(fig2, ax=ax2, shrink=0.45)
	ax2.set_title("winnings / bets")

	fig3 = ax3.imshow(np.log10(bets_array.T / random_states),cmap='Oranges')
	fig.colorbar(fig3, ax=ax3, shrink=0.45)
	ax3.set_title("Log10(bets)")

	fig4 = ax4.imshow(win_percent_array.T / bets_array.T,cmap='PuOr',vmax=1,vmin=0)
	fig.colorbar(fig4, ax=ax4, shrink=0.45)
	ax4.set_title("acc on data")

	ax5.plot(match_time_bins, np.array(model_acc_array) / random_states * 100., label="estimated acc")
	ax5.set_xlabel("match time")
	ax5.set_ylabel("model acc")
	ax5.set_title("model accuracy")
	ax5.legend()
	for plot in (ax1, ax2, ax3, ax4):
		plot.set_xticks(range(0,len(bdt_bins)))
		plot.set_xticklabels(bdt_bins, rotation=90)
		plot.set_yticks(range(0,len(match_time_bins)))
		plot.set_yticklabels(match_time_bins)
		plot.set_xlabel("bdt cut")
		plot.set_ylabel("match time")

	if len(match_time_bins) == 1:
		ax6.hist(succes,bins=bdt_bins,histtype='step',linewidth=2,label="succes")
		ax6.hist(fails,bins=bdt_bins,histtype='step',linewidth=2,label="fails")
		ax6.legend()
		ax6.set_xlabel("ML score")
		ax6.set_ylabel("frequency")
		

	save_title = "Winnings_HNG_MO_%1.2f_BET_%s_RS_%i.png" %(bet_limit,bet_result,random_states)
	plt.savefig("plots/" + save_title)
	print("dumped plot in Analysis/plots/")
	plt.close()


"""
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
"""
