import numpy as np
from scipy import interpolate

def spline_data(time_array,data_array):

	# values where the spline is evaluated
	xvals_new = np.linspace(0,int(max(time_array)),100)
	
	# arange data in chronological order
	time = np.array(sorted(time_array))
	data = np.array(sorted(data_array))

	tck = interpolate.splrep(time, data)
	spline_vals = interpolate.splev(xvals_new, tck)
	
	#print(xvals_new, spline_vals)
	return xvals_new, spline_vals
