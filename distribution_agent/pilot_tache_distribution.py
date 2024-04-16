import numpy as np
import math
import random
class pilot:
    def __init__(self, exp, seuil, workload, r=0, nature=0):
        # Initialisation du pilote avec son expérience, les seuils, la charge de travail, et les paramètres optionnels r et nature
        self.exp = exp  # Niveau d'expérience du pilote
        self.workload = workload  # Capacité de charge de travail initiale du pilote
        self.level = 0  # Niveau du pilote, qui sera déterminé en fonction de l'expérience et des seuils

        # Boucle pour déterminer le niveau du pilote en fonction de son expérience et des seuils
        for i in range(len(seuil) - 1, -1, -1):
            if exp >= seuil[i]:
                self.level = i  # Mise à jour du niveau du pilote
                break

        self.tache = []  # Liste des tâches assignées au pilote

        self.r = r  # vitesse de recuperation lineaire
        self.r_a = 0 #vitesse recup quad
        self.r_b = 0 #vitesse recuo lineaire
        self.latency = 0
        self.capacite = workload  # Capacité actuelle de travail du pilote (peut être modifiée au cours du temps)
        self.t = 0  # Paramètre temporel (son utilisation doit être clarifiée)
        self.workload_est = 0
        self.needUpdate = False  # Indicateur pour déterminer si une mise à jour est nécessaire
        self.updatePoint = 0  # Point de mise à jour (doit être défini dans un contexte spécifique)
        
        self.miu = 0.0096 #valeur suppose dans l'article A task scheduling model integrating micro-breaks for optimisation of job-cycle time in human-robot collaborative assembly cells
        # Utilisé pour la simulation
        self.workloadActuelle = workload  # Charge de travail actuelle du pilote
        self.nature = nature  # Nature du pilote (O pour humain 1 pour IA)


    def __str__(self):
        return (f"Pilot(exp={self.exp}, level={self.level}, workload={self.workload}, "
                f"tache={self.tache}, r={self.r}, capacite={self.capacite}, "
                f"t={self.t}, needUpdate={self.needUpdate}, updatePoint={self.updatePoint},"
               f"nature={self.nature})")



class tache:
    def __init__(self, level, cost, td=0, duration=0, tt=0, weight=1, relation=1):
        # Initialisation de la tâche avec différents paramètres définissant ses caractéristiques
        self.cost = cost  # Coût de la tâche
        self.level = level  # Niveau requis pour effectuer la tâche
        self.pilot = -1  # Identifiant du pilote assigné à la tâche, -1 signifie qu'aucun pilote n'est assigné
        
        self.td = td  # Délai avant le début de la tâche
        self.duration = duration  # Durée de la tâche
        self.tt = tt  # Temps total associé à la tâche

        # Intérêt de cette mission
        self.weight = weight  # Poids ou importance de la tâche

        # Relation de cette tâche avec le segment
        # Si relation = 1, échouer dans cette tâche signifie échouer dans la mission
        # Si relation = 0, il est possible d'ignorer cette tâche et de continuer avec les suivantes
        self.relation = relation
        
        self.wr = 0  # workload rest estime apres cette mission
        self.wn = 0  # workload necessaire estime apres cette mission
        
    def __str__(self):
        # Méthode pour retourner une représentation textuelle de la tâche
        return (f"Tache(level={self.level}, cost={self.cost}, pilot={self.pilot}, "
                f"td={self.td}, duration={self.duration}, tt={self.tt}, "
                f"wr={self.wr}, wn={self.wn}, weight={self.weight}, relation={self.relation})")





sizeDiff = 3

def generateTabdiff(agentsPool, tachePool, sizeDiff=3):
    # Génération de deux tableaux basés sur les niveaux des agents et des tâches
    # agentsPool : liste des agents (pilotes)
    # tachePool : liste des tâches
    # sizeDiff : nombre de niveaux différents (par défaut à 3)

    tabAgent = []  # Tableau pour stocker les agents triés par niveau
    tabTache = []  # Tableau pour stocker les tâches triées par niveau

    # Initialisation des sous-tableaux pour chaque niveau
    for i in range(sizeDiff):
        tabAgent.append([])
        tabTache.append([])

    # Parcours de la liste des agents pour les classer par niveau
    for j in range(0, len(agentsPool)):
        level = agentsPool[j].level  # Niveau de l'agent
        exp = agentsPool[j].exp  # Expérience de l'agent
        tabAgent[level].append((j, exp))  # Ajout de l'agent et de son expérience au tableau correspondant à son niveau

    # Parcours de la liste des tâches pour les classer par niveau
    for t in range(0, len(tachePool)):
        level = tachePool[t].level  # Niveau requis pour la tâche
        tabTache[level].append(t)  # Ajout de la tâche au tableau correspondant à son niveau

    return tabAgent, tabTache  # Retourne les deux tableaux organisés

def DistributionSansRecuperation(agentsPool, tachePool):
    # Distribution des tâches parmi les agents sans possibilité de récupération de la charge de travail
    # agentsPool : liste des agents (pilotes)
    # tachePool : liste des tâches

    sizeDiff = 3  # Nombre de niveaux différents pour les agents et les tâches
    tabAgent, tabTache = generateTabdiff(agentsPool, tachePool)  # Générer des tableaux organisés par niveau
    tabOverworkload = [0, 0, 0]  # Tableau pour suivre les surcharges de travail par niveau

    # Parcours des niveaux de plus haut à plus bas
    for i in range(sizeDiff - 1, -1, -1):
        # Tri des agents par expérience (du plus expérimenté au moins expérimenté)
        tabAgent[i].sort(key=lambda x: x[1], reverse=True)

        for tup in tabAgent[i]:
            supprimeList = []  # Liste pour stocker les tâches attribuées

            # Attribution des tâches aux agents en fonction de leur capacité de travail restante
            for t in tabTache[i]:
                agent = agentsPool[tup[0]]
                tache = tachePool[t]
                cost = consoTache(agent,tache )
                if agent.workload > cost:
                    agent.tache.append(t)  # Ajouter la tâche à l'agent
                    tache.pilot = tup[0]  # Assigner l'agent à la tâche
                    agent.workload -= cost  # Réduire la charge de travail de l'agent
                    supprimeList.append(t)  # Ajouter la tâche à la liste des tâches attribuées

            # Retirer les tâches attribuées du pool de tâches
            for s in supprimeList:
                tabTache[i].remove(s)

        # Gestion des tâches restantes en cas de surcharge de travail
        if len(tabTache[i]) > 0:
            tabOverworkload[i] = len(tabTache[i])  # Mise à jour du tableau de surcharge
            count = 0
            size_a = len(tabAgent[i])  # Nombre d'agents dans le niveau actuel

            # Répartition des tâches restantes entre les agents
            if size_a != 0:
                for t in tabTache[i]:
                    agentsPool[tabAgent[i][count % size_a][0]].tache.append(t)
                    tachePool[t].pilot = tabAgent[i][count % size_a][0]
                    agentsPool[tabAgent[i][count % size_a][0]].workload = 0
                    count += 1
                    
        # Redistribution des agents avec de la capacité restante vers le niveau inférieur
        for tup in tabAgent[i]:
            if agentsPool[tup[0]].workload > 0 and i > 0:
                tabAgent[i - 1].append(tup)

    # Mise à jour finale des charges de travail nécessaires
    for i in range(sizeDiff - 1, -1, -1):
        for tup in tabAgent[i]:
            updateWorkloadNecessaire(agentsPool[tup[0]], tachePool)

    return tabOverworkload  # Retourne le tableau des surcharges de travail par niveau
