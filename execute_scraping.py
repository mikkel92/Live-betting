import os, sys,time
import subprocess
p = subprocess.Popen([sys.executable, '/home/mikkel/Desktop/Live-betting/run_scraping.py'], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.STDOUT)

time.sleep(60*60*6)
os.system('reboot')
