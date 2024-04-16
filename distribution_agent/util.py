import random
from pilot_tache_distribution import *
import numpy as np
import copy 
import statistics as st

#partie generation of pilot and tache 
costcoef= [1,2,3]
def generatePilot(expMax, expMin, seuil, workloadRange, recuperation):
    # Générer un pilote avec des caractéristiques aléatoires
    exp = random.uniform(0, 1)  # Générer un nombre aléatoire pour déterminer l'expérience
    # Assignation de l'expérience en fonction de l'intervalle défini
    if exp > 0.7:
        exp = random.randint(70, expMax)
    elif exp > 0.2:
        exp = random.randint(20, 70)
    else:
        exp = random.randint(0, 20)

    level = 0  # Détermination du niveau du pilote en fonction de l'expérience
    for index, item in enumerate(seuil):
        if exp > item:
            level = index

    workload = random.randint(workloadRange[0], workloadRange[1])  # Capacité de travail aléatoire
    r = recuperation  # Taux de récupération

    return pilot(exp, seuil, workload, r)  # Création d'un objet pilote




#generate from a fix length of tache and a range of time
def generateTachePool(length, timeRange,prob_tache = [0.2, 0.5, 0.3]):
    random_level = random.choices([0,1,2], prob_tache, k= length)
    random_duration = [random.randint(timeRange[0], timeRange[1]) for _ in range(length)]
    cost = 0
    #costcoef = [1,2,3]
    timeTotal = 0
    tachePool = []
    for i in range(length):
        level = random_level[i]
        td = timeTotal
        duration = random_duration[i]
        cost = costcoef[level]*random_duration[i]
        tt = td + duration
        tachePool.append(tache(level, cost, td, duration, tt))
        timeTotal = tt
    return tachePool

def generatePilotPool(nb_pilot, expRange, seuil, workloadRange, recuperation):
    # Générer un ensemble de pilotes
    pilotPool = []
    for i in range(nb_pilot):
        # Création de chaque pilote avec des caractéristiques aléatoires
        pilotPool.append(generatePilot(expRange[1], expRange[0], seuil, workloadRange, recuperation))
    return pilotPool  # Retourne la liste des pilotes


def generatePilotTache(nb_pilot, expRange, seuil, workloadRange, recuperation, nb_mission, timeRange, prob_tache=[0.2, 0.5, 0.3]):
    # Générer des ensembles de pilotes et de tâches
    tachePool = generateTachePool(nb_mission, timeRange, prob_tache)  # Création des tâches
    pilotPool = []
    for i in range(nb_pilot):
        # Création des pilotes
        pilotPool.append(generatePilot(expRange[1], expRange[0], seuil, workloadRange, recuperation))
    return pilotPool, tachePool  # Retourne les listes des pilotes et des tâches

def generateFixPilot(exps, seuil, workloads, recuperation):
    # Générer des pilotes avec des expériences et charges de travail fixes
    pilotPool = []
    for exp, workload in zip(exps, workloads):
        # Création de chaque pilote avec des caractéristiques fixes
        pilotPool.append(pilot(exp, seuil, workload, recuperation))
    return pilotPool  # Retourne la liste des pilotes

def AddIA(pilotPool, exp, seuil):
    # Ajouter un pilote IA (Intelligence Artificielle) au pool de pilotes
    workload = 10000000000  # Charge de travail très élevée pour simuler une capacité quasi infinie
    pilotPool.append(pilot(exp, seuil, workload, 10, 1))  # Création du pilote IA et ajout au pool

def generateFixTimeTache(timeTotal, timeRange, prob_tache=[8, 1.5, 0.5]):
    # Générer un ensemble de tâches avec une durée totale fixe
    start = 0
    tacheFixe = []
    while start < timeTotal:
        t = random.randint(timeRange[0], timeRange[1])  # Durée aléatoire de la tâche
        level = random.choices([0, 1, 2], prob_tache, k=1)[0]  # Niveau aléatoire de la tâche
        
        tacheFixe.append((t, level))  # Ajouter la tâche à la liste
        start += t  # Mise à jour du temps de départ pour la prochaine tâche

    return tacheFixe  # Retourner la liste des tâches

def generateFixNbTache(n, timeTable, prob_tache = [8, 1.5, 0.5]):
    fixset =[]
    levels = random.choices([0, 1, 2], prob_tache, k=n)
    for t,l in zip(timeTable,levels):
        fixset.append((t,l))
    return fixset