def DistributionAvecRecuperation(agentsPool, tachePool):
    # Fonction pour attribuer les tâches aux agents en tenant compte de la récupération de la charge de travail
    # agentsPool : liste des agents (pilotes)
    # tachePool : liste des tâches
    tabAgent, tabTache = generateTabdiff(agentsPool, tachePool, sizeDiff)
    tabOverworkload = [0,0,0]
    # Traitement des agents et tâches par niveau, en commençant par le plus élevé
    for i in range(sizeDiff-1,-1,-1):
        tabAgent[i].sort(key=lambda x: x[1], reverse =True)
        #atrribue les tache a priori aux user plus experimente
        for j in range(sizeDiff-1, i,-1):
            for tup in tabAgent[j]:
                supprimeList = []
                for t in tabTache[i]:
                    agent = agentsPool[tup[0]]
                    tache = tachePool[t]
                    cost = consoTache(agent,tache )

                    #is 1 is2 l'indcie dans agent.tache
                    #indexs1 , indexs2 l'indice dans tachepool
                    # Trouver les segments de tâches entourant la tâche actuelle
                    is1, is2, indexs1, indexs2 = findSegementAutour(agent,t)
                    #enfonction de is1 et is2 on change facon de juge comment ajouter le tache
                    #si is1 = -1 et is2 = -1 alor le tache il est vide 
                    #si is1 = -1 alors le point il est bien devant tout les tache 
                    #si is2 =- 1 alors le point il est bien derrier tout les tache 
                    if is1 == -1 and is2 == -1:
                        if min(agent.workload + agent.r*(tache.td - agent.t), agent.capacite) > cost:
                            tache.pilot = tup[0]
                            agent.workload = min(agent.workload + agent.r*(tache.td - agent.t), agent.capacite) - cost
                            agent.t = tache.tt
                            supprimeList.append(t)
                            tache.wr = agent.workload
                            
                    elif is1 == -1:
                        s2 = tachePool[indexs2]
                        x2 = agent.capacite - cost +agent.r*(s2.td- tache.tt)
                        if agent.capacite > cost and s2.wn<= x2 :
                            tache.pilot = tup[0]
                            supprimeList.append(t)
                            tache.wr = agent.capacite- cost
                            agent.needUpdate = True
                            agent.updatePoint = is2
                            costS2 = consoTache(agent,s2 )
                            s2.wr = min(x2, agent.capacite) - costS2
                            
                    elif is2 == -1:
                        s1 = tachePool[indexs1]
                        if len(supprimeList) > 0:
                            if(supprimeList[-1] > indexs1):
                                s1 = tachePool[supprimeList[-1]]
                            x1 = min(s1.wr + agent.r*(tache.td - s1.tt), agent.capacite)
                            if x1 >= cost:
                                tache.pilot = tup[0]
                                supprimeList.append(t)
                                tache.wr = x1 - cost
                                agent.needUpdate = False
                                
                    else:
                        s1 = tachePool[indexs1]
                        s2 = tachePool[indexs2]
                        if agent.needUpdate and is1 > agent.updatePoint:
                            updateWorkloadRest(agent, is1, tachePool)
                        if len(supprimeList) > 0:
                            if(supprimeList[-1] > indexs1):
                                s1 = tachePool[supprimeList[-1]]
                                
                        tache = tachePool[t]
                        x1 = min(s1.wr + agent.r*(tache.td - s1.tt), agent.capacite) 
                        x2 = min(s1.wr + agent.r*(tache.td - s1.tt), agent.capacite) - cost +agent.r*(s2.td- tache.tt)
                        if x1 >= cost and s2.wn <= x2:
                            tache.pilot = tup[0]
                            agent.t = tache.tt
                            supprimeList.append(t)
                            tache.wr = min(s1.wr + agent.r*(tache.td - s1.tt), agent.capacite) - cost
                            costS2 = consoTache(agent,s2)
                            s2.wr = min(tache.wr +agent.r*(s2.td- tache.tt), agent.capacite) - costS2
                            agent.needUpdate = True
                            agent.updatePoint = is2
                # Retirer les tâches attribuées de la liste de tâches disponibles
                for s in supprimeList:
                    tabTache[i].remove(s)
                    agent.tache.append(s)
        # Attribution des tâches restantes aux agents du même niveau 
        for tup in tabAgent[i]:
            supprimeList = []
            for t in tabTache[i]:
                agent = agentsPool[tup[0]]
                tache = tachePool[t]
                cost = consoTache(agent,tache )
                if min(agent.workload + agent.r*(tache.td - agent.t), agent.capacite) > cost:
                    agent.tache.append(t)
                    tache.pilot = tup[0]
                    agent.workload = min(agent.workload + agent.r*(tache.td - agent.t), agent.capacite) - cost
                    agent.t = tache.tt
                    supprimeList.append(t)
                    tache.wr = agent.workload
            for s in supprimeList:
                tabTache[i].remove(s)
        if len(tabTache[i]) > 0:
            tabOverworkload[i] = len(tabTache[i])
            count = 0
            size_a = len(tabAgent[i])
            if size_a != 0:
                for t in tabTache[i]:
                    agentsPool[tabAgent[i][count%size_a][0]].tache.append(t)
                    tachePool[t].pilot = tabAgent[i][count%size_a][0]
                    agentsPool[tabAgent[i][count%size_a][0]].workload = 0
                    count = count +1
        for j in range(sizeDiff-1, i-1,-1):
            for tup in tabAgent[j]:
                updateWorkloadNecessaire(agentsPool[tup[0]],tachePool)
    return tabOverworkload     

def chacunSesJob(agentsPool, tachePool):
    # Fonction pour distribuer les tâches aux agents en fonction de leur niveau et capacité de travail
    # agentsPool : liste des agents (pilotes)
    # tachePool : liste des tâches

    # Générer des tableaux d'agents et de tâches organisés par niveau
    tabAgent, tabTache = generateTabdiff(agentsPool, tachePool, sizeDiff)
    tabOverworkload = [0, 0, 0]  # Tableau pour suivre les surcharges de travail par niveau

    # Parcours des niveaux de plus haut à plus bas
    for i in range(sizeDiff - 1, -1, -1):
        # Tri des agents par expérience (du plus expérimenté au moins expérimenté)
        tabAgent[i].sort(key=lambda x: x[1], reverse=True)

        for tup in tabAgent[i]:
            supprimeList = []  # Liste pour stocker les tâches attribuées

            # Attribution des tâches aux agents en fonction de leur capacité de travail restante
            for t in tabTache[i]:
                agent = agentsPool[tup[0]]
                tache = tachePool[t]
                cost = consoTache(agent,tache )
                if agent.workload > cost:
                    agent.tache.append(t)  # Ajouter la tâche à l'agent
                    tache.pilot = tup[0]  # Assigner l'agent à la tâche
                    agent.workload -= cost  # Réduire la charge de travail de l'agent
                    supprimeList.append(t)  # Ajouter la tâche à la liste des tâches attribuées

            # Retirer les tâches attribuées du pool de tâches
            for s in supprimeList:
                tabTache[i].remove(s)

        # Gestion des tâches restantes en cas de surcharge de travail
        if len(tabTache[i]) > 0:
            tabOverworkload[i] = len(tabTache[i])  # Mise à jour du tableau de surcharge
            count = 0
            size_a = len(tabAgent[i])  # Nombre d'agents dans le niveau actuel

            # Répartition des tâches restantes entre les agents
            if size_a != 0:
                for t in tabTache[i]:
                    agentsPool[tabAgent[i][count % size_a][0]].tache.append(t)
                    tachePool[t].pilot = tabAgent[i][count % size_a][0]
                    agentsPool[tabAgent[i][count % size_a][0]].workload = 0
                    count += 1

    # Mise à jour finale des charges de travail nécessaires
    for i in range(sizeDiff - 1, -1, -1):
        for tup in tabAgent[i]:
            updateWorkloadNecessaire(agentsPool[tup[0]], tachePool)

    return tabOverworkload  # Retourne le tableau des surcharges de travail par niveau
    
