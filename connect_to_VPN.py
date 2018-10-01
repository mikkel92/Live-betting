import time
import numpy as np
import matplotlib.pyplot as plt
import os, re, sys, tempfile, base64, subprocess
import urllib, json
import requests
from live_bet365 import scrape_betting
from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup

# ------------------------------------------------------ #
# VPNGate SCRIPTs NEEDS SUDO COMMAND!                             #
# ------------------------------------------------------ #

# Get servers from VPNGate
def Get_VPNGate_servers():

	try:
	    vpn_data = requests.get('http://www.vpngate.net/api/iphone/').text.replace('\r','')
	    servers = [line.split(',') for line in vpn_data.split('\n')]
	    labels = servers[1]
	    labels[0] = labels[0][1:]

	    # Server columns
	    #HostName,IP,Score,Ping,Speed,CountryLong,CountryShort,NumVpnSessions,Uptime,
	    #TotalUsers,TotalTraffic,LogType,Operator,Message,OpenVPN_ConfigData_Base64

	    servers = [s for s in servers[2:] if len(s) > 1]
	    print 'Found %i servers on VPNGate'%len(servers)

	except:
	    print 'Cannot get VPN servers data'

	supported = [s for s in servers if len(s[-1]) > 0]

	return supported

def connect_to_VPNGate(server):

	# Currently works on Mac OS

	print "\nLaunching VPN..."
	path = '/tmp/tmpVPNconfig'

	try:
		os.system('rm ' + path)
	except:
		print path, "doesn't exists yet, creating file:"

	fout = open(path, 'w')
	fout.write(base64.b64decode(server[-1]))
	fout.write('\nscript-security 2')#\nup /etc/openvpn/update-resolv-conf\ndown /etc/openvpn/update-resolv-conf')
	fout.close()

	print "\nConnection to IP %s" %server[1]
	VPN_connection = subprocess.Popen(['openvpn', '--config', path])
	time.sleep(5)

	# Scrape the bet360 page using live_bet365.py script
	try:
		scrape_betting()
		return True
		VPN_connection.kill()
	except:
		return False
		VPN_connection.kill()

	print '\nVPN terminated'

def get_mullvad_servers():

	# Get the servers from mullvad page
	servers_url = "https://mullvad.net/en/servers/"
	html = requests.get(servers_url).text
	soup = BeautifulSoup(html, 'html.parser')
	server_list = soup.find_all('tr')

	# Find all the name from the terminal connection
	connect_info = []
	for server in server_list:
		tds = server.find_all('td') 
		if len(tds) == 6:
			break

		if '-' in tds[4].text:
			connect_info.append(tds[4].text)
		
	servers = [i.split('-') for i in set(connect_info)]
	print "Number of servers on mullvad:" , len(servers)

	return servers

	#print html

def connect_with_mullvad(server):
	
	terminal_command = "$MULLVAD_DIR relay set location %s %s" % (server[0],server[1])
	os.system(terminal_command)
	print "Connecting to server: %s %s" % (server[0],server[1])
	os.system('$MULLVAD_DIR connect')

	time.sleep(10)

def disconnect_with_mullvad():

	try:
		print "Disconnecting from mullvad server"
		os.system('$MULLVAD_DIR disconnect')
	except:
		print "Not connected via mullvad"

	time.sleep(5) # takes a few seconds to connect














