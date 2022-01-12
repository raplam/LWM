import datetime
import math
import os
import numpy as np
from numpy import ndarray
import time

import tools
from analysis import LWM_analysis


# Alternative 1 en générant les trajets retours au début


def alt1_folder(input_folder, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, beta_final, epsilon, max_steps):
    prod_file = input_folder + "/" + input_folder[input_folder.rfind("/") + 1:] + "-productions.txt"
    attr_file = input_folder + "/" + input_folder[input_folder.rfind("/") + 1:] + "-attractions.txt"
    costs_file = input_folder + "/" + input_folder[input_folder.rfind("/") + 1:] + "-distances.txt"
    output_folder = os.getcwd() + "/output/" + input_folder[input_folder.rfind("/") + 1:]
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    output_file_name = output_folder + "/" + output_folder[output_folder.rfind("/") + 1:] + \
                       "_alt1_nb" + str(nb_stops_by_trips) + "_bd" + \
                       str(beta_dem) + "_bi" + str(beta_ini) + "_bint" + str(beta_inter) + "_bf" + str(beta_final) + \
                       "_e" + str(math.log10(epsilon)) + "_ms" + str(max_steps)
    alt_1(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, beta_final, epsilon,
          max_steps,
          output_file_name)


def alt_1(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, beta_final, epsilon,
          max_steps, output_file_name):
    # Lecture des données d'entrée
    costs = np.loadtxt(costs_file)
    productions = np.loadtxt(prod_file)
    attractions = np.loadtxt(attr_file)

    # Conversion de la demande en trajets
    start_time = time.time()
    demand = calc_potential_to_demand(productions, attractions, costs, beta_dem, epsilon, max_steps)
    initial_trips = calc_initial_trips(productions, attractions, demand, nb_stops_by_trips, costs, beta_ini, epsilon,
                                       max_steps)
    final_trips = calc_final_trips(productions, attractions, nb_stops_by_trips, costs, beta_final, epsilon, max_steps)
    intermediate_trips = calc_intermediate_trips(attractions, initial_trips, final_trips, costs, beta_inter, epsilon,
                                                 max_steps)
    end_time = time.time()

    # ecrire dans un fichier de sortie
    np.savetxt((output_file_name + "_alt1_initial.txt"), initial_trips, fmt='%1.6f', delimiter='\t')
    np.savetxt((output_file_name + "_alt1_intermediate.txt"), intermediate_trips, fmt='%1.6f', delimiter='\t')
    np.savetxt((output_file_name + "_alt1_final.txt"), final_trips, fmt='%1.6f', delimiter='\t')

    post_process = LWM_analysis.post_processing(demand, nb_stops_by_trips, initial_trips, intermediate_trips,
                                                final_trips, costs)
    LWM_analysis.save_output(post_process, end_time - start_time, output_file_name)


# Etape 2 : Distribution de la demande (non utilisée dans les contraintes par la suite)
def calc_potential_to_demand(productions, attractions, costs, beta, furness_epsilon, max_furness_steps):
    # Initialisation de la variable de sortie
    demand0 = np.zeros((len(productions), len(attractions)))

    # Calcul des valeurs de demande à partir du logit
    prob = tools.logit(costs, beta)
    for i in range(0, np.size(productions)):
        if productions[i] == 0:  # pas de demande si pas de production
            continue
        for j in range(0, np.size(attractions)):
            demand0[i, j] = prob[i, j] * productions[i]

    # Algorithme de Furness
    # Définitions des sets de contraintes dans Furness
    demand0_size = np.shape(demand0)
    # Premier set de contraintes :
    # sum(i in S) x[i,j] = A[j]
    constraints_set_1 = []
    for j in range(0, demand0_size[1]):
        curr_constraint = [(0, attractions[j])]
        for i in range(0, demand0_size[0]):
            curr_constraint.append((i, j, 1))
        constraints_set_1.append(curr_constraint)
    # Deuxième set de contraintes :
    # sum(j in S) x[i,j] = P[i]
    constraints_set_2 = []
    for i in range(0, demand0_size[0]):
        curr_constraint = [(0, productions[i])]
        for j in range(0, demand0_size[1]):
            curr_constraint.append((i, j, 1))
        constraints_set_2.append(curr_constraint)

    #  Définition des sets de contrainte d'égalité et d'inégalité
    eq_constraints = (constraints_set_1, constraints_set_2)  # Deux contraintes d'inégalité
    ineq_constraints = ()  # Pas de contraintes d'égalité

    # Exécution algorithme de Furness
    demand = tools.furness(demand0, eq_constraints, ineq_constraints, furness_epsilon, max_furness_steps)

    return demand


