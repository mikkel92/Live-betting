# Live-betting
Repository for live prediction of soccer matches

The project is twofold: Web scraping of live soccer stats (this repo) and estimate of profitable live bets (Analysis repo)

Web scraping requirements: Selenium, Chromedriver, Requests,



Installation: ( $ = type in command line )

Make a folder for the project 

$ mkdir "folder" 

$ cd "folder"

$ git clone https://github.com/mikkel92/Live-betting.git

$ pip install selenium

$ pip install requests

Download latests chromedriver from https://sites.google.com/a/chromium.org/chromedriver/downloads 

Put chromedriver.exe in "folder" or add the path to chromedriver in your .bash_profile

$ python scrape_bet365.py

This should open a browser and start scraping current soccer matches. It will also create a folder to save the data in.



