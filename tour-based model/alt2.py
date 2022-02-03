import datetime
import math
import os
import numpy as np
from numpy import ndarray
import time

import tools
from analysis import LWM_analysis


# Alternative 2 en générant toutes les tournées explicitement


def alt2_folder(input_folder, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, epsilon, max_steps):
    prod_file = input_folder + "/" + input_folder[input_folder.rfind("/")+1:] + "-productions.txt"
    attr_file = input_folder + "/" + input_folder[input_folder.rfind("/")+1:] + "-attractions.txt"
    costs_file = input_folder + "/" + input_folder[input_folder.rfind("/")+1:] + "-distances.txt"
    output_folder = os.getcwd() + "/output/" + input_folder[input_folder.rfind("/")+1:]
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    output_file_name = output_folder + "/" + output_folder[output_folder.rfind("/")+1:] + \
                       "_alt2_nb" + str(nb_stops_by_trips) + "_bd" + \
                       str(beta_dem) + "_bi" + str(beta_ini) + "_bint" + str(beta_inter) + \
                       "_e" + str(math.log10(epsilon)) + "_ms" + str(max_steps)
    alt_2(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, epsilon, max_steps,
          output_file_name)


def alt_2(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, epsilon, max_steps,
          output_file_name):
    # Lecture des données d'entrée
    costs = np.loadtxt(costs_file)
    productions = np.loadtxt(prod_file)
    attractions = np.loadtxt(attr_file)

    start_time = time.time()
    # Distribution de la demande
    demand = calc_potential_to_demand(productions, attractions, costs, beta_dem, epsilon, max_steps)
    # Conversion de la demande en trajets
    initial_trips = calc_initial_trips(demand, productions, nb_stops_by_trips, costs, beta_ini, epsilon, max_steps)
    intermediate_trips = calc_intermediate_trips(demand, productions, initial_trips, nb_stops_by_trips, costs, beta_inter, epsilon, max_steps)
    final_trips = calc_final_trips(demand, productions, intermediate_trips, nb_stops_by_trips)
    end_time = time.time()

    # ecrire dans un fichier de sortie
    np.savetxt((output_file_name + "_alt2_initial.txt"), initial_trips, fmt='%1.6f', delimiter='\t')
    sum1 = np.sum(intermediate_trips, 0)
    sum2 = np.sum(sum1, 0)
    np.savetxt((output_file_name + "_alt2_intermediate.txt"), sum2, fmt='%1.6f', delimiter='\t')
    np.savetxt((output_file_name + "_alt2_final.txt"), final_trips, fmt='%1.6f', delimiter='\t')

    post_process = LWM_analysis.post_processing(demand, nb_stops_by_trips, initial_trips, np.sum(sum1, 0), final_trips, costs)
    LWM_analysis.save_output(post_process, end_time - start_time, output_file_name)

"""
# Distribution de la demande
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
    # sum(j in S) x[i,j] = Ai
    constraints_set_2 = []
    for i in range(0, demand0_size[0]):
        curr_constraint = [(0, productions[i])]
        for j in range(0, demand0_size[1]):
            curr_constraint.append((i, j, 1))
        constraints_set_2.append(curr_constraint)

    # Définition des sets de contraintes d'égalité et d'inégalité
    eq_constraints = (constraints_set_1, constraints_set_2) # Deux sets de contrainte d'égalité
    ineq_constraints = () # Pas de contraintes d'inégalité

    # 3.2 Application algorithme de Furness
    return tools.furness(demand0, eq_constraints, ineq_constraints, furness_epsilon, max_furness_steps)
"""


# Etape 2 : Distribution de la demande
def calc_potential_to_demand(productions, attractions, costs, beta, furness_epsilon, max_furness_steps):
    print("tbf_demand :" + str(datetime.datetime.now()))
    ### Initialisation de la variable de sortie
    demand0 = np.zeros((len(productions), len(attractions)))

    ### Distribution initiale de la demande
    prob = tools.logit(costs, beta)
    for i in range(0, np.size(productions)):
        if productions[i] == 0:  # si pas de production, pas de demande
            continue
        for j in range(0, np.size(attractions)):
            if attractions[j] == 0: # si pas d'attraction, pas de demande
                continue
            demand0[i, j] = prob[i, j] * productions[i]

    ### Algorithme de Furness
    # Définitions des sets de contraintes dans Furness
    demand0_size = np.shape(demand0)
    # Premier set de contraintes : sum(i in S) x[i,j] = Aj
    constraints_set_1 = []
    for j in range(0, demand0_size[1]):
        curr_constraint = [(0, attractions[j])]
        for i in range(0, demand0_size[0]):
            if demand0[i, j] == 0:  # si pas de demande, pas de trajets
                continue
            curr_constraint.append((i, j, 1))
        constraints_set_1.append(curr_constraint)
    # Deuxième set de contraintes : sum(j in S) x[i,j] = Pi
    constraints_set_2 = []
    for i in range(0, demand0_size[0]):
        curr_constraint = [(0, productions[i])]
        for j in range(0, demand0_size[1]):
            if demand0[i, j] == 0:  # si pas de demande, pas de trajets
                continue
            curr_constraint.append((i, j, 1))
        constraints_set_2.append(curr_constraint)

    #  Définition des sets de contraintes d'inégalité et d'égalité
    eq_constraints = (constraints_set_1, constraints_set_2) #  Deux sets de contrainte d'égalité
    ineq_constraints = ()  # Pas de contraintes d'inégalité

    # Exécution de l'algorithme de Furness
    demand = tools.furness(demand0, eq_constraints, ineq_constraints, furness_epsilon, max_furness_steps)

    return demand