def chacunSesJobAvecRecuperation(agentsPool, tachePool):
    # Fonction pour distribuer les tâches aux agents avec possibilité de récupération de la charge de travail
    # agentsPool : liste des agents (pilotes)
    # tachePool : liste des tâches

    # Générer des tableaux d'agents et de tâches organisés par niveau
    tabAgent, tabTache = generateTabdiff(agentsPool, tachePool, sizeDiff)
    tabOverworkload = [0, 0, 0]  # Tableau pour suivre les surcharges de travail par niveau

    # Parcours des niveaux de plus haut à plus bas
    for i in range(sizeDiff - 1, -1, -1):
        # Tri des agents par expérience (du plus expérimenté au moins expérimenté)
        tabAgent[i].sort(key=lambda x: x[1], reverse=True)

        for tup in tabAgent[i]:
            supprimeList = []  # Liste pour stocker les tâches attribuées

            # Attribution des tâches en tenant compte de la récupération de la charge de travail
            for t in tabTache[i]:
                agent = agentsPool[tup[0]]
                tache = tachePool[t]
                cost = consoTache(agent,tache )
                # Calcul de la charge de travail disponible avec récupération
                workloadDisponible = min(agent.workload + agent.r * (tache.td - agent.t), agent.capacite)

                if workloadDisponible > cost:
                    agent.tache.append(t)  # Ajouter la tâche à l'agent
                    tache.pilot = tup[0]  # Assigner l'agent à la tâche
                    agent.workload = workloadDisponible - cost  # Mise à jour de la charge de travail
                    agent.t = tache.tt  # Mise à jour du temps de l'agent
                    tache.wr = agent.workload  # Mise à jour de la charge de travail restante pour la tâche
                    supprimeList.append(t)  # Ajouter la tâche à la liste des tâches attribuées

            # Retirer les tâches attribuées du pool de tâches
            for s in supprimeList:
                tabTache[i].remove(s)

        # Gestion des tâches restantes en cas de surcharge de travail
        if len(tabTache[i]) > 0:
            tabOverworkload[i] = len(tabTache[i])  # Mise à jour du tableau de surcharge
            count = 0
            size_a = len(tabAgent[i])  # Nombre d'agents dans le niveau actuel

            # Répartition des tâches restantes entre les agents
            if size_a != 0:
                for t in tabTache[i]:
                    agent = agentsPool[tabAgent[i][count % size_a][0]]
                    agent.tache.append(t)
                    tachePool[t].pilot = agent
                    agent.workload = 0  # Remise à zéro de la charge de travail
                    count += 1

        # Mise à jour finale des charges de travail nécessaires
        for tup in tabAgent[i]:
            updateWorkloadNecessaire(agentsPool[tup[0]], tachePool)

    return tabOverworkload  # Retourne le tableau des surcharges de travail par niveau

def DistributionSansRecuperationBas(agentsPool, tachePool, sizeDiff = 3):
    #todo
    tabAgent, tabTache = generateTabdiff(agentsPool, tachePool, sizeDiff)
    tabOverworkload = [0,0,0]
    #attribue les tache aux agent moin niveau  possible essayer reserve le pilot pour le plus haut tache 
    for i in range(0,sizeDiff):
        tabAgent[i].sort(key=lambda x: x[1], reverse =True)
        for tup in tabAgent[i]:
            supprimeList = []
            for t in tabTache[i]:
                agent = agentsPool[tup[0]]
                tache = tachePool[t]
                cost = consoTache(agent,tache )
                if agent.workload  > cost:
                    agent.tache.append(t)
                    tache.pilot = tup[0]
                    agent.workload = agent.workload  - cost
                    agent.t = tache.tt
                    supprimeList.append(t)
                    tache.wr = agent.workload
            for s in supprimeList:
                tabTache[i].remove(s)
        for tup in tabAgent[i]:
            updateWorkloadNecessaire(agentsPool[tup[0]],tachePool)
    #attribue les 
    for i in range(sizeDiff-2,-1,-1):
        if len(tabTache[i+1]) > 0:
            tabOverworkload[i+1] = len(tabTache[i+1])
            count = 0
            size_a = len(tabAgent[i])
            if size_a != 0:
                for t in tabTache[i]:
                    agentsPool[tabAgent[i][count%size_a][0]].tache.append(t)
                    tachePool[t].pilot = tabAgent[i][count%size_a][0]
                    agentsPool[tabAgent[i][count%size_a][0]].workload = 0
                    count = count +1
            for tup in tabAgent[i+1]:
                updateWorkloadNecessaire(agentsPool[tup[0]],tachePool)
        supprimeList = []
        for t in tabTache[i]:
            
            tache = tachePool[t]
            if tache.pilot == -1:
                for j in range(i+1,sizeDiff):
                    for tup in tabAgent[j]:
                        agent = agentsPool[tup[0]]
                        cost = consoTache(agent,tache )
                        is1, is2, indexs1, indexs2 = findSegementAutour(agent,t)
                        if is1 == -1 and is2 == -1:
                            if agent.workload  > cost:
                                tache.pilot = tup[0]
                                agent.workload = agent.workload - cost
                                agent.t = tache.tt
                                supprimeList.append(t)
                                tache.wr = agent.workload
                                
                        elif is1 == -1:
                            s2 = tachePool[indexs2]
                            x1 = agent.capacite
                            
                            if len(supprimeList) > 0:
                                for sup in range(len(supprimeList)):
                                    if(supprimeList[len(supprimeList)-1-sup] > indexs1):
                                        if tachePool[supprimeList[len(supprimeList)-1-sup]].pilot == tup[0]:
                                            s1 = tachePool[supprimeList[len(supprimeList)-1-sup]]
                                            x1 = s1.wr 
                                            break
                                    else:
                                        break
                            x2 = x1 - cost 
                            if x1 > cost and s2.wn<= x2 :
                                tache.pilot = tup[0]
                                supprimeList.append(t)
                                tache.wr = x1- cost
                                agent.needUpdate = True
                                agent.updatePoint = is2
                                costS2 = consoTache(agent,s2 )
                                s2.wr = min(x2, agent.capacite) - costS2
  
                        elif is2 == -1:
                            s1 = tachePool[indexs1]
                            if len(supprimeList) > 0:
                                for sup in range(len(supprimeList)):
                                    if(supprimeList[len(supprimeList)-1-sup] > indexs1):
                                        if tachePool[supprimeList[len(supprimeList)-1-sup]].pilot == tup[0]:
                                            s1 = tachePool[supprimeList[len(supprimeList)-1-sup]]
                                            x1 = s1.wr 
                                            break
                                    else:
                                        break
                            x1 = s1.wr 
                            if x1 >= cost:
                                tache.pilot = tup[0]
                                supprimeList.append(t)
                                tache.wr = x1 - cost
                                agent.needUpdate = False
                                    
                        else:
                            s1 = tachePool[indexs1]
                            s2 = tachePool[indexs2]
                            if agent.needUpdate and is1 > agent.updatePoint:
                                updateWorkloadRest(agent, is1, tachePool, False)
                            if len(supprimeList) > 0:
                                if(supprimeList[-1] > indexs1):
                                    for sup in range(len(supprimeList)):
                                        if(supprimeList[len(supprimeList)-1-sup] > indexs1):
                                            if tachePool[supprimeList[len(supprimeList)-1-sup]].pilot == tup[0]:
                                                s1 = tachePool[supprimeList[len(supprimeList)-1-sup]]
                                                x1 = s1.wr 
                                                break
                                        else:
                                            break
                                    
                            tache = tachePool[t]
                            x1 = s1.wr 
                            x2 = s1.wr - cost
                            if x1 >= cost and s2.wn <= x2:
                                tache.pilot = tup[0]
                                agent.t = tache.tt
                                supprimeList.append(t)
                                tache.wr = s1.wr  - cost
                                costS2 = consoTache(agent,s2 )
                                s2.wr = tache.wr - costS2
                                agent.needUpdate = True
                                agent.updatePoint = is2
                    # Retirer les tâches attribuées de la liste de tâches disponibles
        for s in supprimeList:
            tabTache[i].remove(s)
            agent.tache.append(s)
        for j in range(i+1,sizeDiff):
            for tup in tabAgent[j]:
                updateWorkloadNecessaire(agentsPool[tup[0]],tachePool)
    return tabOverworkload
