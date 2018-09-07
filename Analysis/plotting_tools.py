import matplotlib.pyplot as plt
import numpy as np
from data_loader import load_match

def plot_match_data(match_data):

	time = [float(i["time"][0].replace(':','')) for i in match_data]
	attacks_home = [i["stats"]["attacks"][0] for i in match_data]
	attacks_away = [i["stats"]["attacks"][1] for i in match_data]
	
	plt.plot(time,attacks_home,'.',label="home")
	plt.plot(time,attacks_away,'.',label="away")
	plt.xlabel("time [wierd unit]")
	plt.xlim(0,max(time) + 200)
	plt.ylabel("attacks")
	plt.legend()
	plt.grid()
	plt.show(block=False)
	raw_input('...')

	plt.close_all()


if __name__ == "__main__":
	plot_match_data(load_match("ABOB","2018/9/6"))