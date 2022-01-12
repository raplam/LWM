import datetime
import math
import os
import numpy as np
from numpy import ndarray
import time

import tools
from analysis import LWM_analysis


# Alternative 1 en générant les trajets retours à la fin


def alt_1r_folder(input_folder, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, beta_final, epsilon, max_steps):
    prod_file = input_folder + "/" + input_folder[input_folder.rfind("/")+1:] + "-productions.txt"
    attr_file = input_folder + "/" + input_folder[input_folder.rfind("/")+1:] + "-attractions.txt"
    costs_file = input_folder + "/" + input_folder[input_folder.rfind("/")+1:] + "-distances.txt"
    output_folder = os.getcwd() + "/output/" + input_folder[input_folder.rfind("/")+1:]
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    output_file_name = output_folder + "/" + output_folder[output_folder.rfind("/")+1:] + \
                       "_alt1r_nb" + str(nb_stops_by_trips) + "_bd" + \
                       str(beta_dem) + "_bi" + str(beta_ini) + "_bint" + str(beta_inter) + \
                       "_e" + str(math.log10(epsilon)) + "_ms" + str(max_steps)
    alt_1r(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, beta_final, epsilon, max_steps,
           output_file_name)


def alt_1r(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, beta_final, epsilon, max_steps, output_file_name):
    # Lecture des données d'entrée
    costs = np.loadtxt(costs_file)
    productions = np.loadtxt(prod_file)
    attractions = np.loadtxt(attr_file)

    # Conversion de la demande en trajets
    start_time = time.time()
    demand = calc_potential_to_demand(productions, attractions, costs, beta_dem, epsilon, max_steps)
    initial_trips = calc_initial_trips(productions, attractions, demand, nb_stops_by_trips, costs, beta_ini, epsilon, max_steps)
    intermediate_trips = calc_intermediate_trips(attractions, initial_trips, costs, beta_inter, epsilon, max_steps)
    final_trips = calc_final_trips(initial_trips, intermediate_trips, productions, attractions, costs, beta_final, epsilon, max_steps)
    end_time = time.time()

    # ecrire dans un fichier de sortie
    np.savetxt((output_file_name + "_alt1r_initial.txt"), initial_trips, fmt='%1.4f', delimiter='\t')
    np.savetxt((output_file_name + "_alt1r_intermediate.txt"), intermediate_trips, fmt='%1.4f', delimiter='\t')
    np.savetxt((output_file_name + "_alt1r_final.txt"), final_trips, fmt='%1.4f', delimiter='\t')

    post_process = LWM_analysis.post_processing(demand, nb_stops_by_trips, initial_trips, intermediate_trips, final_trips, costs)
    LWM_analysis.save_output(post_process, end_time - start_time, output_file_name)


# Etape 1 : Données : productions et attractions
# Utilisation de fonctions existantes

def calc_potential_to_demand(productions, attractions, costs, beta, furness_epsilon, max_furness_steps):
    # Initialisation de la variable de sortie
    demand0 = np.zeros((len(productions), len(attractions)))

    # Calcul des valeurs de demande à partir du logit
    prob = tools.logit(costs, beta)
    for i in range(0, np.size(productions)):
        for j in range(0, np.size(attractions)):
            demand0[i, j] = prob[i, j] * productions[i]

    # Algorithme de Furness
    # Définitions des sets de contraintes dans Furness
    demand0_size = np.shape(demand0)
    # Premier set de contraintes :
    # sum(i in S) x[i,j] = Aj
    constraints_set_1 = []
    for j in range(0, demand0_size[1]):
        curr_constraint = [(0, attractions[j])]
        for i in range(0, demand0_size[0]):
            curr_constraint.append((i, j, 1))
        constraints_set_1.append(curr_constraint)
    # Deuxième set de contraintes :
    # sum(j in S) x[i,j] = Pi
    constraints_set_2 = []
    for i in range(0, demand0_size[0]):
        curr_constraint = [(0, productions[i])]
        for j in range(0, demand0_size[1]):
            curr_constraint.append((i, j, 1))
        constraints_set_2.append(curr_constraint)

    # Définition des contraintes d'égalité et d'inégalité
    eq_constraints = (constraints_set_1, constraints_set_2)
    ineq_constraints = ()

    # Application algorithme de Furness
    demand = tools.furness(demand0, eq_constraints, ineq_constraints, furness_epsilon, max_furness_steps)

    return demand


