from pilot_tache_distribution import*
from simulation import *
from util import *

import matplotlib.pyplot as plt

def experience(pilotPool, seuil, time_range,  prob_reussi, nb_exp, puni,  stra = True, insere = False, timeRange = [9,18],prob_tache = [7, 2.5, 0.5],relation_tache = True):
	mission_reussi = []
	mission_reussi2 = []
	mission_reussi3 = []
	mission_reussi4 = []
	listlen = []
	for t in time_range:
		l1=[]
		l2=[]
		l3=[]
		l4=[]
		l5=[]
		for i in range(10):
			pilotPool1 = pilotPool[:]
			AddIA(pilotPool1,10, seuil)
			tachePool = generateTacheAlter(t,timeRange)
			pp = [copy.deepcopy(pilotPool) for i in range(2)]
			pp1 = [copy.deepcopy(pilotPool1) for i in range(2)]
			tp = [copy.deepcopy(tachePool) for i in range(4)]

			l1 += compterMission(DistributionSansRecuperation, simulation, pp[0], tp[0], prob_reussi, nb_exp, puni,  stra , insere, timeRange ,prob_tache ,relation_tache )[0]
			l2 += compterMission(DistributionAvecRecuperationBas, simulation, pp[1], tp[1], prob_reussi, nb_exp, puni, stra , insere, timeRange ,prob_tache ,relation_tache)[0]
			l3 += compterMission(DistributionSansRecuperation, simulation, pp1[0], tp[2], prob_reussi, nb_exp, puni, stra , insere, timeRange ,prob_tache ,relation_tache)[0]
			l4 += compterMission(DistributionAvecRecuperationBas, simulation, pp1[1], tp[3], prob_reussi, nb_exp, puni, stra , insere, timeRange ,prob_tache ,relation_tache)[0]
			l5 += [len(tachePool) for i in range(nb_exp)] 
		mission_reussi.append(l1)
		mission_reussi2.append(l2)
		mission_reussi3.append(l3)
		mission_reussi4.append(l4)
		listlen.append(l5)

	mission = []
	mission.append(mission_reussi)
	mission.append(mission_reussi2)
	mission.append(mission_reussi3)
	mission.append(mission_reussi4)
	return mission, listlen

def affichage_moyen_stdev_v_time_mission(time_range, moyen, stdev, listAlgo):

	plt.figure(figsize=(10, 6))
	moyen_stdev=[]
	for i in range(len(moyen)):
	    plusstdev = [x+y for x, y in zip(moyen[i], stdev[i])]
	    moinstdev = [x-y for x, y in zip(moyen[i], stdev[i])]
	    moyen_stdev.append((plusstdev,moinstdev))
	# Définition des couleurs
	red_tones = ['#8B0000', '#FF0000', '#FF7F7F']  # Rouge foncé, Rouge, Rouge clair
	blue_tones = ['#00008B', '#0000FF', '#87CEFA']  # Bleu foncé, Bleu, Bleu clair
	green_tones = ['#006400', '#008000', '#00FF00']  # Vert foncé, Vert, Vert clair
	yellow_tones = ['#FFD700', '#FFFF00', '#FFFFE0']  # Or, Jaune, Jaune clair
	allcolor=[red_tones, blue_tones, green_tones, yellow_tones]
	for index,algo in enumerate(listAlgo):
		plt.plot(time_range, moyen[index], label=algo+' moyen'  , color=allcolor[index][0], marker='o')
		plt.plot(time_range, moyen_stdev[index][0], label=algo+' moyen+stdev'  , color=allcolor[index][1], marker='o')
		plt.plot(time_range, moyen_stdev[index][1], label=algo+' moyen-stdev'  , color=allcolor[index][2], marker='o')
	
	# Title and labels
	plt.title('moyen  et stdev avec 1000exp reussi avec different nombre de session !')
	plt.xlabel('time_mission')
	plt.ylabel('moyen de mission complet')

	# Legend
	plt.legend()
	plt.show()
def affichage_mission_complet(time_range, count_mission_complet, listAlgo):
	plt.figure(figsize=(10, 6))
	allcolor=['red','blue','green', 'yellow']
	for index,algo in enumerate(listAlgo):
		plt.plot(time_range, count_mission_complet[index], label=algo  , color=allcolor[index], marker='o')
		
	# Title and labels
	plt.title('mission complet avec 1000exp reussi avec different nombre de session DistributionAvecRecuperation!')
	plt.xlabel('time_mission')
	plt.ylabel('nb_des fois les pilot ont reussi tous les mission')

	# Legend
	plt.legend()

	# Display the plot
	plt.show()
	