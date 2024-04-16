D6XAt-Lx4Bz-bRtHK-J9yeF-oMofz



def DistributionAvecRecuperationBas(agentsPool, tachePool, sizeDiff = 3, methode = "lineaire"):

    tabAgent, tabTache = generateTabdiff(agentsPool, tachePool, sizeDiff)
    tabOverworkload = [0,0,0]
    #attribue les tache aux agent moin niveau  possible essayer reserve le pilot pour le plus haut tache 
    for i in range(0,sizeDiff):
        tabAgent[i].sort(key=lambda x: x[1], reverse =False)
        for tup in tabAgent[i]:
            supprimeList = []
            for t in tabTache[i]:
                agent = agentsPool[tup[0]]
                tache = tachePool[t]
                time = tache.td - agent.t
                agent.workload_est = agent.workload
                if min(agent.workload +  recup_calcul(agent,time, methode), agent.capacite) > tache.cost:
                    agent.tache.append(t)
                    tache.pilot = tup[0]
                    agent.workload = min(agent.workload + recup_calcul(agent,time, methode), agent.capacite) - tachePool[t].cost
                    agent.t = tache.tt
                    supprimeList.append(t)
                    tache.wr = agent.workload
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
                            is1, is2, indexs1, indexs2 = findSegementAutour(agent,t)
                            if is1 == -1 and is2 == -1:
                                time = tache.td - agent.t
                                agent.workload_est = agent.workload
                                if min(agent.workload + recup_calcul(agent,time, methode), agent.capacite) > tache.cost:
                                    
                                    tache.pilot = tup[0]
                                    agent.workload = min(agent.workload + recup_calcul(agent,time, methode), agent.capacite) - tachePool[t].cost
                                    agent.t = tache.tt
                                    supprimeList.append(t)
                                    tache.wr = agent.workload
                                    break
                                    
                            elif is1 == -1:
                                
                                s2 = tachePool[indexs2]
                                x1 = agent.capacite
                                if len(supprimeList) > 0:
                                    s1 = tachePool[supprimeList[-1]]
                                    time = tache.td - s1.tt
                                    agent.workload_est = s1.wr
                                    x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite)
                                time = s2.td- tache.tt
                                agent.workload_est = x1 - tache.cost
                                x2 = x1 - tache.cost + recup_calcul(agent,time, methode)
                                if x1 > tache.cost and s2.wn<= min(x2, agent.capacite) :
                                    
                                    tache.pilot = tup[0]
                                    supprimeList.append(t)
                                    tache.wr = x1 - tache.cost
                                    agent.needUpdate = True
                                    agent.updatePoint = is2
                                    break
                                    
                            elif is2 == -1:
                                s1 = tachePool[indexs1]
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
                                if x1 >= tache.cost:
                                    tache.pilot = tup[0]
                                    supprimeList.append(t)
                                    tache.wr = x1 - tache.cost
                                    agent.needUpdate = False
                                    break
                                        
                            else:
                                s1 = tachePool[indexs1]
                                s2 = tachePool[indexs2]
                                if agent.needUpdate and is1 > agent.updatePoint:
                                    updateWorkloadRest(agent, is1, tachePool, methode)
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
                                agent.workload_est = x1 - tache.cost
                                x2 = x1 - tache.cost + recup_calcul(agent, time2, methode)
                                if x1 >= tache.cost and s2.wn <= min(x2,agent.capacite):
                                    
                                    tache.pilot = tup[0]
                                    agent.t = tache.tt
                                    supprimeList.append(t)
                                    tache.wr = x1 - tachePool[t].cost
                                    s2.wr = min(x2, agent.capacite) - s2.cost
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
    return tabOverworkload