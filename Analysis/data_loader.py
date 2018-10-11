import numpy as np
import os, sys
import json

class data_loader():

	def __init__(self, date):

		self.date = date
		self.year = self.date.split("/")[0]
		self.path = os.path.dirname(os.path.realpath(sys.argv[0]))

		if len(self.date.split("/")) >= 2:
			self.month = self.date.split("/")[1]

		if len(self.date.split("/")) >= 3:
			self.day = self.date.split("/")[2]
         

	def load_match(self,match):

		match_data = []
		files_path = "%s/../%s" % (self.path,self.date) #format: year/month/day
		file_list = os.listdir(files_path)
		
		for file in file_list:
			if match in file:

				data = open(files_path + "/" + file, "r").read()
				match_data.append(eval(data))

		return match_data

	def load_one_day(self): # Can be optimized a lot in speed, by not looping entire directory every time one match needs to be loaded

		files_path = "%s/../%s" % (self.path,self.date) #format: year/month/day
		file_list = os.listdir(files_path)
		matches = []
		for match in file_list:
			matches.append(''.join([letter for letter in match[:-4] if not letter.isdigit()]))
		
		unique_matches = np.unique(matches)

		day_data = []
		for match in unique_matches:
			day_data.append(self.load_match(match=match))
		
		return day_data

	def load_month(self):

		days = range(1,32)
		
		month_hist = {}
		for day in days:

			print("loading day %i" %day)
			day_str = "%s/%s/%s" %(self.year,self.month,day)
			self.date = day_str

			if os.path.exists(self.path + "/../" + day_str):
				day_data = self.load_one_day()
			else: 
				day_data = np.nan
			month_hist[day] = []
			month_hist[day].append(day_data)
		
		print month_hist.keys()
		return month_hist

	def dump_month(self):

		data = self.load_month()
		fout = open(self.path + '/' + self.year + "_" + self.month + '_month_data.json', "w")
		fout.write(json.dumps(data))

		fout.close()


if __name__ == "__main__":
	#dump_month(load_month("2018","9"))
	loader = data_loader("2018/10/6")
	loader.load_one_day()
	loader.dump_month()


