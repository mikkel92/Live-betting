#!/home/mikkel/anaconda2/bin/python

from connect_to_VPN import *
from scrape_bet365 import scrape_betting
import numpy as np
from datetime import datetime
import time
import random
import mysql.connector
from data_loader import data_loader



def run_scraper(vpn="expressvpn",debug=False):

	restart_time = datetime.now()

	"""
	mydb = mysql.connector.connect(
	  host="localhost",
	  user="root",
	  passwd="",
	  database="bets"
	)

	mycursor = mydb.cursor()
	mycursor.execute("DELETE FROM BettingData WHERE Time < NOW() - INTERVAL 10 HOUR")
	"""


	mydb = 'a'
	live_analysis = False

	if vpn == "mullvad":
		server_list = get_mullvad_servers()
		# list of servers working this connection way
		server_list = [["se","sto","success"],["se","hel","success"],
						["se","got","success"],["de","fra","success"],["de","ber","success"],
						["gb","mnc","success"],["gb","lon","success"]]
	
	if vpn == "expressvpn":
		server_list = [["dk1"],["nlam"],["nlro"],["nlth"],
						["defr1"],["defr2"],["denu"],["deda"],
						["ukbe"],["ukke"],["uklo"],["ukel"],
						["ukdo"],["se1"],["se2"],
						["no1"],["frpa1"],["frpa2"],["frst"],
						["ch1"],["ch2"],["itmi"],["itco"],
						["ro1"],["be1"],["is1"],["fi1"],
						["esma"],["esba"],["ie1"],["pt1"],
						["at1"],["cz1"],["lu1"],
						["li1"]]

		failed_servers = []
		
		random.shuffle(server_list)
	
	scrape_site = "success"
	counter = 0
	start_time = datetime.now()

	run = True
	while run:


		if len(server_list) < 5:
			server_list = [["dk1"],["nlam"],["nlro"],["nlth"],
						["defr1"],["defr2"],["denu"],["deda"],
						["ukbe"],["ukke"],["uklo"],["ukel"],
						["ukdo"],["se1"],["se2"],
						["no1"],["frpa1"],["frpa2"],["frst"],
						["ch1"],["ch2"],["itmi"],["itco"],
						["ro1"],["be1"],["is1"],["fi1"],
						["esma"],["esba"],["ie1"],["pt1"],
						["at1"],["cz1"],["lu1"],
						["li1"]]

			failed_servers = []

		print "servers: ", server_list
		print "failed servers: ", failed_servers

		for server in server_list: 
			
			counter += 1

			if counter < len(server_list):
				scrape_site = "failed"
			
			print("Time connected: ", str(datetime.now()))	
			# If the last server successfully loaded the matches
			if scrape_site == "success":

				try:
					rand_fail_server = failed_servers[int(np.random.rand()*len(failed_servers))] # get random server in the failed list
					
					connect_with_expressvpn(server=rand_fail_server)
					
					scrape_site = scrape_betting(live_analysis=live_analysis,database=mydb,debug=debug)
					disconnect_with_expressvpn()

					if scrape_site == "success":
						server_list.append(failed_servers.pop(failed_servers.index(rand_fail_server)))
						
					else:
						disconnect_with_expressvpn()
						continue
						

				except:
	
					connect_with_expressvpn(server=server)
					scrape_site = scrape_betting(live_analysis=live_analysis,database=mydb,debug=debug)
				
					if scrape_site == "failed":
						failed_servers.append(server_list.pop(server_list.index(server)))
						
						disconnect_with_expressvpn()
						continue 

					disconnect_with_expressvpn()

			else:

				connect_with_expressvpn(server=server)
				scrape_site = scrape_betting(live_analysis=live_analysis,database=mydb,debug=debug)
			
				if scrape_site == "failed":
					failed_servers.append(server_list.pop(server_list.index(server)))
					
					disconnect_with_expressvpn()
					continue 

				disconnect_with_expressvpn()
			
			print "last server: ", scrape_site
			scrape_time = datetime.now() - start_time 
			if 299.5 - scrape_time.total_seconds() < 0:
				start_time = datetime.now()
				continue
			else:
				print "sleeping for ", abs(299.5 - scrape_time.total_seconds()), " seconds"
				time.sleep(abs(299.5 - scrape_time.total_seconds()))
			
			start_time = datetime.now()
			
			if (datetime.now() - restart_time).total_seconds() > 3600 * 6:
				os.system("sudo reboot now")
				
if __name__ == "__main__":
	run_scraper(debug=True)
	#run_scraper()















