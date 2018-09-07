from connect_to_VPN import get_mullvad_servers, connect_with_mullvad, disconnect_with_mullvad
from scrape_bet365 import scrape_betting
import numpy as np
from datetime import datetime
import time

def run_scraper(debug=False):

	server_list = get_mullvad_servers()
	# list of servers working this connection way
	server_list = [["se","sto","success"],["se","hel","success"],
					["se","got","success"],["de","fra","success"],["de","ber","success"],
					["gb","mnc","success"],["gb","lon","success"]]

	scrape_site = "success"

	while True:
		for server in server_list:
			if server[0] in ["ca","au","us"]:
				continue 

			# If the last server successfully loaded the matches
			if scrape_site == "success":
				start_time = datetime.now()	

			# If the last page failed and the next page in line failed last attemp, then continue to working server
			if scrape_site == "failed" and server[2] == "failed":
				continue

			connect_with_mullvad(server=server)
			scrape_site = scrape_betting(debug=debug)
			
			if scrape_site == "failed":
				server[2] = "failed"
				continue 

			disconnect_with_mullvad()
			server[2] = "success"
			
			scrape_time = datetime.now() - start_time 
			
			time.sleep(299.5 - scrape_time.total_seconds())

if __name__ == "__main__":
	run_scraper()
















