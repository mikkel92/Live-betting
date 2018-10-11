
import time
import datetime
import numpy as np
import os, re
import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchAttributeException
from selenium.webdriver.common.keys import Keys
import urllib, json
from datetime import datetime

def get_match_data(button,browser,debug=False):

	if debug:
		print("Getting match data:")


	"""	
	# Click any unclicked odds tabs ( Works but takes alot of time )
	try:
		event_odds = browser.find_elements_by_class_name("gl-MarketGroup")
		for i in event_odds:
			if i.size['height'] < 35: #Arbitrary placeholder, the heigh is 30 seemingly
				i.click()
	except:
		print("whatever")
	"""

	# try to scrape the match data

	inner_html = "None"

	try:
		# click match button and wait a bit for it to load
		start_time = datetime.now()
		button.click()
		time.sleep(0.5)
		inner_html = str(button.get_attribute('innerHTML').encode(encoding='UTF-8',errors='strict'))

		# change to stats tab i live stream is an option for the match
		if "ipn-ScoreDisplayStandard_AVIcon" in inner_html:
			stats_tab = browser.find_element_by_class_name("lv-ButtonBar_MatchLive")
			stats_tab.click()
			time.sleep(0.2)

		event_team = browser.find_elements_by_class_name("ml1-ScoreHeader_TeamText")
		event_time = browser.find_elements_by_class_name("ml1-ScoreHeader_Clock")
		score_data = browser.find_elements_by_class_name("ml1-ScoreHeader_Column")
		event_data = browser.find_elements_by_class_name("ml1-AllStats")
		evex1_data = browser.find_elements_by_class_name("ml1-StatWheel_Team1Text") # Properly extracts team stats from event data window
		evex2_data = browser.find_elements_by_class_name("ml1-StatWheel_Team2Text")
		event_odds = browser.find_elements_by_class_name("gl-MarketGroup")
		
		processed_event_team = split_data(event_team)
		processed_event_time = event_time[0].text
		processed_score_data = split_data(score_data)
		processed_event_data = split_data(event_data)
		processed_evex1_data = split_data(evex1_data)
		processed_evex2_data = split_data(evex2_data)
		processed_event_odds = split_data(event_odds)

		match_data = [processed_event_team, processed_event_time, processed_event_data,
		processed_event_odds, processed_score_data, processed_evex1_data, processed_evex2_data]

		if debug:
			print("Successfully found match data")
		
	except Exception as err: 
		if debug:
			print("Failed to get data from match")
			print("Error message:", err)
		match_data = "failed"


	if "ipn-ScoreDisplayStandard " not in inner_html:
		match_data = "not_soccer_match"
	
	#time.sleep(np.random.rand()*0.5)
	return match_data

def split_data(data):
	
	splitlist = []

	for category in data:
		totext = category.text
		processed = totext.split("\n")
		splitlist.append(processed)

	return splitlist

