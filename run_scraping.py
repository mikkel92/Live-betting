from connect_to_VPN import *
from scrape_bet365 import scrape_betting
import numpy as np
from datetime import datetime
import time

def run_scraper(vpn="expressvpn",debug=False):

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
						["ukdo"],["ukbe2"],["se1"],["se2"],
						["no1"],["frpa1"],["frpa2"],["frst"],
						["ch1"],["ch2"],["itmi"],["itco"],
						["ro1"],["be1"],["is1"],["fi1"],
						["esma"],["esba"],["ie1"],["pt1"],
						["at1"],["pl1"],["cz1"],["lu1"],
						["li1"]]

		failed_servers = []

	scrape_site = "success"
	counter = 0
	start_time = datetime.now()

	while True:

		print "servers: ", server_list
		print "failed servers: ", failed_servers

		for server in server_list: 

			counter += 1

			print "last server: ", scrape_site

			if counter < len(server_list):
				scrape_site = "failed"
			
				
			# If the last server successfully loaded the matches
			if scrape_site == "success":

				try:
					rand_fail_server = failed_servers[int(np.random.rand()*len(failed_servers))] # get random server in the failed list
					print rand_fail_server
					connect_with_expressvpn(server=rand_fail_server)
					print "successfully connected to ", rand_fail_server
					scrape_site = scrape_betting(debug=debug)
					disconnect_with_expressvpn()

					if scrape_site == "success":
						server_list.append(failed_servers.pop(failed_servers.index(rand_fail_server)))
						
					else:
						continue
						

				except:
	
					connect_with_expressvpn(server=server)
					scrape_site = scrape_betting(debug=debug)
				
					if scrape_site == "failed":
						failed_servers.append(server_list.pop(server_list.index(server)))
						
						disconnect_with_expressvpn()
						continue 

					disconnect_with_expressvpn()

			else:

				connect_with_expressvpn(server=server)
				scrape_site = scrape_betting(debug=debug)
			
				if scrape_site == "failed":
					failed_servers.append(server_list.pop(server_list.index(server)))
					
					disconnect_with_expressvpn()
					continue 

				disconnect_with_expressvpn()
			
			scrape_time = datetime.now() - start_time 
			
			time.sleep(abs(299.5 - scrape_time.total_seconds()))
			
			start_time = datetime.now()

if __name__ == "__main__":
	run_scraper()
