def DistributionAvecRecuperationBas(agentsPool, tachePool, sizeDiff = 3, methode = "lineaire"):

    tabAgent, tabTache = generateTabdiff(agentsPool, tachePool, sizeDiff)
    tabOverworkload = [0,0,0]
    # #attribue les tache aux agent moin niveau  possible essayer reserve le pilot pour le plus haut tache 
    
    for i in range(0,sizeDiff):
        tabAgent[i].sort(key=lambda x: x[1], reverse =False)
        supprimeList = []
        for t in tabTache[i]:
            tache = tachePool[t]
            list_availiable  = []
            for tup in tabAgent[i]:
                agent = agentsPool[tup[0]]
                time = tache.td - agent.t
                cost = consoTache(agent,tache )
                agent.workload_est = agent.workload
                if min(agent.workload +  recup_calcul(agent,time, methode), agent.capacite) > cost:
                    list_availiable.append(tup[0])
            if len(list_availiable) == 1:
                agent = agentsPool[list_availiable[0]]
                cost = consoTache(agent,tache )
                agent.tache.append(t)
                tache.pilot = list_availiable[0]
                time = tache.td - agent.t
                agent.workload = min(agent.workload + recup_calcul(agent,time, methode), agent.capacite) - cost
                agent.t = tache.tt
                supprimeList.append(t)
                tache.wr = agent.workload
            if len(list_availiable) > 1:
                if agentsPool[list_availiable[-1]].nature == 1:
                    x =  random.randint(0, len(list_availiable)-1)
                    num = list_availiable[x]
                else:
                    num = list_availiable[-1]
                agent = agentsPool[num]
                cost = consoTache(agent,tache )
                agent.tache.append(t)
                tache.pilot = num
                time = tache.td - agent.t
                agent.workload = min(agent.workload + recup_calcul(agent,time, methode), agent.capacite) - cost
                agent.t = tache.tt
                supprimeList.append(t)
        for s in supprimeList:
            tabTache[i].remove(s)
        for tup in tabAgent[i]:
            updateWorkloadNecessaire(agentsPool[tup[0]],tachePool, methode)

    #check les reste tache et essaie d'attrbu aux des agent qui a des workload
    for i in range(sizeDiff-2,-1,-1):
        if len(tabTache[i+1]) > 0:
            tabOverworkload[i+1] = len(tabTache[i+1])
            count = 0
            size_a = len(tabAgent[i+1])
            if size_a != 0:
                for t in tabTache[i+1]:

                    agentsPool[tabAgent[i+1][count%size_a][0]].tache.append(t)
                    tachePool[t].pilot = tabAgent[i+1][count%size_a][0]
                    agentsPool[tabAgent[i+1][count%size_a][0]].workload = 0
                    count = count + 1
                for tup in tabAgent[i+1]:
                    updateWorkloadNecessaire(agentsPool[tup[0]],tachePool, methode)
            else:
                for j in range(2,sizeDiff):
                    if (i+j) < sizeDiff:
                        size_b = len(tabAgent[i+j])
                        for t in tabTache[i+1]:

                            agentsPool[tabAgent[i+j][count%size_b][0]].tache.append(t)
                            tachePool[t].pilot = tabAgent[i+j][count%size_b][0]
                            agentsPool[tabAgent[i+j][count%size_b][0]].workload = 0
                            count = count + 1
                        for tup in tabAgent[i+j]:
                            updateWorkloadNecessaire(agentsPool[tup[0]],tachePool, methode)
        supprimeList = []
        for t in tabTache[i]:
            
            tache = tachePool[t]
            if tache.pilot == -1:
                for j in range(i+1,sizeDiff):
                    if tache.pilot == -1:
                        for tup in tabAgent[j]:

                            agent = agentsPool[tup[0]]
                            cost = consoTache(agent,tache )
                            is1, is2, indexs1, indexs2 = findSegementAutour(agent,t)
                            if is1 == -1 and is2 == -1:
                                time = tache.td - agent.t
                                agent.workload_est = agent.workload
                                if min(agent.workload + recup_calcul(agent,time, methode), agent.capacite) > cost:
                                    
                                    tache.pilot = tup[0]
                                    agent.workload = min(agent.workload + recup_calcul(agent,time, methode), agent.capacite) - cost
                                    agent.t = tache.tt
                                    supprimeList.append(t)
                                    tache.wr = agent.workload
                                    break
                                    
                            elif is1 == -1:
                                
                                s2 = tachePool[indexs2]
                                x1 = agent.capacite
                                if len(supprimeList) > 0:
                                    for sup in range(len(supprimeList)):
                                        if(supprimeList[len(supprimeList)-1-sup] > indexs1):
                                            if tachePool[supprimeList[len(supprimeList)-1-sup]].pilot == tup[0]:
                                                s1 = tachePool[supprimeList[len(supprimeList)-1-sup]]
                                                time = tache.td - s1.tt
                                                agent.workload_est = s1.wr
                                                x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite)
                                                break
                                        else:
                                            break
                                time = s2.td- tache.tt
                                agent.workload_est = x1 - cost
                                x2 = x1 - cost + recup_calcul(agent,time, methode)
                                if x1 > cost and s2.wn<= min(x2, agent.capacite) :
                                    
                                    tache.pilot = tup[0]
                                    supprimeList.append(t)
                                    tache.wr = x1 - cost
                                    agent.needUpdate = True
                                    agent.updatePoint = is2
                                    costS2 = consoTache(agent,s2 )
                                    s2.wr = min(x2, agent.capacite) - costS2
                                    break
                                    
                            elif is2 == -1:
                                s1 = tachePool[indexs1]
                                if agent.needUpdate and is1 > agent.updatePoint:
                                    updateWorkloadRest(agent, is1, tachePool, methode=methode)
                                if len(supprimeList) > 0:
                                    for sup in range(len(supprimeList)):
                                        if(supprimeList[len(supprimeList)-1-sup] > indexs1):
                                            if tachePool[supprimeList[len(supprimeList)-1-sup]].pilot == tup[0]:
                                                s1 = tachePool[supprimeList[len(supprimeList)-1-sup]]
                                                break
                                        else:
                                            break
                                time = tache.td - s1.tt
                                agent.workload_est = s1.wr
                                x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite)
                                if x1 >= cost:
                                    tache.pilot = tup[0]
                                    supprimeList.append(t)
                                    tache.wr = x1 - cost
                                    agent.needUpdate = False
                                    break
                                        
                            else:
                                s1 = tachePool[indexs1]
                                s2 = tachePool[indexs2]
                                if agent.needUpdate and is1 > agent.updatePoint:
                                    updateWorkloadRest(agent, is1, tachePool, methode=methode)
                                if len(supprimeList) > 0:
                                    for sup in range(len(supprimeList)):
                                        if(supprimeList[len(supprimeList)-1-sup] > indexs1):
                                            if tachePool[supprimeList[len(supprimeList)-1-sup]].pilot == tup[0]:
                                                s1 = tachePool[supprimeList[len(supprimeList)-1-sup]]
                                                break
                                        else:
                                            break
                                        
                                tache = tachePool[t]
                                time = tache.td - s1.tt
                                time2 = s2.td- tache.tt
                                agent.workload_est = s1.wr
                                x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite) 
                                agent.workload_est = x1 - cost
                                x2 = x1 - cost + recup_calcul(agent, time2, methode)
                                if x1 >= cost and s2.wn <= min(x2,agent.capacite):
                                    
                                    tache.pilot = tup[0]
                                    agent.t = tache.tt
                                    supprimeList.append(t)
                                    tache.wr = x1 - cost
                                    costS2 = consoTache(agent,s2 )
                                    s2.wr = min(x2, agent.capacite) - costS2
                                    agent.needUpdate = True
                                    agent.updatePoint = is2
                                    break
                    # Retirer les tâches attribuées de la liste de tâches disponibles

        for s in supprimeList:
            agentsPool[tachePool[s].pilot].tache.append(s)
            tabTache[i].remove(s)
            
        for j in range(i+1,sizeDiff):
            for tup in tabAgent[j]:
                updateWorkloadNecessaire(agentsPool[tup[0]],tachePool, methode)
    if len(tabTache[0]) > 0:
            tabOverworkload[0] = len(tabTache[0])
            count = 0
            
    return tabOverworkload