# Trajets initiaux - renvoie la matrice des trajets initiaux et la demande mise à jour
def calc_initial_trips(productions, attractions, demand, nb_stops_by_trips, costs, beta, epsilon, max_steps):
    print("alt1_initial :" + str(datetime.datetime.now()))
    ### Initialisation de la variable de sortie
    trips_0: ndarray = np.zeros((len(productions), len(attractions)))

    ### Distribution initiale des trajets
    prob = tools.logit(costs, beta)
    for o in range(0, len(productions)):
        if productions[o] == 0:  # pas de productions, pas de trajets initiaux
            continue
        for j in range(0, len(attractions)):
            trips_0[o, j] = prob[o, j] * attractions[j]  # demand[o, j]

    ### Algorithme de Furness
    # Définitions des sets de contraintes dans Furness
    # Premier set de contraintes :
    # pour chaque o, sum(j in S) s[o, j] = 1/nb_stops_by_trips * productions[o]
    constraints_set_1 = []
    for o in range(0, len(productions)):
        if productions[o] == 0:  # si pas de productions, pas de trajets
            continue
        curr_constraint = [(0, productions[o] / nb_stops_by_trips)]  # contrainte d'égalité
        for j in range(0, len(attractions)):
            if attractions[j] == 0:  # si pas d'attractions, pas pas de trajets
                continue
            curr_constraint.append((o, j, 1))
        constraints_set_1.append(curr_constraint)

    # Deuxième set de contraintes :
    # pour chaque j, sum(o in S) s[o, j] <= Aj
    constraints_set_2 = []
    for j in range(0, len(attractions)):
        if attractions[j] == 0:  # si pas d'attractions, pas de trajets
            continue
        curr_constraint = [(-1, attractions[j])]  # contrainte d'inégalité leq
        for o in range(0, len(productions)):
            if productions[o] == 0:  # si pas de productions, pas de trajets
                continue
            curr_constraint.append((o, j, 1))
        constraints_set_2.append(curr_constraint)

    # Définition des sets de contraintes d'égalité et d'inégalité
    eq_constraints = (constraints_set_1,)
    ineq_constraints = (constraints_set_2,)

    # Application Algorithme de Furness
    trips = tools.furness(trips_0, eq_constraints, ineq_constraints, epsilon, max_steps)

    return trips


# Trajets finaux - renvoie la matrice des trajets finaux
def calc_final_trips(productions, attractions, nb_stops_by_trips, costs, beta, epsilon, max_steps):
    print("alt1_final :" + str(datetime.datetime.now()))
    # Initialisation des variables
    trips_0: ndarray = np.zeros((len(productions), len(attractions)))

    # Distribution avec logit
    prob = tools.logit(costs, beta)
    for o in range(0, len(productions)):
        if productions[o] == 0:
            continue
        for j in range(0, len(attractions)):
            trips_0[j, o] = prob[j, o] * productions[o] / nb_stops_by_trips

    # Définitions des sets de contraintes dans Furness
    # Premier set de contraintes : sum(j in S) r[j, o] = 1/nb_stops_by_trips * productions[o] for all o
    constraints_set_1 = []
    for o in range(0, len(productions)):
        if productions[o] == 0:  # pas de productions, pas de trajets
            continue
        curr_constraint = [(0, productions[o] / nb_stops_by_trips)]
        for i in range(0, len(attractions)):
            if attractions[i] == 0:  # pas d'attractions, pas de trajets
                continue
            curr_constraint.append((i, o, 1))
        constraints_set_1.append(curr_constraint)
    # Deuxième set de contraintes : sum(o in S) r[i, o] <= Ai for all i
    constraints_set_2 = []
    for i in range(0, len(attractions)):
        curr_constraint = [(-1, attractions[i])]  # contrainte d'inégalité leq
        for o in range(0, len(productions)):
            if productions[o] == 0:
                continue
            curr_constraint.append((i, o, 1))
        constraints_set_2.append(curr_constraint)

    # Contraintes
    eq_constraints = (constraints_set_1,)
    ineq_constraints = (constraints_set_2,)

    # Algorithme de Furness
    trips = tools.furness(trips_0, eq_constraints, ineq_constraints, epsilon, max_steps)

    return trips


# Trajets intermédiaires - renvoie la matrice des trajets intermédiaires
def calc_intermediate_trips(attractions, initial_trips, final_trips, costs, beta, epsilon, max_steps):
    print("alt1_intermediate :" + str(datetime.datetime.now()))
    # Initialisation des variables
    intermediate_trips_0 = np.zeros((len(attractions), len(attractions)))

    ### Distribution avec logit
    prob = tools.logit(costs, beta)
    # Distribution initiale seulement liée à la distance
    # intermediate_trips = prob

    # Autres distributions initiales
    for i in range(0, len(attractions)):
        value = attractions[i]
        for o in range(0, len(attractions)):
                  value -= initial_trips[o, i]
             #    value -= final_trips[i, o]
        for j in range(0, len(attractions)):
            intermediate_trips_0[j, i] = prob[j, i] * max(value, 0)
            # utilisation de max pour éviter les valeurs négatives

    ### Définitions des sets de contraintes dans Furness
    # Premier set de contraintes :
    # sum(i in S) t[i, j] = A[j] - sum(i in S) s[i, j] for all j in S
    constraints_set_1 = []
    for j in range(0, len(attractions)):
        goal_value = attractions[j]
        curr_constraint = [(0, 0)]
        for i in range(0, len(attractions)):
            curr_constraint.append((i, j, 1))
            goal_value -= initial_trips[i, j]
        curr_constraint[0] = (0, max(0, goal_value))
        constraints_set_1.append(curr_constraint)

    # Deuxième set de contraintes :
    # sum(j in S) t[i, j] = A[i] - sum(j in S) r[i, j] for all i in S
    constraints_set_2 = []
    for i in range(0, len(attractions)):
        goal_value = attractions[i]
        curr_constraint = [(0, attractions[i])]
        for j in range(0, len(attractions)):
            curr_constraint.append((i, j, 1))
            goal_value -= final_trips[i, j]
        curr_constraint[0] = (0, max(0, goal_value))
        constraints_set_2.append(curr_constraint)

    # Définition des sets de contrainte d'égalité et d'inégalité
    eq_constraints = (constraints_set_1, constraints_set_2)  # Deux contraintes d'égalité
    ineq_constraints = ()  # Pas de contraintes d'inégalité

    # Exécution Algorithme de Furness
    intermediate_trips = tools.furness(intermediate_trips_0, eq_constraints, ineq_constraints, epsilon, max_steps)

    return intermediate_trips