#  Trajets initiaux - renvoie la matrice des trajets initiaux
def calc_initial_trips(demand, productions, nb_stops_by_trips, costs, beta, epsilon, max_steps):
    print("alt2_initial :" + str(datetime.datetime.now()))
    ### Initialisation de la variable de sortie
    initial_trips: ndarray = np.ndarray((len(demand), len(demand)))

    ### Calcul préliminaire pour la distribution înitiale des trajets
    prob = tools.logit(costs, beta)

    ### Génération de trajets pour chaque zone de production
    for o in range(0, len(demand)):
        if productions[o] == 0:  # pas de productions, pas de trajets
            initial_trips[o] = np.zeros((1, len(demand)))
            continue
        ## Distribution initiale des trajets
        initial_trips_0 = np.ndarray((1, len(demand)))
        for j in range(0, len(demand)):
            initial_trips_0[0, j] = prob[o, j] * demand[o, j]

        # Définitions des sets de contraintes dans Furness
        # Premier set de contraintes : sum(j in S) s[o, j] = 1/nb_stops_by_trips * sum(j in S) x[o,j]
        constraints_set_1 = []
        curr_constraint = [(0, 0)]
        goal_value = 0
        for j in range(0, len(demand)):
            goal_value += demand[o, j]
            curr_constraint.append((0, j, 1))
        curr_constraint[0] = (0, goal_value / nb_stops_by_trips)  # contrainte d'égalite
        constraints_set_1.append(curr_constraint)

        # Deuxième set de contraintes : pour tout j, s[o, j] <= x[o,j]
        constraints_set_2 = []
        for j in range(0, len(demand)):
            curr_constraint = [(-1, demand[o, j]), (0, j, 1)]  # contrainte d'inégalité leq
            constraints_set_2.append(curr_constraint)

        #  Définition des sets de contraintes d'égalité et d'inégalité
        eq_constraints = (constraints_set_1,)
        ineq_constraints = (constraints_set_2,)

        # Application de Furness
        initial_trips[o] = tools.furness(initial_trips_0, eq_constraints, ineq_constraints, epsilon, max_steps)

    return initial_trips


