import numpy as np
import os

def load_match(match,date):

	match_data = []
	files_path = "%s/../%s" % (os.getcwd(),date)
	file_list = os.listdir(files_path)
	
	for file in file_list:
		if match in file:

			data = open(files_path + "/" + file, "r").read()
			match_data.append(eval(data))

	return match_data

def load_one_day(date):

	files_path = "%s/../%s" % (os.getcwd(),date)
	file_list = os.listdir(files_path)
	matches = []
	for match in file_list:
		matches.append(''.join([letter for letter in match[:-4] if not letter.isdigit()]))
	
	unique_matches = np.unique(matches)

	day_data = []
	for match in unique_matches:
		day_data.append(load_match(match=match,date=date))
	
	return day_data


if __name__ == "__main__":
	load_one_day("2018/9/6")
