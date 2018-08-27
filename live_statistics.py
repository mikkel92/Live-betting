import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import unicodedata
import json
import os

def bet_nextgoal(monthly_data):
	
	for match in monthly_data:
		print match
		break

def bet_asain(monthly_data):

	BP_weight = 0.2 # BallPossession weigth
	SOnG_weight = 20. # ShotsOnGoal weight
	SOffG_weight = 10. # ShotsOffGoal weight
	Better_weight = 1. # how much better does a team have to be for a bet to be placed?


	won = 0
	lost = 0

	for match in monthly_data:
		
		for i_t in range(0,len(match[2]['Time'])):
			

			try:
				if match[2]['Time'][i_t] > 58:
					home_score = (match[0]['homeBallPossession'][i_t] * BP_weight + 
								match[0]['homeShotsOnGoal'][i_t] * SOnG_weight + 
								match[0]['homeShotsOffGoal'][i_t] * SOffG_weight)
					away_score = (match[1]['awayBallPossession'][i_t] * BP_weight + 
								match[1]['awayShotsOnGoal'][i_t] * SOnG_weight + 
								match[1]['awayShotsOffGoal'][i_t] * SOffG_weight)
					current_standing = match[0]['homeScore'][i_t] - match[1]['awayScore'][i_t]
					
				break
			except: break
		try:
			end_result = match[0]['homeScore'][-1] - match[1]['awayScore'][-1]
			if end_result == current_standing:
				continue

			if home_score > away_score * Better_weight and end_result > current_standing:
				won += 1.
			elif home_score * Better_weight < away_score and end_result < current_standing:
				won += 1.
			elif home_score > away_score * Better_weight and end_result < current_standing:
				lost += 1.
			elif home_score * Better_weight < away_score and end_result > current_standing:
				lost += 1.
			else: continue

		except: continue

	return won, lost



def get_monthly_data(month):

	directory = '/Users/mjensen/Desktop/Universitet/Adaboost/live_betting/live_data/2018/%i/' %month
	file_list = []

	# get all txt files in the directory
	for txt_file in os.listdir(directory):
		if txt_file[-4:] == '.txt': 
			file_list.append(txt_file)

	file_list = sorted(file_list)

	match_data = []

	variables_to_use = ('ShotsOnGoal', 'ShotsOffGoal', 'BallPossession')

	while len(file_list) > 2:

		opened_files = []
		home_data = {'homeScore': [],}
		away_data = {'awayScore': [],}
		odds = {'Time': []}

		for key in variables_to_use:
			home_data['home' + key] = []
			away_data['away' + key] = []

		for i_f in range(0,len(file_list)):
			

			if file_list[i_f][0:2] and file_list[i_f][12:] in file_list[0]:
				file_data = json.load(open(directory + file_list[i_f]))
				opened_files.append(file_list[i_f])
				try:
					odds['Time'].append(file_data['liveForm'][-1]["minute"])
					for var in variables_to_use:
						
						home_data['home' + var].append(file_data['statistics']['home' + var])
						away_data['away' + var].append(file_data['statistics']['away' + var])
				except:
					a = 1

				home_data['homeScore'].append(file_data['event']['homeScore']['current'])
				away_data['awayScore'].append(file_data['event']['awayScore']['current'])
		match_data.append([home_data,away_data,odds])
		for index in opened_files:
			file_list.remove(index)	

	return match_data

monthly_data = get_monthly_data(3)
won, lost = bet_asain(monthly_data)

print won, lost , won/lost














