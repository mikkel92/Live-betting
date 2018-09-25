import numpy as np
from scipy import interpolate

def spline_data(time_array,data_array):

	xvals_new = np.linspace(0,int(max(time_array)),20)
	
	spline_data = interpolate.InterpolatedUnivariateSpline(np.array(time_array),np.array(data_array))
	spline_vals = spline_data(np.array(time_array))
	
	print xvals_new, spline_vals
	return xvals_new, spline_vals
