import random
import numpy as np
import copy 
import statistics as st


def simule_exp_prob(nb_mission, nb_coef, n_d, t_s, cp, cr, ce, exp_seuil, exp_max, exp_min, proba, step):
    t_seq= [random.uniform(5, 15) for _ in range(nb_mission)]
    size_t = len(np.arange(proba[0], proba[1], step))
    exp_init=0
    exp = [0]*size_t
    
    if exp_init > exp_seuil[1]:
            random_level = [random.randint(0, 2) for _ in range(nb_mission)]
            exp_level = 2
    elif exp_init > exp_seuil[0]:
            random_level = [random.randint(0, 1) for _ in range(nb_mission)]
            exp_level = 1
    else:
        random_level =  [0] * nb_mission
        exp_level = 0
    muti = 0
    for j in np.arange(proba[0], proba[1], step):
        random_bools = [random.choices([True, False],weights= [j,1-j]) for _ in range(nb_mission)]
        for i in range(nb_mission):
            if(random_bools[i][0]):
                if(exp[muti] < exp_max):
                    exp[muti] = exp[muti] +t_seq[i]/t_s*cr[random_level[i]]*nb_coef
                    if(exp[muti] > exp_max):
                        exp[muti] = exp_max

            else:
                exp[muti] = exp[muti] - t_s/t_seq[i]*cp[random_level[i]]*nb_coef*ce[exp_level]
                if (exp[muti] < 0):
                    exp[muti] = 0;
        muti = muti+1
    return exp


def simule_exp(nb_mission, nb_coef, n_d, t_s, cp, cr, ce, exp_seuil, exp_max, exp_min, proba):
    t_seq= [random.uniform(5, 15) for _ in range(nb_mission)]

    random_bools = [random.choices([True, False],weights= proba) for _ in range(nb_mission)]
    exp_init=0
    exp = [0]*nb_coef
    if exp_init > exp_seuil[1]:
            random_level = [random.randint(0, 2) for _ in range(nb_mission)]
            exp_level = 2
    elif exp_init > exp_seuil[0]:
            random_level = [random.randint(0, 1) for _ in range(nb_mission)]
            exp_level = 1
    else:
        random_level =  [0] * nb_mission
        exp_level = 0
    for muti in range(0,nb_coef):
        coef = 1+muti
        for i in range(nb_mission):
            if(random_bools[i][0]):
                if(exp[muti] < exp_max):
                    exp[muti] = exp[muti] +t_seq[i]/t_s*cr[random_level[i]]*coef
                    if(exp[muti] > exp_max):
                        exp[muti] = exp_max

            else:
                exp[muti] = exp[muti] - t_s/t_seq[i]*cp[random_level[i]]*coef*ce[exp_level]
                if (exp[muti] < 0):
                    exp[muti] = 0;
    return exp

def simule_exp_avance(nb_mission, nb_coef, n_d, t_s, cp, cr, ce, exp_seuil, exp_max, exp_min, proba, exp_init):
    exp = [exp_init]*nb_coef
    t_seq= [random.uniform(5, 15) for _ in range(nb_mission)]
    
    if exp_init > exp_seuil[1]:
            random_level = [random.randint(0, 2) for _ in range(nb_mission)]
            exp_level = 2
    elif exp_init > exp_seuil[0]:
            random_level = [random.randint(0, 1) for _ in range(nb_mission)]
            exp_level = 1
    else:
        random_level =  [0] * nb_mission
        exp_level = 0

    elements = [True, False]

    random_bools = []
    for i in range(0,nb_mission):
        if random_level[i] == 2:
            chosen_element = random.choices(elements, weights=proba[2], k=1)[0]
        elif random_level[i] == 1:
            chosen_element = random.choices(elements, weights=proba[1], k=1)[0]
        else:
            chosen_element = random.choices(elements, weights=proba[0], k=1)[0]
        random_bools.append(chosen_element)
    for muti in range(0,nb_coef):
        coef = 1+muti
        for i in range(nb_mission):
            if(random_bools[i]):
                if(exp[muti] < exp_max):
                    exp[muti] = exp[muti] +t_seq[i]/t_s*cr[random_level[i]]*coef
                    if(exp[muti] > exp_max):
                        exp[muti] = exp_max

            else:
                exp[muti] = exp[muti] - t_s/t_seq[i]*cp[random_level[i]]*coef*ce[exp_level]
                if (exp[muti] < 0):
                    exp[muti] = 0;
    return exp
def simule_exp_prob(nb_mission, nb_coef, n_d, t_s, cp, cr, ce, exp_seuil, exp_max, exp_min, proba, step):
    t_seq= [random.uniform(5, 15) for _ in range(nb_mission)]
    size_t = len(np.arange(proba[0], proba[1], step))
    exp_init=0
    exp = [0]*size_t
    
    if exp_init > exp_seuil[1]:
            random_level = [random.randint(0, 2) for _ in range(nb_mission)]
            exp_level = 2
    elif exp_init > exp_seuil[0]:
            random_level = [random.randint(0, 1) for _ in range(nb_mission)]
            exp_level = 1
    else:
        random_level =  [0] * nb_mission
        exp_level = 0
    muti = 0
    for j in np.arange(proba[0], proba[1], step):
        random_bools = [random.choices([True, False],weights= [j,1-j]) for _ in range(nb_mission)]
        for i in range(nb_mission):
            if(random_bools[i][0]):
                if(exp[muti] < exp_max):
                    exp[muti] = exp[muti] +t_seq[i]/t_s*cr[random_level[i]]*nb_coef
                    if(exp[muti] > exp_max):
                        exp[muti] = exp_max

            else:
                exp[muti] = exp[muti] - t_s/t_seq[i]*cp[random_level[i]]*nb_coef*ce[exp_level]
                if (exp[muti] < 0):
                    exp[muti] = 0;
        muti = muti+1
    return exp