# Trajets intermédiaires - renvoie la matrice des trajets intermédiaires
def calc_intermediate_trips(demand, productions, initial_trips, nb_stops_by_trips, costs, beta, epsilon, max_steps):
    print("alt2_intermediate :" + str(datetime.datetime.now()))
    ### Définition de paramètres accessoires
    # nb_stops_by_trips : nombre de points d'arrêt durant la tournée
    # nb_intermediate_trips = nb_stops_by_trips-1 : nombre de trajets intermédiaires
    nb_intermediate_trips = nb_stops_by_trips - 1

    ### Initialisation de la variable de sortie
    intermediate_trips = np.zeros((len(demand), nb_intermediate_trips, len(demand), len(demand)))

    ### Génération pour chaque zone d'origine
    for o in range(0, len(demand)):
        if productions[o] == 0: # si pas de production, pas de trajets
            intermediate_trips[o] = np.zeros((nb_intermediate_trips, len(demand), len(demand)))
            continue
        # si la production de la zone de référence n'est pas nulle, il peut y avoir des trajets

        ## Calculs préliminaires
        # Calcul des coûts à appliquer lors de la distribution initiale des trajets
        savings = tools.calculate_savings(o, costs)
        prob = tools.logit(savings, beta)
        #  Initialisation des variables intermédiaires
        intermediate_trips_o = np.zeros((nb_intermediate_trips, len(demand), len(demand)))

        # Préparation des valeurs à introduire dans l'algorithme de Furness
        goal_value_1 = np.zeros(len(demand))  # Valeurs de contraintes pour le premier set de contraintes
        goal_value_2 = np.zeros(len(demand))  # Valeurs de contraintes pour le deuxième set de contraintes
        for j in range(0, len(demand)):
            goal_value_1[j] = max(0, demand[o, j] - initial_trips[o, j])  # pour chaque j, x[o, j] - s[o, j]
            goal_value_2[j] = initial_trips[o, j]  # pour chaque j:  s[o, :]

        for n in range(0, nb_intermediate_trips):  # n : rang de trajet intermédiaire
            # Définition des valeurs de contraintes et de potentiels de distribution
            # emit - flux de trajets intermédiaires de rang n à émettre pour la zone o avec
            # receive - flux de trajets à recevoir avec des trajets intermédiaires de rang au moins n
            if n == 0:  # premier trajet intermédiaire
                # emit = initial_trips[o]  # pour chaque j, s[o, j]
                # receive = demand[o, :]  # option 1
                receive = demand[o, :] - initial_trips[o, :]  # option 2
            else:  # tous les autres trajets intermédiaires
                # receive est déjà égal à demand[o, :] - initial_trips[o, :] - sum (i in S, m in 0..n-2) t[o, m, i, j])
                emit = np.zeros(len(demand))  # remis à 0 à chaque passage de rang
                # goal_value_1 est déjà égal à sum(j in S) (d[o, j] - s[o,j] - sum (i in S, m in 0..n-2) t[o, m, i, j]))
                goal_value_2 = np.zeros(len(demand))  # remis à 0 à chaque passage de rang
                for j in range(0, len(demand)):
                    for i in range(0, len(demand)):
                        # emit[i] est égal à sum (j in S) t[o, n-1, j, i]
                        emit[i] += intermediate_trips_o[n-1, j, i]
                        receive[j] -= intermediate_trips_o[n-1, i, j]  # si option 2
                        # goal_value_2[i] est égal à sum (j in S) t[o, n-1, i, j]
                        goal_value_2[i] += intermediate_trips_o[n-1, j, i]
                        # goal_value_1[j] sum(i in S) (d[o, j] - s[o,j] - sum (i in S, m in 0...n-1) t[o, m, i, j])
                        goal_value_1[j] -= intermediate_trips_o[n-1, i, j]
                    # max pour éviter les valeurs négatives dûes aux arrondis
                    receive[j] = max(0, receive[j])
                    goal_value_1[j] = max(0, goal_value_1[j])

            ## Distribution initiale des trajets
            #  Initialisation des variables intermédiaires avec la zone d'origine et le rang
            intermediate_trips_o_n = np.zeros((len(demand), len(demand)))
            for i in range(0, len(demand)):
                for j in range(0, len(demand)):
                    # intermediate_trips_o_n[i, j] = prob[i, j] * emit[i] # calcul par emission
                    intermediate_trips_o_n[i, j] = prob[i, j] * receive[j]  # calcul par attraction

            # Définitions des sets de contraintes dans Furness
            # Premier set de contraintes :
            # sum(i in S) t[o, n, i, j] <= x[o,j] - s[o, j] - sum (m = 1:n-1) t[o, m, i, j] for all j in S
            constraints_set_1 = []
            for j in range(0, len(demand)):
                curr_constraint = [(-1, goal_value_1[j])]  # max pour éviter les valeurs négatives dûes aux arrondis
                for i in range(0, len(demand)):
                    curr_constraint.append((i, j, 1))
                constraints_set_1.append(curr_constraint)
            # Deuxième set de contraintes :
            # sum(j in S) t[o, n, i, j] = s[o, i] ou sum(j in S) t[o, n-1, j, i] for all i in S
            constraints_set_2 = []
            for i in range(0, len(demand)):
                curr_constraint = [(0, goal_value_2[i])]
                for j in range(0, len(demand)):
                    curr_constraint.append((i, j, 1))
                constraints_set_2.append(curr_constraint)

            # Définition des sets de contrainte d'égalité et d'inégalité
            eq_constraints = (constraints_set_2, )
            ineq_constraints = (constraints_set_1, )

            # Application de Furness
            intermediate_trips_o_n_fin = tools.furness(intermediate_trips_o_n, eq_constraints, ineq_constraints, epsilon, max_steps)
            intermediate_trips_o[n] = intermediate_trips_o_n_fin

        intermediate_trips[o] = intermediate_trips_o

    return intermediate_trips


# Trajets finaux
def calc_final_trips(demand, productions, intermediate_trips, nb_stops_by_trips):
    print("alt2_final :" + str(datetime.datetime.now()))
    nb_intermediate_trips = nb_stops_by_trips - 1
    final_trips = np.zeros((len(demand), len(demand)))
    for o in range(0, len(demand)):
        if productions[o] == 0: # si pas de productions dans la zone d'origine, pas de trajets finaux
            continue
        for i in range(0, len(demand)):
            final_trips[i, o] = 0
            for j in range(0, len(demand)):
                final_trips[i, o] += intermediate_trips[o, nb_intermediate_trips-1, j, i]

    return final_trips