def DistributionAvecRecuperationBasRepo(agentsPool, tachePool, sizeDiff = 3, methode = "lineaire", pause = 10):
    #todo ajoute des possibilite ajoute apres les tache
    tabAgent, tabTache = generateTabdiff(agentsPool, tachePool, sizeDiff)
    tabOverworkload = [0,0,0]
    repo_rest = pause
    #attribue les tache aux agent moin niveau  possible essayer reserve le pilot pour le plus haut tache 
    for i in range(0,sizeDiff):
        tabAgent[i].sort(key=lambda x: x[1], reverse =True)
        supprimeList = []
        for t in tabTache[i]:
            tache = tachePool[t]
            list_availiable  = []
            for tup in tabAgent[i]:
                agent = agentsPool[tup[0]]
                time = tache.td - agent.t
                cost = consoTache(agent,tache )
                agent.workload_est = agent.workload
                if min(agent.workload +  recup_calcul(agent,time, methode), agent.capacite) > cost:
                    list_availiable.append(tup[0])
            if len(list_availiable) == 1:
                agent = agentsPool[list_availiable[0]]
                cost = consoTache(agent,tache )
                agent.tache.append(t)
                tache.pilot = list_availiable[0]
                time = tache.td - agent.t
                agent.workload = min(agent.workload + recup_calcul(agent,time, methode), agent.capacite) - cost
                agent.t = tache.tt
                supprimeList.append(t)
                tache.wr = agent.workload
            if len(list_availiable) > 1:
                if agentsPool[list_availiable[-1]].nature == 1:
                    x =  random.randint(0, len(list_availiable)-1)
                    num = list_availiable[x]
                else:
                    num = list_availiable[-1]
                agent = agentsPool[num]
                cost = consoTache(agent,tache )
                agent.tache.append(t)
                tache.pilot = num
                time = tache.td - agent.t
                agent.workload = min(agent.workload + recup_calcul(agent,time, methode), agent.capacite) - cost
                agent.t = tache.tt
                supprimeList.append(t)
        for s in supprimeList:
            tabTache[i].remove(s)
        for tup in tabAgent[i]:
            updateWorkloadNecessaire(agentsPool[tup[0]],tachePool, methode)

    #check les reste tache et essaie d'attrbu aux des agent qui a des workload
    for i in range(sizeDiff-2,-1,-1):
        #partie ajoute des repo 
        
        if len(tabTache[i+1]) > 0:
            count = 0
            for t  in tabTache[i+1]:
                level = i+1
                #for e, tache123 in enumerate(tachePool):
                    #print(e,tache123)
                #todo ajouter version ajoute apres 
                agent_num, timeNeedBefore, timeNeedAfter =  ajout_tache_repos(agentsPool, tachePool, t, tabAgent, level, sizeDiff, repo_rest , methode)
                timeNeed = timeNeedBefore+ timeNeedAfter
                #print(agent_num, t, timeNeedBefore,timeNeedAfter, "time")
                if timeNeedBefore + timeNeedAfter > repo_rest or agent_num ==None:
                    return False
                #elif timeNeed == 0:
                    #pass
                else:
                    if timeNeedBefore != 0:
                        updateTacheTime(tachePool, timeNeedBefore, t)

                    if timeNeedAfter != 0: 
                        updateTacheTime(tachePool, timeNeedAfter, t+1)
                        
                    for index,agent in enumerate(agentsPool):
                        
                        is1, is2, indexs1, indexs2 = findSegementAutour(agent,t)
                        tache = tachePool[t]
                        cost = consoTache(agent,tache )
                        if index == agent_num:
                            if is2==-1:
                                s1 = tachePool[indexs1]
                                time = tache.td - s1.tt
                                agent.workload_est = s1.wr
                                x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite)
                                tache.pilot = index
                                tache.wr = x1 - cost
                                agent.needUpdate = False
                            else:
                                s1 = tachePool[indexs1]
                                s2 = tachePool[indexs2]
                                
                                if agent.needUpdate and is1 > agent.updatePoint:
                                    updateWorkloadRest(agent, is1, tachePool,methode= methode)

                                time = tache.td - s1.tt
                                time2 = s2.td- tache.tt
                                agent.workload_est = s1.wr
                                x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite) 
                                agent.workload_est = x1 - cost
                                x2 = x1 - cost + recup_calcul(agent, time2, methode)
                                tache.pilot = index
                                agent.t = tache.tt
                                tache.wr = x1 - cost
                                costS2 = consoTache(agent,s2 )
                                s2.wr = min(x2, agent.capacite) - costS2
                                agent.needUpdate = True
                                agent.updatePoint = is2
                        elif is2 == -1 or is1 ==-1:
                            pass
                        else:
                            s1 = tachePool[indexs1]
                            s2 = tachePool[indexs2]    
                            if agent.needUpdate and is1 > agent.updatePoint:
                                updateWorkloadRest(agent, is1, tachePool,methode= methode)
                            time = s2.td - s1.tt
                            agent.workload_est = s1.wr
                            x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite) 
                            costS2 = consoTache(agent,s2 )
                            s2.wr = x1 - costS2
                            agent.needUpdate = True
                            agent.updatePoint = is2
                    agentsPool[agent_num].tache.append(t)
                    for agent in agentsPool:
                        updateWorkloadNecessaire(agent,tachePool)
                    repo_rest= repo_rest- timeNeed
                    #for e, tache123 in enumerate(tachePool):
                       # print(e,tache123)

        supprimeList = []
        for t in tabTache[i]:
            
            tache = tachePool[t]
            if tache.pilot == -1:
                for j in range(i+1,sizeDiff):
                    if tache.pilot == -1:
                        for tup in tabAgent[j]:

                            agent = agentsPool[tup[0]]
                            cost = consoTache(agent,tache )
                            is1, is2, indexs1, indexs2 = findSegementAutour(agent,t)
                            if is1 == -1 and is2 == -1:
                                time = tache.td - agent.t
                                agent.workload_est = agent.workload
                                if min(agent.workload + recup_calcul(agent,time, methode), agent.capacite) > cost:
                                    
                                    tache.pilot = tup[0]
                                    agent.workload = min(agent.workload + recup_calcul(agent,time, methode), agent.capacite) - cost
                                    agent.t = tache.tt
                                    supprimeList.append(t)
                                    tache.wr = agent.workload
                                    break
                                    
                            elif is1 == -1:
                                
                                s2 = tachePool[indexs2]
                                x1 = agent.capacite
                                if len(supprimeList) > 0:
                                    for sup in range(len(supprimeList)):
                                        if(supprimeList[len(supprimeList)-1-sup] > indexs1):
                                            if tachePool[supprimeList[len(supprimeList)-1-sup]].pilot == tup[0]:
                                                s1 = tachePool[supprimeList[len(supprimeList)-1-sup]]
                                                time = tache.td - s1.tt
                                                agent.workload_est = s1.wr
                                                x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite)
                                                break
                                        else:
                                            break
                                time = s2.td- tache.tt
                                agent.workload_est = x1 - cost
                                x2 = x1 - cost + recup_calcul(agent,time, methode)
                                if x1 > cost and s2.wn<= min(x2, agent.capacite) :
                                    
                                    tache.pilot = tup[0]
                                    supprimeList.append(t)
                                    tache.wr = x1 - cost
                                    agent.needUpdate = True
                                    agent.updatePoint = is2
                                    costS2 = consoTache(agent,s2 )
                                    s2.wr = min(x2, agent.capacite) - costS2
                                    break
                                    
                            elif is2 == -1:
                                s1 = tachePool[indexs1]
                                if agent.needUpdate and is1 > agent.updatePoint:
                                    updateWorkloadRest(agent, is1, tachePool, methode=methode)
                                if len(supprimeList) > 0:
                                    for sup in range(len(supprimeList)):
                                        if(supprimeList[len(supprimeList)-1-sup] > indexs1):
                                            if tachePool[supprimeList[len(supprimeList)-1-sup]].pilot == tup[0]:
                                                s1 = tachePool[supprimeList[len(supprimeList)-1-sup]]
                                                break
                                        else:
                                            break
                                time = tache.td - s1.tt
                                agent.workload_est = s1.wr
                                x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite)
                                if x1 >= cost:
                                    tache.pilot = tup[0]
                                    supprimeList.append(t)
                                    tache.wr = x1 - cost
                                    agent.needUpdate = False
                                    break
                                        
                            else:
                                s1 = tachePool[indexs1]
                                s2 = tachePool[indexs2]
                                if agent.needUpdate and is1 > agent.updatePoint:
                                    updateWorkloadRest(agent, is1, tachePool, methode=methode)
                                if len(supprimeList) > 0:
                                    for sup in range(len(supprimeList)):
                                        if(supprimeList[len(supprimeList)-1-sup] > indexs1):
                                            if tachePool[supprimeList[len(supprimeList)-1-sup]].pilot == tup[0]:
                                                s1 = tachePool[supprimeList[len(supprimeList)-1-sup]]
                                                break
                                        else:
                                            break
                                        
                                tache = tachePool[t]
                                time = tache.td - s1.tt
                                time2 = s2.td- tache.tt
                                agent.workload_est = s1.wr
                                x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite) 
                                agent.workload_est = x1 - cost
                                x2 = x1 - cost + recup_calcul(agent, time2, methode)
                                if x1 >= cost and s2.wn <= min(x2,agent.capacite):
                                    
                                    tache.pilot = tup[0]
                                    agent.t = tache.tt
                                    supprimeList.append(t)
                                    tache.wr = x1 - cost
                                    costS2 = consoTache(agent,s2 )
                                    s2.wr = min(x2, agent.capacite) - costS2
                                    agent.needUpdate = True
                                    agent.updatePoint = is2
                                    break
                    # Retirer les tâches attribuées de la liste de tâches disponibles
        for s in supprimeList:
            agentsPool[tachePool[s].pilot].tache.append(s)
            tabTache[i].remove(s)
            
        for j in range(i+1,sizeDiff):
            for tup in tabAgent[j]:
                updateWorkloadNecessaire(agentsPool[tup[0]],tachePool, methode)


    if len(tabTache[0]) > 0:
            
        count = 0
        for t  in tabTache[0]:
            level = 0
            #for e, tache123 in enumerate(tachePool):
                #print(e,tache123)
            #todo ajouter version ajoute apres 
            agent_num, timeNeedBefore, timeNeedAfter =  ajout_tache_repos(agentsPool, tachePool, t, tabAgent, level, sizeDiff, repo_rest , methode)
            timeNeed = timeNeedBefore+ timeNeedAfter
            #print(agent_num, t, timeNeedBefore,timeNeedAfter, "time")
            if timeNeedBefore + timeNeedAfter > repo_rest:
                return False
            #elif timeNeed == 0:
                #pass
            else:
                if timeNeedBefore != 0:
                    updateTacheTime(tachePool, timeNeedBefore, t)

                if timeNeedAfter != 0: 
                    updateTacheTime(tachePool, timeNeedAfter, t+1)
                    
                for index,agent in enumerate(agentsPool):
                    
                    is1, is2, indexs1, indexs2 = findSegementAutour(agent,t)
                    tache = tachePool[t]
                    cost = consoTache(agent,tache )
                    if index == agent_num:
                        if is2==-1:
                            s1 = tachePool[indexs1]
                            time = tache.td - s1.tt
                            agent.workload_est = s1.wr
                            x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite)
                            tache.pilot = index
                            tache.wr = x1 - cost
                            agent.needUpdate = False
                        else:
                            s1 = tachePool[indexs1]
                            s2 = tachePool[indexs2]
                            
                            if agent.needUpdate and is1 > agent.updatePoint:
                                updateWorkloadRest(agent, is1, tachePool,methode= methode)

                            time = tache.td - s1.tt
                            time2 = s2.td- tache.tt
                            agent.workload_est = s1.wr
                            x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite) 
                            agent.workload_est = x1 - cost
                            x2 = x1 - cost + recup_calcul(agent, time2, methode)
                            tache.pilot = index
                            agent.t = tache.tt
                            tache.wr = x1 - cost
                            costS2 = consoTache(agent,s2 )
                            s2.wr = min(x2, agent.capacite) - costS2
                            agent.needUpdate = True
                            agent.updatePoint = is2
                    elif is2 == -1 or is1 ==-1:
                        pass
                    else:
                        s1 = tachePool[indexs1]
                        s2 = tachePool[indexs2]    
                        if agent.needUpdate and is1 > agent.updatePoint:
                            updateWorkloadRest(agent, is1, tachePool,methode= methode)
                        time = s2.td - s1.tt
                        agent.workload_est = s1.wr
                        x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite) 
                        costS2 = consoTache(agent,s2 )
                        s2.wr = x1 - costS2
                        agent.needUpdate = True
                        agent.updatePoint = is2
                agentsPool[agent_num].tache.append(t)
                for agent in agentsPool:
                    updateWorkloadNecessaire(agent,tachePool)
                repo_rest= repo_rest- timeNeed
                    #for e, tache123 in enumerate(tachePool):
                       # print(e,tache123)
    return True