def rearange_data(data):
	#print(data)
	structured_data = {"teams":[],
					   "score":[],
					   "time":[],
					   "stats":{"attacks":[],"dangerous attacks":[],"possession":[],
					   "shots on target":[],"shots off target":[]},
					   "odds":{"next goal":[],"fulltime result":[],"draw money back":[]
					   ,"asian handicap":[]},
					   "extra odds":[]
						}
	# team names
	structured_data["teams"].append(data[0][0][0])
	structured_data["teams"].append(data[0][1][0])

	# score
	structured_data["score"].append(data[4][0][1])
	structured_data["score"].append(data[4][1][0])

	# time
	structured_data["time"].append(data[1])	

	# stats
	structured_data["stats"]["attacks"].append(data[5][0][0])
	structured_data["stats"]["attacks"].append(data[6][0][0])
	structured_data["stats"]["dangerous attacks"].append(data[5][1][0])
	structured_data["stats"]["dangerous attacks"].append(data[6][1][0])
	structured_data["stats"]["shots off target"].append(data[2][0][-2])
	structured_data["stats"]["shots off target"].append(data[2][0][-1])
	structured_data["stats"]["shots on target"].append(data[2][0][-4])
	structured_data["stats"]["shots on target"].append(data[2][0][-3])

	if len(data[2][0]) == 9: # matches with possession stats
		structured_data["stats"]["possession"].append(data[5][2][0])
		structured_data["stats"]["possession"].append(data[6][2][0])

	# odds
	goals_home = int(structured_data["score"][0])
	goals_away = int(structured_data["score"][1])
	next_goal = goals_home + goals_away + 1
	
	for bet_type in data[3]:
		
		# next goal
		goal_str = (str(next_goal) + ". m" + "\xe5" + "l")
		if bet_type[0] == goal_str.decode('latin1'): 
			
			for i_odds in bet_type:
				try:
					float(i_odds)
					structured_data["odds"]["next goal"].append(i_odds)
				except: continue
	
		# fulltime result
		if bet_type[0] == "Fuldtid - Resultat":
			
			for i_odds in bet_type:
				try:
					float(i_odds)
					structured_data["odds"]["fulltime result"].append(i_odds)
				except: continue

		# draw money back
		draw_str = "Uafgjort - V" + "\xe6" + "ddem" + "\xe5" + "l annulleret"
		if bet_type[0] == draw_str.decode('latin1'):

			for i_odds in bet_type:
				try:
					float(i_odds)
					structured_data["odds"]["draw money back"].append(i_odds)
				except: continue

		# asian handicap
		asian_str = "Asian handicap (%i-%i)" %(goals_home,goals_away)
		if bet_type[0] == asian_str:
			
			for i_entry in bet_type[1:]:
				structured_data["odds"]["asian handicap"].append(i_entry)

		# other odds:
		structured_data["extra odds"] = data[3]

		return structured_data

def save_data(data,debug=False):

	import json

	if debug:
		print("Saving match data:")

	# Create folder for data if it doesn't exists
	time_now = datetime.now()
	save_path = "%s/%s/%s/%s/" % (os.getcwd(),time_now.year,time_now.month,time_now.day)
	if not os.path.exists(save_path):
		os.makedirs(save_path)
	
	try:
		save_data = rearange_data(data)
		match_team = save_data["teams"]
		match_time = save_data["time"][0].replace(":", "")
		
		now = datetime.now()
		club1 = match_team[0].replace(" ", "")
		club2 = match_team[1].replace(" ", "")
		filename = now.strftime("%d%m%y") + club1[0:3] + club2[0:3] + match_time
		fout = open(save_path + filename + '.txt', "w")
		fout.write(json.dumps(save_data))
		
		fout.close()

		#with open(save_path + filename + '.json', "w") as outfile:
		#	json.dump(save_data, outfile)

		if debug:
			print(match_team[0], match_time)
			print("Successfully saved data")

	except Exception as err:
		if debug:
			print(err)
			print("Unable to save data")

def write_to_database():

	import sqlite3
	script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
	connection = sqlite3.connect(script_path + "/database/bets")
	cursor = connection.cursor()

	print script_path + "/database/bets"

	format_data = """
	INSERT INTO Matches (
	HomeTeam,
	AwayTeam,
	League,
	Country,
	HomeScore,
	AwayScore,
	TimePassed,
	Date,
	HomeAttacks,
	HomeDangerousAttacks,
	HomePossession,
	HomeShotsOnGoal,
	HomeShotsOffGoal,
	HomeCorners,
	HomeYellowCards,
	HomeRedCards,
	AwayAttacks,
	AwayDangerousAttacks,
	AwayPossession,
	AwayShotsOnGoal,
	AwayShotsOffGoal,
	AwayCorners,
	AwayYellowCards,
	AwayRedCards,
	HomeScoresNextGoal,
	NoNextGoal,
	AwayScoresNextGoal,
	HomeAsianHandicap,
	AwayAsianHandicap,
	HomeTie,
	AwayTie,
	HomeFullTimeResult,
	DrawFullTimeResult,
	AwayFullTimeResult,
	DoubleChanceHomeOrTie,
	DoubleChanceAwayOrTie,
	DoubleChanceHomeOrAway)

    VALUES ("{HomeTeam}",
	"{AwayTeam}",
	"{League}",
	"{Country}",
	"{HomeScore}",
	"{AwayScore}",
	"{TimePassed}",
	"{Date}",
	"{HomeAttacks}",
	"{HomeDangerousAttacks}",
	"{HomePossession}",
	"{HomeShotsOnGoal}",
	"{HomeShotsOffGoal}",
	"{HomeCorners}",
	"{HomeYellowCards}",
	"{HomeRedCards}",
	"{AwayAttacks}",
	"{AwayDangerousAttacks}",
	"{AwayPossession}",
	"{AwayShotsOnGoal}",
	"{AwayShotsOffGoal}",
	"{AwayCorners}",
	"{AwayYellowCards}",
	"{AwayRedCards}",
	"{HomeScoresNextGoal}",
	"{NoNextGoal}",
	"{AwayScoresNextGoal}",
	"{HomeAsianHandicap}",
	"{AwayAsianHandicap}",
	"{HomeTie}",
	"{AwayTie}",
	"{HomeFullTimeResult}",
	"{DrawFullTimeResult}",
	"{AwayFullTimeResult}",
	"{DoubleChanceHomeOrTie}",
	"{DoubleChanceAwayOrTie}",
	"{DoubleChanceHomeOrAway}");
    """

    sql_command = format_data.format(AwayTeam=)
	cursor.execute(sql_command)
	

