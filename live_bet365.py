
import time
import datetime
import numpy as np
import matplotlib.pyplot as plt
import os, re
import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchAttributeException
from selenium.webdriver.common.keys import Keys
import urllib, json
from datetime import datetime

def get_match_data(button,browser):

	print "Getting match data:"
	# click mathc button and wait a bit for it to load
	start_time = datetime.now()
	button.click()
	time.sleep(1.0)
	inner_html = str(button.get_attribute('innerHTML').encode(encoding='UTF-8',errors='strict'))

	# change to stats tab i live stream is an option for the match
	if "ipn-ScoreDisplayStandard_AVIcon" in inner_html:
		stats_tab = browser.find_element_by_class_name("lv-ButtonBar_MatchLive")
		stats_tab.click()
		time.sleep(0.2)

	"""	
	# Click any unclicked odds tabs
	try:
		event_odds = browser.find_elements_by_class_name("gl-MarketGroup")
		for i in event_odds:
			if i.size['height'] < 35: #Arbitrary placeholder, the heigh is 30 seemingly
				i.click()
	except:
		print "whatever"
	"""

	# try to scrape the match data
	try:
		event_time = browser.find_elements_by_class_name("ml1-ScoreHeader_Clock")
		event_data = browser.find_elements_by_class_name("ml1-AllStats")
		#event_odds = browser.find_elements_by_class_name("ipe-EventViewDetail_MarketGrid")
		event_odds = browser.find_elements_by_class_name("gl-MarketGroup")
		
		processed_event_time = event_time[0].text
		processed_event_data = split_data(event_data)
		processed_event_odds = split_data(event_odds)
		
		match_data = [processed_event_time, processed_event_data, processed_event_odds]
		print "Successfully found match data"
		
	except: 
		print "Failed to get data from match"
		match_data = "failed"

	if "ipn-ScoreDisplayStandard " not in inner_html:
		match_data = "not_soccer_match"
	
	time.sleep(np.random.rand()*0.5)
	return match_data

def split_data(data):
	
	splitlist = []

	for category in data:
		totext = category.text
		processed = totext.split("\n")
		splitlist.append(processed)

	return splitlist

def save_data(data):

	print "Saving match data:"
	# Create folder for data if it doesn't exists
	time_now = datetime.now()
	save_path = "%s/%s/%s/%s/" % (os.getcwd(),time_now.year,time_now.month,time_now.day)
	if not os.path.exists(save_path):
		os.makedirs(save_path)
	
	try:
		match_time = data[0].replace(":", "") # Removes the :
		if match_time == "":
			match_time = "PreMatch"
		event_data = data[1]
		event_odds = data[2]
		
		now = datetime.now()
		club1 = event_odds[0][1].replace(" ", "")
		club2 = event_odds[0][5].replace(" ", "")
		filename = now.strftime("%d%m%y") + club1[0:3] + club2[0:3] + match_time
		
		fout = open(save_path + filename + '.txt', "w")
		fout.write(match_time + "\n")
		fout.write('\n---------------------------------------\n\n')
		for line in event_data:
			fout.write(str(line) + "\n")
		fout.write('\n---------------------------------------\n\n')
		for line in event_odds:
			fout.write(str(line) + "\n")
		fout.close()

		print "Successfully saved data"

	except:
		print "Unable to save data"
	

def scrape_betting():

	page_url_mobile = "https://mobile.bet365.dk/#type=InPlay;"
	page_url = "https://www.bet365.dk/#/IP/"

	browser = webdriver.Chrome()  # choose web browser
	browser.get(page_url) # get the url for the corrosponding league
	browser.get(page_url)

	time.sleep(5) # requires a long waiting time when connecting via VPN

	# Click on the tab to web scrape
	se_begivenhed_button = browser.find_elements_by_class_name("ip-ControlBar_BBarItem")
	se_begivenhed_button[1].click()
	time.sleep(1)

	# Click on every live event in the live betting tab
	event_buttons = browser.find_elements_by_class_name("ipn-FixtureButton")
	failed_loads = []
	page_fails = ([0,0])

	for counter, button in enumerate(event_buttons):
		print counter

		# Try to get the data from match
		match_data = get_match_data(button,browser)
		print match_data[1]

		# If the event is not a soccer match, then break
		if match_data == "not_soccer_match":
			print "Done scraping soccer matches"
			break

		# If the script failed to get data from a match, try again. If it fails again, then continue
		elif match_data == "failed":
			match_data = get_match_data(button,browser)
			if match_data == "failed":
				failed_loads.append(button)
				continue
			else: 
				save_data(match_data)
				continue

		# Save the match data if successfully scraped
		else:
			save_data(match_data)
			continue
		
	# Try to get the data from the failed matches one more time, before ending script
	for button in failed_loads:

		match_data = get_match_data(button,browser)
		if match_data == "failed":
			page_fails[1] += 1
			print "failed to get page second time"
		else:
			save_data(match_data)
			

	print page_fails

	#print source
	browser.close()
	"""

	html = browser.execute_script("return document.documentElement.innerHTML;")

	# This will get the html after on-load javascript
	#html = driver.execute_script("return window.performance.getEntries();")
	#print html

	"""

# Run code without VPN by running this script directly
if __name__ == "__main__":
	scrape_betting()