def DistributionAvecRecuperationRepo(agentsPool, tachePool, sizeDiff = 3, methode = "lineaire", pause = 10):
    #todo ajoute des possibilite ajoute apres les tache
    tabAgent, tabTache = generateTabdiff(agentsPool, tachePool, sizeDiff)
    tabOverworkload = [0,0,0]
    repo_rest = pause
    #attribue les tache aux agent moin niveau  possible essayer reserve le pilot pour le plus haut tache 
    for i in range(0,sizeDiff):
        tabAgent[i].sort(key=lambda x: x[1], reverse =True)
        supprimeList = []
        for t in tabTache[i]:
            tache = tachePool[t]
            list_availiable  = []
            for tup in tabAgent[i]:

                agent = agentsPool[tup[0]]
                cost = consoTache(agent,tache)
                time = tache.td - agent.t
                agent.workload_est = agent.workload
                if min(agent.workload +  recup_calcul(agent,time, methode), agent.capacite) > cost:
                    list_availiable.append(tup[0])
            if len(list_availiable) == 1:
                agent = agentsPool[list_availiable[0]]
                cost = consoTache(agent,tache)
                agent.tache.append(t)
                tache.pilot = list_availiable[0]
                time = tache.td - agent.t
                agent.workload = min(agent.workload + recup_calcul(agent,time, methode), agent.capacite) - cost
                agent.t = tache.tt
                supprimeList.append(t)
                tache.wr = agent.workload
            if len(list_availiable) > 1:
                if list_availiable[-1].nature == 1:
                    x =  random.randint(0, len(list_availiable)-1)
                    num = list_availiable[x]
                else:
                    num = list_availiable[-1]
                agent = agentsPool[num]
                cost = consoTache(agent,tache)
                agent.tache.append(t)
                tache.pilot = num
                time = tache.td - agent.t
                agent.workload = min(agent.workload + recup_calcul(agent,time, methode), agent.capacite) - cost
                agent.t = tache.tt
                supprimeList.append(t)
        for tup in tabAgent[i]:
            updateWorkloadNecessaire(agentsPool[tup[0]],tachePool, methode)




    #check les reste tache et essaie d'attrbu aux des agent qui a des workload
    for i in range(sizeDiff-2,-1,-1):
        #partie ajoute des repo 
        
        if len(tabTache[i+1]) > 0:
            
            count = 0
            for t  in tabTache[i+1]:
                level = i+1
                #for e, tache123 in enumerate(tachePool):
                    #print(e,tache123)
                #todo ajouter version ajoute apres 
                agent_num, timeNeedBefore, timeNeedAfter =  ajout_tache_repos(agentsPool, tachePool, t, tabAgent, level, sizeDiff, repo_rest , methode)
                timeNeed = timeNeedBefore + timeNeedAfter
                #print(agent_num, t, timeNeedBefore,timeNeedAfter, "time")
                if timeNeedBefore + timeNeedAfter > repo_rest:
                    return False
                #elif timeNeed == 0:
                    #pass
                else:
                    if timeNeedBefore != 0:
                        updateTacheTime(tachePool, timeNeedBefore, t)

                    if timeNeedAfter != 0: 
                        updateTacheTime(tachePool, timeNeedAfter, t+1)
                        
                    for index,agent in enumerate(agentsPool):
                        
                        is1, is2, indexs1, indexs2 = findSegementAutour(agent,t)
                        if index == agent_num:
                            if is2==-1:
                                s1 = tachePool[indexs1]
                                tache = tachePool[t]
                                cost = consoTache(agent,tache)
                                time = tache.td - s1.tt
                                agent.workload_est = s1.wr
                                x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite)
                                tache.pilot = index
                                tache.wr = x1 - cost
                                agent.needUpdate = False
                            else:
                                s1 = tachePool[indexs1]
                                s2 = tachePool[indexs2]
                                tache = tachePool[t]
                                cost = consoTache(agent,tache)
                                if agent.needUpdate and is1 > agent.updatePoint:
                                    updateWorkloadRest(agent, is1, tachePool,methode= methode)

                                time = tache.td - s1.tt
                                time2 = s2.td- tache.tt
                                agent.workload_est = s1.wr
                                x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite) 
                                agent.workload_est = x1 - cost
                                x2 = x1 - cost + recup_calcul(agent, time2, methode)

                                tache.pilot = index
                                agent.t = tache.tt
                                tache.wr = x1 - cost
                                costS2 = consoTache(agent, s2)
                                s2.wr = min(x2, agent.capacite) - costS2
                                agent.needUpdate = True
                                agent.updatePoint = is2
                        elif is2 == -1 or is1 ==-1:
                            pass
                        else:
                            s1 = tachePool[indexs1]
                            s2 = tachePool[indexs2]    
                            if agent.needUpdate and is1 > agent.updatePoint:
                                updateWorkloadRest(agent, is1, tachePool,methode= methode)
                            time = s2.td - s1.tt
                            agent.workload_est = s1.wr
                            x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite) 
                            costS2 = consoTache(agent, s2)
                            s2.wr = x1 - costS2
                            agent.needUpdate = True
                            agent.updatePoint = is2
                    agentsPool[agent_num].tache.append(t)
                    for agent in agentsPool:
                        updateWorkloadNecessaire(agent,tachePool)
                    repo_rest= repo_rest- timeNeed
                    #for e, tache123 in enumerate(tachePool):
                       # print(e,tache123)

        supprimeList = []
        for t in tabTache[i]:
            
            tache = tachePool[t]
            if tache.pilot == -1:
                for j in range(i+1,sizeDiff):
                    if tache.pilot == -1:
                        for tup in tabAgent[j]:

                            agent = agentsPool[tup[0]]
                            cost = consoTache(agent, tache)
                            is1, is2, indexs1, indexs2 = findSegementAutour(agent,t)
                            if is1 == -1 and is2 == -1:
                                time = tache.td - agent.t
                                agent.workload_est = agent.workload
                                if min(agent.workload + recup_calcul(agent,time, methode), agent.capacite) > cost:
                                    
                                    tache.pilot = tup[0]
                                    agent.workload = min(agent.workload + recup_calcul(agent,time, methode), agent.capacite) - cost
                                    agent.t = tache.tt
                                    supprimeList.append(t)
                                    tache.wr = agent.workload
                                    break
                                    
                            elif is1 == -1:
                                
                                s2 = tachePool[indexs2]
                                x1 = agent.capacite
                                if len(supprimeList) > 0:
                                    for sup in range(len(supprimeList)):
                                        if(supprimeList[len(supprimeList)-1-sup] > indexs1):
                                            if tachePool[supprimeList[len(supprimeList)-1-sup]].pilot == tup[0]:
                                                s1 = tachePool[supprimeList[len(supprimeList)-1-sup]]
                                                time = tache.td - s1.tt
                                                agent.workload_est = s1.wr
                                                x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite)
                                                break
                                        else:
                                            break
                                time = s2.td- tache.tt
                                agent.workload_est = x1 - cost
                                x2 = x1 - cost + recup_calcul(agent,time, methode)
                                if x1 > cost and s2.wn<= min(x2, agent.capacite) :
                                    
                                    tache.pilot = tup[0]
                                    supprimeList.append(t)
                                    tache.wr = x1 - cost
                                    agent.needUpdate = True
                                    agent.updatePoint = is2
                                    consoS2 = consoTache(agent, s2)
                                    s2.wr = min(x2, agent.capacite) - costS2
                                    break
                                    
                            elif is2 == -1:
                                s1 = tachePool[indexs1]
                                if agent.needUpdate and is1 > agent.updatePoint:
                                    updateWorkloadRest(agent, is1, tachePool, methode=methode)
                                if len(supprimeList) > 0:
                                    for sup in range(len(supprimeList)):
                                        if(supprimeList[len(supprimeList)-1-sup] > indexs1):
                                            if tachePool[supprimeList[len(supprimeList)-1-sup]].pilot == tup[0]:
                                                s1 = tachePool[supprimeList[len(supprimeList)-1-sup]]
                                                break
                                        else:
                                            break
                                time = tache.td - s1.tt
                                agent.workload_est = s1.wr
                                x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite)
                                if x1 >= cost:
                                    tache.pilot = tup[0]
                                    supprimeList.append(t)
                                    tache.wr = x1 - cost
                                    agent.needUpdate = False
                                    break
                                        
                            else:
                                s1 = tachePool[indexs1]
                                s2 = tachePool[indexs2]
                                if agent.needUpdate and is1 > agent.updatePoint:
                                    updateWorkloadRest(agent, is1, tachePool, methode=methode)
                                if len(supprimeList) > 0:
                                    for sup in range(len(supprimeList)):
                                        if(supprimeList[len(supprimeList)-1-sup] > indexs1):
                                            if tachePool[supprimeList[len(supprimeList)-1-sup]].pilot == tup[0]:
                                                s1 = tachePool[supprimeList[len(supprimeList)-1-sup]]
                                                break
                                        else:
                                            break
                                        
                                tache = tachePool[t]
                                time = tache.td - s1.tt
                                time2 = s2.td- tache.tt
                                agent.workload_est = s1.wr
                                x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite) 
                                agent.workload_est = x1 - cost
                                x2 = x1 - cost + recup_calcul(agent, time2, methode)
                                if x1 >= cost and s2.wn <= min(x2,agent.capacite):
                                    
                                    tache.pilot = tup[0]
                                    agent.t = tache.tt
                                    supprimeList.append(t)
                                    tache.wr = x1 - cost
                                    costS2 = consoTache(agent,s2)
                                    s2.wr = min(x2, agent.capacite) - costS2
                                    agent.needUpdate = True
                                    agent.updatePoint = is2
                                    break
                    # Retirer les tâches attribuées de la liste de tâches disponibles
        for s in supprimeList:
            agentsPool[tachePool[s].pilot].tache.append(s)
            tabTache[i].remove(s)
            
        for j in range(i+1,sizeDiff):
            for tup in tabAgent[j]:
                updateWorkloadNecessaire(agentsPool[tup[0]],tachePool, methode)
    return True

