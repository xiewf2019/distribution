#code Non test
#le gain d'une mission principalement peut diviser en 2 partie gain de satisfaction et le gain de exp sur les pilot ici on consider les ia ne sont pas capable gain des experience(pas via mission peut etre via data qui va etre sur le nombre de reussit de segment)
#et ici on consider que les drone a des energy non limited et notre but est essayer gain de maximum point interet possible
def compterMissionNew(funcDistribu,simu, agentPool, tachePool, prob_reussi, nb_exp, puni, stra):
    ap = copy.deepcopy(agentPool)
    tp = copy.deepcopy(tachePool)
    funcDistribu(ap, tp)
    nb_mission = simu(ap,tp, prob_reussi, nb_exp, puni, stra)
    return nb_mission
​
def simulation_weighted(ap, tp, prob_reussi, nb_exp, puni, stra):
    mission_reussi = []
    mission_ai = []
    gain_interet = []
    for i in range(nb_exp):
        mission_reussi_per_exp = 0
        mission_reussi_per_exp_ai = 0
        gain_interet_per_exp = 0
        ap_copy = copy.deepcopy(ap)
        tp_copy = copy.deepcopy(tp)
        tabAgent = []
        missionfailed = False
        for j in range(0, len(ap_copy)):
            level = ap_copy[j].level
            exp = ap_copy[j].exp
            tabAgent.append((j,exp))
        tabAgent.sort(key=lambda x: x[1], reverse=stra) 
        
        for a in ap_copy:
            a.t = 0
        reussi = False    
        for index,tache in enumerate(tp_copy):
            if missionfailed:
                break
            reussi = False
            if tache.pilot != -1:
                agent = ap_copy[tache.pilot]
                updateAgentWorkloadActuelleAvant(agent, tache)
                reussi = faireTache(agent, tache, puni)
                ap_copy[tache.pilot].tache.remove(index)
                if reussi:
                    mission_reussi_per_exp += 1
                    gain_interet_per_exp += tache.weight
                    if agent.nature >0:
                        mission_reussi_per_exp_ai += 1
            if not reussi:
                tabOverload= []
                #let the pilot who has extra workload to work before
                for p in range(len(ap)):
                    agent = ap_copy[tabAgent[p][0]]
                    updateAgentWorkloadActuelleAvant(agent, tache)
                    if agent.level >= tache.level and tabAgent[p] != tache.pilot:
                        if tache.cost < agent.workloadActuelle:
                            if len(agent.tache) == 0:
                                reussi = faireTache(agent, tache, puni)
                                if reussi:
                                    mission_reussi_per_exp += 1
                                    gain_interet_per_exp += tache.weight
                                    if agent.nature >0:
                                        mission_reussi_per_exp_ai += 1
                                    break
                            else:
                                x1 = agent.r * (tp_copy[agent.tache[0]].td - tache.tt) + agent.workloadActuelle - tache.cost
                                if tp_copy[agent.tache[0]].wn < x1 :
                                    reussi = faireTache(agent, tache, puni)
                                    if reussi:
                                        mission_reussi_per_exp += 1
                                        gain_interet_per_exp += tache.weight
                                        if agent.nature >0:
                                            mission_reussi_per_exp_ai += 1
                                        break
                                else:
                                    tabOverload.append(tabAgent[p][0])
                        else:
                            tabOverload.append(tabAgent[p][0])
                        
                if not reussi and len(tabOverload) != 0:
                    for index in tabOverload:
                        agent = ap_copy[index]
                        reussi = faireTache(agent, tache, puni)
                        if reussi:
                            mission_reussi_per_exp += 1
                            gain_interet_per_exp += tache.weight
                            if agent.nature >0:
                                    mission_reussi_per_exp_ai += 1
                            break
                if not reussi:
                    missionfailed = True
        mission_reussi.append(mission_reussi_per_exp)
        mission_ai.append(mission_reussi_per_exp_ai)
        gain_interet.append(gain_interet_per_exp)
    return mission_reussi, mission_ai, gain_interet

def generateFixTimeTacheWeighted(timeTotal, timeRange,prob_tache = [8,1.5,0.5] ):
    start = 0
    tacheFixe = []
    while start < timeTotal:
        t = random.randint(timeRange[0], timeRange[1])
        level = random.choices([0,1,2], prob_tache, k= 1)[0]
        weight = t*random.randint(1,5)
        tacheFixe.append((t,level,weight))
        start = start+t
    return tacheFixe


def generateTacheFromFixSetWeighted(fixset):
    taches = []
    for t, l,w in fixset:
        cost = t*(l+1)
        taches.append(tache(l,cost,0,t,t, w))
    return taches

def generateTacheWeighted(ttotal,tr):
    tf = generateFixTimeTacheWeighted(ttotal,tr)
    taches = generateTacheFromFixSetWeighted(tf)
    nt = shuffleTache(taches)
    resetTdtt(nt)
    return nt