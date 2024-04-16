def ajout_tache_repos(agentsPool, tachePool, t, tabAgent, level, sizeDiff, repo_rest,methode ):
    dict_repo = {}
    for j in range(level,sizeDiff):
        for tup in tabAgent[j]:

            tache = tachePool[t]
            agent = agentsPool[tup[0]]
            is1, is2, indexs1, indexs2 = findSegementAutour(agent,t)
            
            if is1 == -1 and is2 == -1:
                time = tache.td - agent.t
                agent.workload_est = agent.workload
                if min(agent.workload + recup_calcul(agent,time, methode), agent.capacite) < tache.cost:
                    dict_repo[tup[0]] =  repo_rest+1
                else:
                    dict_repo[tup[0]] = 0
            elif is1 == -1:
                
                s2 = tachePool[indexs2]
                x1 = agent.capacite
                time = s2.td- tache.tt
                agent.workload_est = x1 - tache.cost
                x2 = x1 - tache.cost + recup_calcul(agent,time, methode)
                if x1 < tache.cost :
                    dict_repo[tup[0]] =  repo_rest+1
                elif s2.wn > x2:
                    workloadNeed =  s2.wn- x2
                    dict_repo[tup[0]] =  recup_sup_necessaire(agent, time ,workloadNeed,methode)
                else:
                    dict_repo[tup[0]] = 0
                    
            elif is2 == -1:
                s1 = tachePool[indexs1]
                time = tache.td - s1.tt
                agent.workload_est = s1.wr
                x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite)
                if x1 < tache.cost:
                    if x1 == agent.capacite:
                        dict_repo[tup[0]] =  repo_rest+1
                    else:
                       workloadNeed =  tache.cost - x1
                       dict_repo[tup[0]] =  recup_sup_necessaire(agent, time ,workloadNeed,methode)
                else:
                    dict_repo[tup[0]] = 0
                        
            else:
                s1 = tachePool[indexs1]
                s2 = tachePool[indexs2]
                if agent.needUpdate and is1 > agent.updatePoint:
                    updateWorkloadRest(agent, is1, tachePool, methode)
                time = tache.td - s1.tt
                time2 = s2.td- tache.tt
                agent.workload_est = s1.wr
                x1 = min(s1.wr + recup_calcul(agent,time, methode), agent.capacite) 
                
                if x1 < tache.cost:
                    if x1 == agent.capacite:
                        dict_repo[tup[0]] =  repo_rest+1
                    else:
                       workloadNeed =  tache.cost - x1
                       dict_repo[tup[0]] =  recup_sup_necessaire(agent, time ,workloadNeed,methode)
                else:
                    agent.workload_est = x1 - tache.cost
                    x2 = x1 - tache.cost + recup_calcul(agent, time2, methode)
                    if s2.wn > x2:
                    
                        workloadNeed =  s2.wn- x2
                        dict_repo[tup[0]] =  recup_sup_necessaire(agent, time2 ,workloadNeed,methode)
                    else :
                        dict_repo[tup[0]] = 0
    min_key = None
    min_value = None

    for key, value in dict_repo.items():
        if min_value is None or value < min_value:
            min_key = key
            min_value = value
    return min_key, min_value