def consoTache(pilot, tache, coef = 0.25):
    tl = tache.level
    pl = pilot.level
    if tl ==0: 
        cost = tache.cost*(1+(tl-pl)*coef)*1.5
    else:
        cost = tache.cost*(1+(tl-pl)*coef) 
    return cost

def updateWorkloadNecessaire(pilot, tachePool, methode = "lineaire"):
    # Mise à jour de la charge de travail nécessaire pour chaque tâche attribuée à un pilote
    pilot.tache.sort()  # Tri des tâches du pilote
    list_t = sorted(pilot.tache, reverse=True)  # Liste inversée des tâches
    
    for index, item in enumerate(list_t):
        cost = consoTache(pilot,tachePool[item])
        # Calcul de la charge de travail nécessaire pour chaque tâche
        if index == 0:

            tachePool[item].wn = cost  # Charge de travail nécessaire pour la dernière tâche
            
        else:

            item_precedent = list_t[index - 1]  # Tâche précédente
            t = tachePool[item_precedent].td - tachePool[item].tt  # Différence de temps entre les tâches
            if methode != "exp":
                
            # Calcul de la charge de travail nécessaire en tenant compte de la récupération
                if tachePool[item_precedent].wn >= recup_calcul(pilot, t, methode):   
                    tachePool[item].wn = cost + tachePool[item_precedent].wn - recup_calcul(pilot, t, methode)
                else:
                    tachePool[item].wn = cost
            else:
                if tachePool[item_precedent].wn >= recup_calcul_inverse(pilot, t, methode):
                    tachePool[item].wn = cost + tachePool[item_precedent].wn - recup_calcul_inverse(pilot, t ,methode, tachePool[item_precedent].wn)
                else:
                    tachePool[item].wn = cost
    return

def updateWorkloadRest(agent, is1, tachePool, rec = True, methode= "lineaire"):
    # Mise à jour de la charge de travail restante pour un agent
    for i in range(agent.updatePoint + 1, is1 + 1):
        index = agent.tache[i]
        indexP = agent.tache[i - 1]
        cost = consoTache(agent,tachePool[index])
        # Calcul de la charge de travail restante après chaque tâche
        tachePool[index].wr = tachePool[indexP].wr - cost
        if rec:

            t = tachePool[index].td - tachePool[indexP].tt 
            

            agent.workload_est =  tachePool[indexP].wr
            
            tachePool[index].wr =  min(tachePool[index].wr +  recup_calcul(agent, t, methode), agent.capacite- cost)

    agent.updatePoint = is1
def findSegementAutour(agent, t):
    # Trouver les segments de tâches entourant une tâche spécifique
    size_t = len(agent.tache)  # Taille de la liste des tâches de l'agent
    if size_t == 0:
        return -1, -1, -1, -1  # Cas où l'agent n'a aucune tâche

    if t < agent.tache[0]:
        # Cas où la tâche est avant la première tâche de l'agent
        return -1, 0, -1, agent.tache[0]

    # Parcours des tâches de l'agent pour trouver les segments entourant la tâche t
    for index, item in enumerate(agent.tache[1:], start=1):
        if t < item:
            return index - 1, index, agent.tache[index - 1], item

    # Cas où la tâche est après la dernière tâche de l'agent
    return size_t - 1, -1, agent.tache[size_t - 1], -1