def scrape_betting(debug=False):

	page_url_mobile = "https://mobile.bet365.dk/#type=InPlay;"
	page_url = "https://www.bet365.dk/#/IP/"
	
	options = webdriver.ChromeOptions()
	options.add_argument('headless')
	browser = webdriver.Chrome(chrome_options=options)  # choose web browser
	browser.set_page_load_timeout(10)
	"""
	options = webdriver.FirefoxOptions()
	options.add_argument('headless')
	browser = webdriver.Firefox("/usr/local/bin/")
	"""
	try:
		browser.get(page_url) # get the url for the corrosponding league
		browser.get(page_url)
		time.sleep(10) # sometimes requires a long waiting time when connecting via VPN

	except:
		browser.close()
		return "failed"
	
	# Click on the tab to web scrape
	try: 
		se_begivenhed_button = browser.find_elements_by_class_name("ip-ControlBar_BBarItem")
		se_begivenhed_button[1].click()
		time.sleep(5)
	except Exception as err: 
		if debug:
			print("Failed to load webpage")
			print("Error message:", err)
		browser.close()
		return "failed"



	# Click on every live event in the live betting tab
	event_buttons = browser.find_elements_by_class_name("ipn-FixtureButton")
	failed_loads = []


	match_time = browser.find_elements_by_class_name("ipn-ScoreDisplayStandard_Timer")

	for counter, button in enumerate(event_buttons):

		# for debugging
		#if counter == 1: break

		# skip matches that have not started yet (TODO: sometimes fails)
		try:
			if float(match_time[counter].text[0:2]) < 1:
				continue
		except Exception as err: 
			if debug:
				print("Failed to get time for match")
				print("Error message:", err)

		# Try to get the data from match
		
		match_data = get_match_data(button=button,browser=browser,debug=debug)
	
		# If the event is not a soccer match, then break
		if match_data == "not_soccer_match":
			if debug:
				print("Done scraping soccer matches")
			break

		# If the script failed to get data from a match, try again. If it fails again, then continue
		elif match_data == "failed":
			match_data = get_match_data(button=button,browser=browser,debug=debug)
			if match_data == "failed":
				failed_loads.append(button)
				continue
			else: 
				save_data(data=match_data,debug=debug)
				continue

		# Save the match data if successfully scraped
		else:
			save_data(data=match_data,debug=debug)
			continue
		
	# Try to get the data from the failed matches one more time, before ending script
	for button in failed_loads:

		match_data = get_match_data(button=button,browser=browser,debug=debug)
		if match_data == "failed":
			if debug:
				print("failed to get page second time")
		else:
			save_data(data=match_data,debug=debug)


	#print source
	browser.close()
	
	return "success"

# Run code without VPN by running this script directly
if __name__ == "__main__":
	scrape_betting(debug=True)