def generateTacheFromFixSet(fixset):
    # Générer des tâches à partir d'un ensemble fixe
    taches = []
    for t, l in fixset:
        cost = t *  costcoef[l]  # Calculer le coût de la tâche
        taches.append(tache(l, cost, 0, t, t))  # Créer et ajouter la tâche à la liste

    return taches  # Retourner la liste des tâches


def shuffleTache(tacheList):
    # Mélanger aléatoirement l'ordre des tâches
    newTache = tacheList[:]  # Copie de la liste des tâches
    random.shuffle(newTache)  # Mélanger la liste
    return newTache  # Retourner la liste mélangée

def resetTdtt(tacheList):
    # Réinitialiser les temps de départ et de fin pour chaque tâche
    for i, ta in enumerate(tacheList):
        if i != 0:
            ta.td = tacheList[i - 1].tt  # Définir le temps de départ en fonction de la tâche précédente
            ta.tt = ta.td + ta.duration  # Calculer le temps de fin

def generateTacheAlter(ttotal, tr,prob_tache=[8, 1.5, 0.5]):
    # Générer des tâches avec un temps total et les mélanger
    tf = generateFixTimeTache(ttotal, tr, prob_tache )  # Générer un ensemble fixe de tâches
    taches = generateTacheFromFixSet(tf)  # Créer des tâches à partir de l'ensemble fixe
    nt = shuffleTache(taches)  # Mélanger les tâches
    resetTdtt(nt)  # Réinitialiser les temps de départ et de fin

    return nt  # Retourner les tâches mélangées

def generateTacheNb(nb, timeTable, prob_tache=[8, 1.5, 0.5] ):
    tf = generateFixNbTache(nb, timeTable,prob_tache)  # Générer un ensemble fixe de tâches
    taches = generateTacheFromFixSet(tf)  # Créer des tâches à partir de l'ensemble fixe
    nt = shuffleTache(taches)  # Mélanger les tâches
    resetTdtt(nt)  # Réinitialiser les temps de départ et de fin

    return nt

# get statistique de la simulation en augument les longueur de tache en  chaque etape
def getStat(mission, step = 2, start = 15):
    moyen = []
    stdev = []
    median = []
    mode = []
    max_m = []
    min_m = []
    count_mission_complet = []
    for i in range(len(mission)):
        moyen.append([])
        stdev.append([])
        median.append([])
        mode.append([])
        max_m.append([])
        min_m.append([])
        count_mission_complet.append([])
    for algo, item in enumerate(mission):
            for i,t in enumerate(item):
                moyen[algo].append(st.mean(t))
                median[algo].append(st.median(t))
                mode[algo].append(st.mode(t))
                stdev[algo].append(st.stdev(t))
                max_m[algo].append(max(t))
                min_m[algo].append(min(t))
                count_mission_complet[algo].append(t.count(i*step+start))
    return moyen, stdev, max_m, min_m, count_mission_complet,median, mode
# get statistique de la simulation en augument les longueur de tache en  chaque etape  en le augmentation de pilot
def getStatdiff(mission, step = 2, start =5):
    moyen = []
    stdev = []
    median = []
    mode = []
    max_m = []
    min_m = []
    count_mission_complet = []
    for i in range(len(mission)):
        moyen.append([])
        stdev.append([])
        median.append([])
        mode.append([])
        max_m.append([])
        min_m.append([])
        count_mission_complet.append([])
    for algo, items in enumerate(mission):
        for index, item in enumerate(items):
            moyen[algo].append([])
            median[algo].append([])
            mode[algo].append([])
            stdev[algo].append([])
            max_m[algo].append([])
            min_m[algo].append([])
            count_mission_complet[algo].append([])
            for i,t in enumerate(item):
                moyen[algo][index].append(st.mean(t))
                median[algo][index].append(st.median(t))
                mode[algo][index].append(st.mode(t))
                stdev[algo][index].append(st.stdev(t))
                max_m[algo][index].append(max(t))
                min_m[algo][index].append(min(t))
                count_mission_complet[algo][index].append(t.count(i*step+start))
    return moyen, stdev, max_m, min_m, count_mission_complet,median, mode

def getStatAlter(m,l):
    moyen, stdev, max_m, min_m, count_mission_complet, median, mode= getStat(m)
    mission = m
    count_mission_complet = []
    for i in range(len(mission)):
        count_mission_complet.append([])
    for algo, item in enumerate(mission):
            for i,t in enumerate(item):
                nombre = sum(e1 >= e2 for e1, e2 in zip(t, l[i]))
                count_mission_complet[algo].append(nombre)
    return moyen, stdev, max_m, min_m, count_mission_complet, median, mode