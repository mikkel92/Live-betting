import time
import numpy as np
import matplotlib.pyplot as plt
import os, re, sys, tempfile, base64, subprocess
import urllib, json
import requests
from live_bet365 import scrape_betting
from datetime import datetime
from selenium import webdriver

# ------------------------------------------------------ #
# SCRIPT NEEDS SUDO COMMAND!                             #
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

def connect_to_VPN(server):

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



servers = Get_VPNGate_servers()
for vpn in servers[0:2]:
	time_connected = datetime.now()
	connection_succes = connect_to_VPN(vpn)
	webdriver.Chrome().close()
	if connection_succes:
		scrape_time = datetime.now() - time_connected
		time.sleep(300 - scrape_time.total_seconds())
	else: continue













