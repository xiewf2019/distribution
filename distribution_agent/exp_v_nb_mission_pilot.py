from pilot_tache_distribution import*
from simulation import *
from util import *

import matplotlib.pyplot as plt

def experience(nb_pilot_range,expRange, seuil, workloadRange, recuperation, nb_mission_range,  prob_reussi, nb_exp, puni,  stra = True, insere = False, timeRange = [9,18],prob_tache = [7, 2.5, 0.5],relation_tache = True):
	mission_reussi = []
	mission_reussi2 = []
	mission_reussi3 = []
	mission_reussi4 = []
	for nb_pilot in nb_pilot_range:
		
		l11=[]
		l21=[]
		l31=[]
		l41=[]
		pilotPool = generatePilotPool(nb_pilot, expRange, seuil, workloadRange, recuperation)
		for nb_mission in nb_mission_range:
			l1=[]
			l2=[]
			l3=[]
			l4=[]
			for i in range(10):
				tachePool = generateTachePool(nb_mission, timeRange, prob_tache)
				pp = [copy.deepcopy(pilotPool) for i in range(4)]
				tp = [copy.deepcopy(tachePool) for i in range(4)]
				l1 += compterMission(DistributionSansRecuperation, simulation, pp[0], tp[0], prob_reussi, nb_exp, puni,  stra , insere, timeRange ,prob_tache ,relation_tache )[0]
				l2 += compterMission(DistributionAvecRecuperation, simulation, pp[1], tp[1], prob_reussi, nb_exp, puni, stra , insere, timeRange ,prob_tache ,relation_tache)[0]
				l3 += compterMission(chacunSesJob, simulation, pp[2], tp[2], prob_reussi, nb_exp, puni, stra , insere, timeRange ,prob_tache ,relation_tache)[0]
				l4 += compterMission(chacunSesJobAvecRecuperation, simulation, pp[3], tp[3], prob_reussi, nb_exp, puni, stra , insere, timeRange ,prob_tache ,relation_tache)[0]
			l11.append(l1)
			l21.append(l2)
			l31.append(l3)
			l41.append(l4)
		mission_reussi.append(l11)
		mission_reussi2.append(l21)
		mission_reussi3.append(l31)
		mission_reussi4.append(l41)
		
	mission = []
	mission.append(mission_reussi)
	mission.append(mission_reussi2)
	mission.append(mission_reussi3)
	mission.append(mission_reussi4)
	return mission