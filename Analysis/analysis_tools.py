import numpy as np
from scipy import interpolate

def spline_data(time_array,data_array):

	# values where the spline is evaluated
	time_new = np.linspace(0,10000,21)
	
	# arange data in chronological order
	time = np.array(time_array)
	data = np.array(data_array)

	#tck = interpolate.splrep(time, data)
	#spline_vals = interpolate.splev(time_new, tck)
	tck = interpolate.PchipInterpolator(time, data)
	spline_vals = tck(time_new)

	#print(time_new, spline_vals)
	return time_new, spline_vals