def simule_exp_avance_prob(nb_mission, nb_coef, n_d, t_s, cp, cr, ce, exp_seuil, exp_max, exp_min, proba, exp_init, prob_tache):
    exp = [exp_init]*nb_coef
    t_seq= [random.uniform(5, 15) for _ in range(nb_mission)]
    
    if exp_init > exp_seuil[1]:
            random_level = random.choices([0,1,2], prob_tache, k= nb_mission)
            exp_level = 2
    elif exp_init > exp_seuil[0]:
            random_level = random.choices([0,1], prob_tache, k= nb_mission)
            exp_level = 1
    else:
        random_level =  [0] * nb_mission
        exp_level = 0
    
    elements = [True, False]

    random_bools = []
    for i in range(0,nb_mission):
        if random_level[i] == 2:
            chosen_element = random.choices(elements, weights=proba[2], k=1)[0]
        elif random_level[i] == 1:
            chosen_element = random.choices(elements, weights=proba[1], k=1)[0]
        else:
            chosen_element = random.choices(elements, weights=proba[0], k=1)[0]
        random_bools.append(chosen_element)
    
    for muti in range(0,nb_coef):
        coef = 1+muti
        for i in range(nb_mission):
            if(random_bools[i]):
                if(exp[muti] < exp_max):
                    exp[muti] = exp[muti] +cr[random_level[i]]*1
                    if(exp[muti] > exp_max):
                        exp[muti] = exp_max

            else:
                exp[muti] = exp[muti] - cp[random_level[i]]*1*ce[exp_level]
                if (exp[muti] < 0):
                    exp[muti] = 0;
    return exp


# Cette fonction résout un système d'équations linéaires pour déterminer les coefficients
# qui équilibrent les probabilités de transition entre différents niveaux d'utilisateur
# en fonction des contraintes spécifiées. Les coefficients 'cr1', 'cr2', 'cr3', 'cp1', 'cp2', et 'cp3'
# représentent les facteurs de transition entre les niveaux et sont calculés de manière à satisfaire
# les équations de contrainte basées sur les probabilités et les coefficients d'entrée.
# Les résultats sont retournés sous forme de liste de dictionnaires, chaque dictionnaire
# représentant une solution possible. Cette fonction peut être utile dans divers contextes
# où vous devez modéliser et équilibrer des transitions probabilistes entre états ou niveaux.
def defini_coef_avec_equation_de_system(prob, prob_tache, ce=[1,2,3]):
    # Définition des symboles pour les coefficients
    cr1, cr2, cr3, cp1, cp2, cp3 = symbols('cr1 cr2 cr3 cp1 cp2 cp3')
    
    # Configuration des équations (contraintes) basées sur les probabilités et coefficients d'entrée

    # Contraintes pour le niveau débutant (niveau 1)
    # constraint1 : Équilibre la probabilité pour un débutant de rester au même niveau
    # constraint2 : Équilibre la probabilité pour un débutant de passer au niveau 2
    constraint1 = Eq(prob[0][0] * cr1 / ce[0] - (1-prob[0][0]) * cp1 * ce[0], 0)
    constraint2 = Eq(prob[0][1] * cr1 / ce[0] - (1-prob[0][1]) * cp1 * ce[0], 2)

    # Contraintes pour le niveau intermédiaire (niveau 2)
    # Ces contraintes équilibrent les probabilités de transition entre les niveaux pour un utilisateur intermédiaire
    constraint3 = Eq(prob_tache[0][0] * (prob[1][0] * cr1 / ce[1] - (1-prob[1][0]) * cp1 * ce[1]) + prob_tache[0][1] * (prob[1][2] * cr2 / ce[0] - (1-prob[1][2]) * cp2 * ce[1]), 0)
    constraint4 = Eq(prob_tache[0][0] * (prob[1][1] * cr1 / ce[1] - (1-prob[1][1]) * cp1 * ce[1]) + prob_tache[0][1] * ( prob[1][3] * cr2 / ce[0]- (1-prob[1][3]) * cp2 * ce[1]), 2.5)

    # Contraintes pour le niveau avancé (niveau 3)
    # Ces contraintes gèrent les probabilités de transition pour un utilisateur avancé
    constraint5 = Eq(prob_tache[1][0] * (prob[2][0] * cr1/ce[2] - (1-prob[2][0]) * cp1 * ce[2]) + prob_tache[1][1] * (prob[2][2] * cr2/ce[1] - (1-prob[2][2]) * cp2 *ce[2]) + prob_tache[1][2] * (prob[2][4] * cr3 / ce[0]- (1-prob[2][4]) * cp3 * ce[2]), 0)
    constraint6 = Eq(prob_tache[1][0] * (prob[2][1] * cr1/ce[2] - (1-prob[2][1]) * cp1 * ce[2]) + prob_tache[1][1] * (prob[2][3] * cr2/ce[1] - (1-prob[2][3]) * cp2 *ce[2]) + prob_tache[1][2] * (prob[2][5] * cr3 / ce[0]- (1-prob[2][5]) * cp3 * ce[2]), 1)
    
    # Combinaison de toutes les contraintes dans une liste unique
    equations = [constraint1, constraint2, constraint3, constraint4, constraint5, constraint6]

    # Résolution du système d'équations pour trouver les valeurs des coefficients
    # La fonction retourne une liste de dictionnaires, chaque dictionnaire représentant une solution possible
    solutions = solve(equations, (cr1, cr2, cr3, cp1, cp2, cp3), dict=True)
    return solutions
