# Live-betting

Repository for live prediction of soccer matches

The project is twofold: Web scraping of live soccer stats (this repo) and estimate of profitable live bets (Analysis repo)

Web scraping requirements: Selenium, Chromedriver, Requests,



# Installation: ( $ = type in command line )

Make a folder for the project 

$ mkdir "folder" 

$ cd "folder"

$ git clone https://github.com/mikkel92/Live-betting.git

$ pip install selenium

$ pip install requests

Download latests chromedriver from https://sites.google.com/a/chromium.org/chromedriver/downloads 

Put chromedriver.exe in "folder" or add the path to chromedriver in your .bash_profile

$ python scrape_bet365.py

This should open a browser and start scraping current soccer matches. It will also create a folder to save the data in. If you don't want the program to print in the terminal and open google while doing this, set debug=False in the last line of the script.

# Running options

For manual use of the script simply run "scrape_bet365.py" every time you want the data of current live matches. 

The script can be run automatically every X minutes (default 5 min) with the "run_scraping.py" script. This will most likely require a VPN, since bet365 temporarily suspends your IP for overusage of their webpage. I am currently using ExpressVPN, but feel free to use whatever you like (will require code changes). I am currently using Ubuntu for the, while Windows doesn't have a CLI for ExpressVPN.

# Analysis part

The Analysis repo is currently an unfinshed mess. It will be updated soon, with some basic example scripts. 

