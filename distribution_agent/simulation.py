import random
import copy 
from pilot_tache_distribution import *

#todo tache  cost a modifier 
def compterMission(funcDistribu, simu, agentPool, tachePool, prob_reussi, nb_exp, puni, stra=True, insere=False, timeRange=[9, 18], prob_tache=[7, 2.5, 0.5], relation_tache=True):
    # Compter le nombre de missions réussies et le nombre total de missions
    # Création de copies des pools d'agents et de tâches pour simulation
    ap = copy.deepcopy(agentPool)
    tp = copy.deepcopy(tachePool)

    # Appliquer la fonction de distribution aux copies
    funcDistribu(ap, tp)

    # Exécution de la simulation pour compter les missions
    nb_mission, nb_mission_ai = simu(ap, tp, prob_reussi, nb_exp, puni, stra, insere, timeRange, prob_tache, relation_tache)
    return nb_mission, nb_mission_ai

def updateAgentWorkloadActuelleAvant(agent, tache, methode):
    # Mise à jour de la charge de travail actuelle de l'agent avant de réaliser une tâche
    time = tache.td - agent.t
    agent.workloadActuelle = recup_calcul(agent,time, methode) + agent.workloadActuelle
    agent.t = tache.td


def updateAgentWorkloadActuelleApres(agent, tache):
    # Mise à jour de la charge de travail actuelle de l'agent après avoir réalisé une tâche
    agent.workloadActuelle = agent.workloadActuelle - tache.cost
    agent.t = tache.tt


def faireTache(agent, prob_reussi, tache, puni):
    # Déterminer si une tâche est réussie par un agent
    levelpilot = agent.level
    leveltache = tache.level
    
    # Calcul de la probabilité de réussite
    prob = prob_reussi[levelpilot][leveltache]
    if agent.workloadActuelle < tache.cost:
        prob *= puni  # Ajustement de la probabilité en cas de surcharge de travail

    probs = [prob, 1 - prob]
    
    # Mise à jour de la charge de travail après la tâche
    updateAgentWorkloadActuelleApres(agent, tache)

    # Détermination du succès ou de l'échec de la tâche
    reussi = random.choices([True, False], weights=probs, k=1)[0]
    return reussi


def generateTacheHasard(timeRange=[9, 18], prob_tache=[7, 2.5, 0.5]):
    # Générer une tâche aléatoire
    level = random.choices([0, 1, 2], prob_tache, k=1)[0]  # Sélection aléatoire du niveau
    duration = random.randint(timeRange[0], timeRange[1])  # Durée aléatoire
    costcoef = [1, 2, 3]
    cost = costcoef[level] * duration  # Calcul du coût
    td = 0  # Temps de départ initialisé à 0
    tt = 0  # Temps de terminie initialisé à 0
    return tache(level, cost, td, duration, tt)
def traiteTacheHasard(ap, tp, prob_reussi, tabAgent, tache, puni, relation_tache, methode):
    # Traitement d'une tâche aléatoire parmi les agents
    missionfailed = False  # Indicateur d'échec de la mission
    tache.cost = tache.cost + tache.duration  # Mise à jour du coût de la tâche

    tabNonAdapter = []  # Liste des agents non adaptés pour la tâche
    reussi = False  # Indicateur de réussite de la tâche

    for p in range(len(ap)):
        agent = ap[tabAgent[p][0]]  # Sélection de l'agent
        updateAgentWorkloadActuelleAvant(agent, tache, methode)  # Mise à jour de la charge de travail avant la tâche
        recup = recup_calcul(agent, tache.duration, methode)
        tache.cost = tache.cost + recup
        agent.workloadActuelle = recup + agent.workloadActuelle  # Calcul de la charge de travail actuelle
        
        # Vérifier si l'agent est apte à réaliser la tâche
        if agent.level >= tache.level and tache.cost < agent.workloadActuelle and not reussi:
            if len(agent.tache) == 0:
                # Si l'agent n'a pas de tâche prévue, tenter de réaliser la tâche
                reussi = faireTache(agent, prob_reussi, tache, puni)
                if reussi:
                    break  # Sortir de la boucle si la tâche est réussie
            else:
                # Calculer la possibilité d'insérer la tâche parmi les tâches existantes
                x1 = agent.r * (tp[agent.tache[0]].td - tache.td) + agent.workloadActuelle - tache.cost
                if tp[agent.tache[0]].wn < x1:
                    # Tenter de réaliser la tâche si possible
                    reussi = faireTache(agent, prob_reussi, tache, puni)
                    if reussi:
                        break  # Sortir de la boucle si la tâche est réussie
                else: 
                    # Ajouter l'agent à la liste des agents non adaptés
                    tabNonAdapter.append(tabAgent[p][0])
        else:
            # Ajouter l'agent à la liste des agents non adaptés si les conditions ne sont pas remplies
            tabNonAdapter.append(tabAgent[p][0])
        tache.cost = tache.cost - recup
    # Gestion de l'échec de la tâche
    if not reussi:
        if relation_tache:
            missionfailed = True  # Marquer la mission comme échouée si la relation de tâche est active
        # Réajuster la charge de travail pour les agents non adaptés
        for p in tabNonAdapter:
            recup = recup_calcul(agent, tache.duration, methode)
            agent.workloadActuelle = -recup + agent.workloadActuelle

    return missionfailed  # Retourner l'état d'échec de la mission