def ajout_tache_repos(agentsPool, tachePool, t, tabAgent, level, sizeDiff, repo_rest,methode ):
    dict_repo = {}
    for j in range(level,sizeDiff):
        for tup in tabAgent[j]:

            tache = tachePool[t]
            agent = agentsPool[tup[0]]
            is1, is2, indexs1, indexs2 = findSegementAutour(agent,t)
            cost  =  consoTache(agent, tache)
            if is1 == -1 and is2 == -1:
                time = tache.td - agent.t
                agent.workload_est = agent.workload
                if min(agent.workload + recup_calcul(agent,time, methode), agent.capacite) < cost:
                    dict_repo[tup[0]] =  (repo_rest+1,0)
                else:
                    dict_repo[tup[0]] = (0,0)
            elif is1 == -1:
                
                s2 = tachePool[indexs2]
                x1 = agent.capacite
                time = s2.td- tache.tt
                agent.workload_est = x1 - cost
                x2 = x1 - cost + recup_calcul(agent,time, methode)
                if x1 < cost :
                    dict_repo[tup[0]] =  (repo_rest+1,0)
                elif s2.wn > x2:

                    workloadNeed =  s2.wn- x2
                    dict_repo[tup[0]] =  (0,recup_sup_necessaire(agent, time ,workloadNeed,methode))
                else:
                    dict_repo[tup[0]] = (0,0)
                    
            elif is2 == -1:
                s1 = tachePool[indexs1]
                time = tache.td - s1.tt
                agent.workload_est = s1.wr
                x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite)
                if x1 < cost:
                    if x1 == agent.capacite:
                        dict_repo[tup[0]] =  (repo_rest+1,0)
                    else:
                       workloadNeed =  cost - x1
                       dict_repo[tup[0]] =  (recup_sup_necessaire(agent, time ,workloadNeed,methode),0)
                else:
                    dict_repo[tup[0]] = (0,0)
                        
            else:
                s1 = tachePool[indexs1]
                s2 = tachePool[indexs2]
                if agent.needUpdate and is1 > agent.updatePoint:
                    updateWorkloadRest(agent, is1, tachePool, methode)
                time = tache.td - s1.tt
                time2 = s2.td- tache.tt
                agent.workload_est = s1.wr
                x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite) 
                
                if x1 < cost:
                    
                    if x1 == agent.capacite:
                        dict_repo[tup[0]] =  (repo_rest+1,0)
                    else:
                       workloadNeed =  cost - x1
                       dict_repo[tup[0]] =  (recup_sup_necessaire(agent, time ,workloadNeed,methode),0)
                       agent.workload_est = 0
                       x2 = recup_calcul(agent, time2, methode)
                       if s2.wn > x2:
                            workloadNeed =  s2.wn- x2
                            dict_repo[tup[0]] = dict_repo[tup[0]][:1] +(recup_sup_necessaire(agent, time2 ,workloadNeed,methode),)
                else:
                    agent.workload_est = x1 - cost
                    x2 = x1 - cost + recup_calcul(agent, time2, methode)
                    if s2.wn > x2:
                        workloadNeed =  s2.wn- x2
                        dict_repo[tup[0]] =  (0,recup_sup_necessaire(agent, time2 ,workloadNeed,methode))
                    else :
                        dict_repo[tup[0]] = (0,0)
    min_key = None
    min_value = None
    before_after = 0
    before = 0
    after = 0
    for key, value in dict_repo.items():
        if min_value is None or sum(value) < min_value:
            min_key = key
            before = value[0]
            after = value[1]
            min_value = sum(value)
    return min_key,  before, after

def recup_calcul(agent,time, methode = "lineaire"):
    if methode == "lineaire":
        return recup_lineaire(agent,time)
    if methode == "quad":
        return recup_quad(agent,time)
    if methode == "other":
        return recup_other(agent,time)
    if methode == "exp":
        return recup_exp(agent,  time)

def recup_lineaire(agent, time):
    return agent.r*time

def recup_quad(agent, time):
    if (agent.r_a<0):
        if time>-agent.r_b/(2*agent.r_a):
            restTime = time + agent.r_b/(2*agent.r_a)
            v= agent.r_a*(-1) 
            return -agent.r_b*agent.r_b/(4*agent.r_a)+ restTime*v
    return agent.r_a*time*time + agent.r_b*time

def recup_exp(agent,time):
    coef = 1- agent.workload_est/agent.capacite
    coef_apre_rest = coef* np.exp(-agent.miu*time)

    return (coef -coef_apre_rest)*agent.capacite
def recup_exp_inverse(agent,  time,workloadFin):
    coef_apre_rest = 1- workloadFin/agent.capacite
    coef =coef_apre_rest* np.exp(agent.miu*time)
    return (coef -coef_apre_rest)*agent.capacite
def recup_calcul_inverse(agent,time, methode = "lineaire", workloadFin = 0):
    if methode == "lineaire":
        return recup_lineaire(agent,time)
    if methode == "quad":
        return recup_quad(agent,time)
    if methode == "other":
        return recup_other(agent,time)
    if methode == "exp":
        return recup_exp_inverse(agent,  time,workloadFin)
def recup_other(agent, time):
    return recup_lineaire(agent, max(time-agent.latency,0))
def recup_sup_necessaire(agent, time ,workloadNeed, methode):
    if methode == "lineaire":
        return recup_lineaire_need(agent,time, workloadNeed)
    if methode == "quad":
        return recup_quad_need(agent,time, workloadNeed)
    if methode == "other":
        return recup_other_need(agent,time, workloadNeed)
    if methode == "exp":
        return recup_exp_need(agent,  time,workloadNeed)

def recup_exp_need(agent,  time, workloadNeed):
    workloadNeedAll= recup_exp(agent,time)+ workloadNeed +agent.workload_est
    
    coef =  1- agent.workload_est/agent.capacite
    coef_apre_rest =  1- workloadNeedAll/agent.capacite
    if coef_apre_rest<= 0:
        if coef_apre_rest >-0.01:
            coef_apre_rest= 0.00001
        coef_apre_rest= 0.00001
        #print("sss")
        #print(recup_exp(agent,time))
        #print(workloadNeed)
        #print(agent.workload_est)
        #coef_apre_rest=0.0000001
    
    needtime = math.log(coef_apre_rest/coef)/(-agent.miu)
    needtime = needtime-time
    return int(needtime+1) 
def recup_other_need(agent,time, workloadNeed):
    delay = agent.latency
    if time <delay:
        return int(workloadNeed/agent.r+delay-time+1)
    return int(workloadNeed/agent.r+1)
def recup_quad_need(agent,time, workloadNeed):
    if agent.r_a ==0:
        return int(workloadNeed/agent.r_b+1)
    if (agent.r_a<0):
        if time >-agent.r_b/(2*agent.r_a):
            v= agent.r_a*(-1)
            return int(workloadNeed/v+1)
        if agent.r_a*time*time + agent.r_b*time + workloadNeed > -agent.r_b*agent.r_b/(4*agent.r_a):
            t1 =  -agent.r_b/(2*agent.r_a)- time
            rest = agent.r_a*time*time + agent.r_b*time + workloadNeed + agent.r_b*agent.r_b/(4*agent.r_a)
            v= agent.r_a*(-1)
            return int(t1+rest/v+1)
        c = agent.r_a*time*time + agent.r_b*time + workloadNeed

        a = agent.r_a
        b = agent.r_b
        
        discriminant = b**2 + 4*a*c
        return  int((-b + math.sqrt(discriminant)) / (2 * a) - time+1)
    if agent.r_a>0:
        c = agent.r_a*time*time + agent.r_b*time + workloadNeed 
        a = agent.r_a
        b = agent.r_b
        discriminant = b**2 + 4*a*c
        return  int((-b + math.sqrt(discriminant)) / (2 * a) - time+1)
def recup_lineaire_need(agent,time, workloadNeed):
    return int(workloadNeed/agent.r+1)

def updateTacheTime(tachePool, timeNeed, t):
    lenPool = len(tachePool)
    for i in range(t,lenPool):
        tachePool[i].td+=timeNeed
        tachePool[i].tt+=timeNeed