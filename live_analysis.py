import numpy as np
import sys


def simple_analysis(match_data):

	BP_weight = 0.2 # BallPossession weigth
	Att_weight = 1. # Attacks weight
	DAtt_weight = 2. # Dangerous Attacks
	SOnG_weight = 20. # ShotsOnGoal weight
	SOffG_weight = 10. # ShotsOffGoal weight
	Better_weight = 1. # how much better does a team have to be for a bet to be placed?

	HT_score = (float(match_data["stats"]["shots on target"][0]) * SOnG_weight + 
				float(match_data["stats"]["shots off target"][0]) * SOffG_weight + 
				float(match_data["stats"]["attacks"][0]) * Att_weight + 
				float(match_data["stats"]["dangerous attacks"][0]) * DAtt_weight)

	AT_score = (float(match_data["stats"]["shots on target"][1]) * SOnG_weight + 
				float(match_data["stats"]["shots off target"][1]) * SOffG_weight + 
				float(match_data["stats"]["attacks"][1]) * Att_weight + 
				float(match_data["stats"]["dangerous attacks"][1]) * DAtt_weight) 

	return HT_score, AT_score



