def traiteTache(ap, tp, prob_reussi,tabAgent, tache, puni, mission_reussi_per_exp, mission_reussi_per_exp_ai, index, methode):
    reussi = False
    if tache.pilot != -1:
        agent = ap[tache.pilot]
        updateAgentWorkloadActuelleAvant(agent, tache, methode)
        reussi = faireTache(agent, prob_reussi, tache, puni)
        ap[tache.pilot].tache.remove(index)
        if reussi:
            mission_reussi_per_exp += 1
            if agent.nature >0:
                mission_reussi_per_exp_ai += 1
    if not reussi:
        tabOverload= []
        #let the pilot who has extra workload to work before
        for p in range(len(ap)):
            agent = ap[tabAgent[p][0]]
            updateAgentWorkloadActuelleAvant(agent, tache, methode)
            if agent.level >= tache.level and tabAgent[p] != tache.pilot:
                if tache.cost < agent.workloadActuelle:
                    if len(agent.tache) == 0:
                        reussi = faireTache(agent,prob_reussi, tache, puni)
                        if reussi:
                            mission_reussi_per_exp += 1
                            if agent.nature >0:
                                mission_reussi_per_exp_ai += 1
                            break
                    else:
                        time = tp[agent.tache[0]].td - tache.tt
                        recup = recup_calcul(agent,time, methode)
                        x1 = recup + agent.workloadActuelle - tache.cost
                        if tp[agent.tache[0]].wn < x1 :
                            reussi = faireTache(agent,prob_reussi, tache, puni)
                            if reussi:
                                mission_reussi_per_exp += 1
                                if agent.nature >0:
                                    mission_reussi_per_exp_ai += 1
                                break
                        else:
                            tabOverload.append(tabAgent[p][0])
                else:
                    tabOverload.append(tabAgent[p][0])
                
        if not reussi and len(tabOverload) != 0:
            for index in tabOverload:
                agent = ap[index]
                reussi = faireTache(agent,prob_reussi, tache, puni)
                if reussi:
                    mission_reussi_per_exp += 1
                    if agent.nature >0:
                        mission_reussi_per_exp_ai += 1
                    break
    return reussi, mission_reussi_per_exp, mission_reussi_per_exp_ai

def simulation(ap, tp, prob_reussi, nb_exp, puni=0.5, stra=True, insere=False, timeRange=[9, 18], prob_tache=[7, 2.5, 0.5], relation_tache=True, methode = "lineaire"):
    # Fonction pour simuler la réalisation de tâches par des agents
    mission_reussi = []  # Liste pour enregistrer le nombre de missions réussies par expérience
    mission_ai = []  # Liste pour enregistrer le nombre de missions réussies par des agents AI

    for i in range(nb_exp):
        # Initialisation des compteurs pour chaque expérience
        mission_reussi_per_exp = 0
        mission_reussi_per_exp_ai = 0
        ap_copy = copy.deepcopy(ap)  # Copie de la liste des agents
        tp_copy = copy.deepcopy(tp)  # Copie de la liste des tâches
        tabAgent = []  # Liste pour trier les agents
        missionfailed = False  # Indicateur d'échec de la mission

        # Préparation de la liste des agents
        for j in range(len(ap_copy)):
            level = ap_copy[j].level
            exp = ap_copy[j].exp
            tabAgent.append((j, exp))
        tabAgent.sort(key=lambda x: x[1], reverse=stra)  # Trier les agents selon leur expérience

        # Initialisation du temps pour chaque agent
        for a in ap_copy:
            a.t = 0
        reussi = False

        # Traitement des tâches
        for index, tache in enumerate(tp_copy):
            if missionfailed:
                break  # Arrêter la simulation en cas d'échec de mission

            # Générer une tâche aléatoire si nécessaire
            if insere:
                if random.random() > 0.7:
                    reussi = False
                    tache_hasard = generateTacheHasard(timeRange, prob_tache)
                    tache_hasard.td = tache.td
                    missionfailed = traiteTacheHasard(ap_copy, tp_copy, prob_reussi, tabAgent, tache_hasard, puni, relation_tache, methode)
                if missionfailed:
                    break

            # Traitement de la tâche courante
            reussi, mission_reussi_per_exp, mission_reussi_per_exp_ai = traiteTache(ap_copy, tp_copy, prob_reussi, tabAgent, tache, puni, mission_reussi_per_exp, mission_reussi_per_exp_ai, index, methode)
            if not reussi:
                missionfailed = True  # Marquer l'échec de la mission si la tâche n'est pas réussie

        # Enregistrement des résultats de l'expérience
        mission_reussi.append(mission_reussi_per_exp)
        mission_ai.append(mission_reussi_per_exp_ai)

    return mission_reussi, mission_ai
