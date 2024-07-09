import random
from pilot_tache_distribution import *
import numpy as np
import copy 
import statistics as st


costcoef= [1,2,3]

def generateTachetime(nb, centre= 15, sigma = 3, borne_inf = 9, borne_sup= 25):
    mu = centre # mean
    n_samples = nb  # number of samples

    # Generate random numbers from a Gaussian distribution
    float_samples = np.random.normal(mu, sigma, n_samples)

    # Round to the nearest integer
    int_samples = np.round(float_samples).astype(int)
    for index, item in enumerate(int_samples):
        if item < borne_inf:
            int_samples[index] = borne_inf
        if item > borne_sup:
            int_samples[index] = borne_sup
    return int_samples

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