# Etape 2: Trajets initiaux
def calc_initial_trips(productions, attractions, demand, nb_stops_by_trips, costs, beta, epsilon, max_steps):  # renvoie la matrice des trajets initiaux et la demande mise à jour
    print("alt1r_initial :" + str(datetime.datetime.now()))
    # Initialisation de la variable de sortie
    trips_0: ndarray = np.zeros((len(productions), len(attractions)))

    prob = tools.logit(costs, beta)
    for o in range(0, len(productions)):
        for j in range(0, len(attractions)):
            trips_0[o, j] = prob[o, j] * attractions[j]  # demand[o, j]

    # Algorithme de Furness
    # Définitions des sets de contraintes dans Furness
    # Premier set de contraintes :
    # pour chaque o, sum(j in S) s[o, j] = 1/nb_stops_by_trips * productions[o]
    constraints_set_1 = []
    for o in range(0, len(productions)):
        curr_constraint = [(0, productions[o] / nb_stops_by_trips)]
        for j in range(0, len(attractions)):
            curr_constraint.append((o, j, 1))
        constraints_set_1.append(curr_constraint)
    # Deuxième set de contraintes :
    # sum(o in S) s[o, j] <= Aj pour chaque j
    constraints_set_2 = []
    for j in range(0, len(attractions)):
        curr_constraint = [(-1, attractions[j])]  # contrainte d'inégalité
        for o in range(0, len(productions)):
            curr_constraint.append((o, j, 1))
        constraints_set_2.append(curr_constraint)
    # Contraintes
    constraints = (constraints_set_2, constraints_set_1)
    eq_constraints = (constraints_set_1,)
    ineq_constraints = (constraints_set_2,)

    # Exécution algorithme de Furness
    trips = tools.furness(trips_0, eq_constraints, ineq_constraints, epsilon, max_steps)

    return trips


# Etape 3 : Trajets intermédiaire
def calc_intermediate_trips(attractions, initial_trips, costs, beta, epsilon, max_steps):  # renvoie la matrice des trajets intermédiaires
    print("alt1_intermediate :" + str(datetime.datetime.now()))
    # Initialisation des variables
    intermediate_trips_0 = np.zeros((len(attractions), len(attractions)))

    # Distribution avec logit - quel potentiel émetteur pour chaque zone à appliquer dans le logit ?
    # On travaille avec le potentiel attracteur
    prob = tools.logit(costs, beta)
    for i in range(0, len(attractions)):
        value = attractions[i]
        for o in range(0, len(attractions)):
            value -= initial_trips[o, i]
        for j in range(0, len(attractions)):
            intermediate_trips_0[i, j] = prob[i, j] * attractions[j] # max(value, 0)  # utilisation max pour éviter les valeurs négatives

    # Définitions des sets de contraintes dans Furness
    # Premier set de contraintes:
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
    # sum(j in S) t[i, j] <= A[i] pour chaque i
    constraints_set_2 = []
    for i in range(0, len(attractions)):
        curr_constraint = [(-1, attractions[i])]
        for j in range(0, len(attractions)):
            curr_constraint.append((i, j, 1))
        constraints_set_2.append(curr_constraint)

     # Définition des sets de contrainte d'égalité et d'inégalité
    eq_constraints = (constraints_set_1, constraints_set_2,)
    ineq_constraints = ()

    # Exécution Algorithme de Furness
    intermediate_trips = tools.furness(intermediate_trips_0, eq_constraints, ineq_constraints, epsilon, max_steps)

    return intermediate_trips


# Trajets finaux
def calc_final_trips(initial_trips, intermediate_trips, productions, attractions, costs, beta, epsilon, max_steps):
    print("alt1_final :" + str(datetime.datetime.now()))
    # Initialisation de la variable
    final_trips_0 = np.zeros((len(attractions), len(attractions)))

    # Distribution avec logit
    prob = tools.logit(costs, beta)
    for i in range(0, len(attractions)):
        for j in range(0, len(attractions)):
            final_trips_0[i, j] = prob[i, j] * productions[j]
        """
        value = attractions[i]
        for j in range(0, len(attractions)):
            value -= intermediate_trips[i, j]
        for j in range(0, len(attractions)):
            final_trips_0[i, j] = prob[i, j] * max(value, 0)
            # should we use productions ?
            # utilisation max si valeurs négatives
        """

    # Définitions des sets de contraintes dans Furness
    # Premier set de contraintes :
    # sum(j in S) r[i, j] = A[i] - sum(j in S) t[i, j] pour tout i
    constraints_set_1 = []
    for i in range(0, len(attractions)):
        goal_value = attractions[i]
        curr_constraint = [(0, 0)]
        for j in range(0, len(attractions)):
            curr_constraint.append((i, j, 1))
            goal_value -= intermediate_trips[i, j]
        curr_constraint[0] = (0, max(0, goal_value))
        constraints_set_1.append(curr_constraint)
    # Deuxième set de contraintes :
    # sum(j in S) r[j, i] = sum(j in S) s[i, j] pour tout i
    constraints_set_2 = []
    for i in range(0, len(attractions)):
        goal_value = 0
        curr_constraint = [(0, 0)]
        for j in range(0, len(attractions)):
            goal_value += initial_trips[i, j]
            curr_constraint.append((j, i, 1))
        curr_constraint[0] = (0, goal_value)
        constraints_set_2.append(curr_constraint)

    # Définition des sets de containtes d'égalité
    eq_constraints = (constraints_set_1, constraints_set_2)
    ineq_constraints = ()

    # Exécution Algorithme de Furness
    final_trips = tools.furness(final_trips_0, eq_constraints, ineq_constraints, epsilon, max_steps)

    return final_trips