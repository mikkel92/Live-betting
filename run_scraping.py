from connect_to_VPN import get_mullvad_servers, connect_with_mullvad, disconnect_with_mullvad
from scrape_bet365 import scrape_betting
import numpy as np
from datetime import datetime
import time

def run_scraper():

	server_list = get_mullvad_servers()

	while True:
		for server in server_list:
			if server[0] in ["ca","au","us"]:
				continue 

			start_time = datetime.now()	
			connect_with_mullvad(server=server)
			scrape_site = scrape_betting()
			print scrape_site
			if scrape_site == "failed":
				continue

			disconnect_with_mullvad()
			scrape_time = datetime.now() - start_time 
			
			time.sleep(270. - scrape_time.total_seconds())

if __name__ == "__main__":
	run_scraper()