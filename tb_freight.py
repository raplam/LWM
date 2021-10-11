import tools
import numpy as np
from numpy import ndarray

# TB-Freight


# Description des étapes et définitions des fonctions
def tb_freight(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, epsilon, max_steps,
               output_file_name):
    # Lecture des données d'entrée
    costs = np.loadtxt(costs_file)
    productions = np.loadtxt(prod_file)
    attractions = np.loadtxt(attr_file)

    # Distribution de la demande
    demand = calc_potential_to_demand(productions, attractions, costs, beta_dem, epsilon, max_steps)

    # Conversion de la demande en trajets
    initial_trips = calc_initial_trips(demand, productions, nb_stops_by_trips, costs, beta_ini, epsilon, max_steps)
    intermediate_trips = calc_intermediate_trips(demand, initial_trips, costs, beta_inter, epsilon, max_steps)
    final_trips = calc_final_trips(demand, initial_trips, intermediate_trips)

    # Output
    np.savetxt((output_file_name + "_tbf_initial.txt"), initial_trips, fmt='%1.2f', delimiter='\t')
    np.savetxt((output_file_name + "_tbf_intermediate.txt"), np.sum(intermediate_trips, 0), fmt='%1.2f', delimiter='\t')
    np.savetxt((output_file_name + "_tbf_final.txt"), final_trips, fmt='%1.2f', delimiter='\t')


# Etape 1 : données
# Utilisation de fonctions existantes


# Etape 2 : Distribution de la demande
def calc_potential_to_demand(productions, attractions, costs, beta, furness_epsilon, max_furness_steps):
    # initialisation
    demand0 = np.zeros((len(productions), len(attractions)))

    # Calcul des valeurs de demande à partir du logit
    prob = tools.logit(costs, beta)
    for i in range(0, np.size(productions)):
        for j in range(0, np.size(attractions)):
            demand0[i, j] = prob[i, j] * productions[i]

    # Algorithme de Furness
    # Définitions des sets de contraintes dans Furness
    demand0_size = np.shape(demand0)
    # Premier set de contraintes : sum(i in S) x[i,j] = Aj
    constraints_set_1 = []
    for j in range(0, demand0_size[1]):
        curr_constraint = [(0, attractions[j])]
        for i in range(0, demand0_size[0]):
            curr_constraint.append((i, j, 1))
        constraints_set_1.append(curr_constraint)
    # Deuxième set de contraintes : sum(j in S) x[i,j] = Pi
    constraints_set_2 = []
    for i in range(0, demand0_size[0]):
        curr_constraint = [(0, productions[i])]
        for j in range(0, demand0_size[1]):
            curr_constraint.append((i, j, 1))
        constraints_set_2.append(curr_constraint)
    # Contraintes
    # constraints = (constraints_set_1, constraints_set_2)
    eq_constraints = (constraints_set_1, constraints_set_2)
    ineq_constraints = ()

    # Application algorithme de Furness
    demand = tools.furness(demand0, eq_constraints, ineq_constraints, furness_epsilon, max_furness_steps)

    return demand


# Etape 3.1 : Trajets initiaux - renvoie la matrice des trajets initiaux
def calc_initial_trips(demand, productions, nb_stops_by_trips, costs, beta, epsilon, max_steps):
    initial_trips: ndarray = np.ndarray((len(demand), len(demand)))

    prob = tools.logit(costs, beta)
    for o in range(0, len(demand)):
        initial_trips_0 = np.ndarray((1, len(demand)))
        for j in range(0, len(demand)):
            initial_trips_0[0, j] = prob[o, j] * productions[o] / nb_stops_by_trips

        # Algorithme de Furness
        # Définitions des sets de contraintes dans Furness
        # Premier set de contraintes : sum(j in S) s[o, j] = 1/nb_stops_by_trips * sum(j in S) x[o,j] for every o
        constraints_set_1 = []
        curr_constraint = [(0, 0)]
        goal_value = 0
        for j in range(0, len(demand)):
            goal_value += demand[o, j]
            curr_constraint.append((0, j, 1))
        curr_constraint[0] = (0, goal_value / nb_stops_by_trips)
        constraints_set_1.append(curr_constraint)
        # Deuxième set de contraintes : s[o, j] <= x[o,j] for every o and j
        constraints_set_2 = []
        for j in range(0, len(demand)):
            curr_constraint = [(-1, demand[o, j]), (0, j, 1)]  # contrainte d'inégalité leq
            constraints_set_2.append(curr_constraint)
        # Contraintes
        # constraints = (constraints_set_1, constraints_set_2)
        eq_constraints = (constraints_set_1,)  # comma necessary to represent tuple with single element
        ineq_constraints = (constraints_set_2,)  # comma necessary to represent tuple with single-element

        # Application de Furness pour chaque o
        initial_trips[o] = tools.furness(initial_trips_0, eq_constraints, ineq_constraints, epsilon, max_steps)

    return initial_trips


# Etape 3.2 : Trajets intermédiaires - renvoie la matrice des trajets intermédiaires
def calc_intermediate_trips(demand, initial_trips, costs, beta, epsilon, max_steps):
    # initialisation de la variable de sortie
    intermediate_trips = np.zeros((len(demand), len(demand), len(demand)))

    for o in range(0, len(demand)):  # pour chaque origine
        # Distribution initial des trajets avec le logit
        savings = tools.calculate_savings(o, costs)
        prob = tools.logit(savings, beta)
        intermediate_trips_0 = np.zeros((len(demand), len(demand)))
        for i in range(0, len(demand)):
            for j in range(0, len(demand)):
                intermediate_trips_0[i, j] = prob[i, j] * (demand[o, j] - initial_trips[o, j]) #  : attracteurs #  * demand[o, i] : emetteurs

        # Algorithme de Furness
        # Définitions des sets de contraintes dans Furness
        # Premier set de contraintes: sum(i in S) t[o, i, j] = x[o,j] - s[o, j] for all j in S
        constraints_set_1 = []
        for j in range(0, len(demand)):
            curr_constraint = [(0, max(0, demand[o, j] - initial_trips[o, j]))] # pour éviter les valeurs négatives dûes aux arrondis
            for i in range(0, len(demand)):
                curr_constraint.append((i, j, 1))
            constraints_set_1.append(curr_constraint)
        # Deuxième set de contraintes : sum(j in S) t[o, i, j] <= x[o,i] for all i in S
        constraints_set_2 = []
        for i in range(0, len(demand)):
            curr_constraint = [(-1, demand[o, i])]
            for j in range(0, len(demand)):
                curr_constraint.append((i, j, 1))
            constraints_set_2.append(curr_constraint)
        # Contraintes
        # constraints = (constraints_set_2, constraints_set_1)
        eq_constraints = (constraints_set_1,)  # comma necessary to represent tuple with single element
        ineq_constraints = (constraints_set_2,)  # comma necessary to represent tuple with single element

        # 3.2 Application de Furness pour chaque o
        intermediate_trips[o] = tools.furness(intermediate_trips_0, eq_constraints, ineq_constraints, epsilon, max_steps)

    return intermediate_trips


#  Etape 3.3 : Trajets finaux - renvoie la matrice des trajets finaux
def calc_final_trips(demand, initial_trips, intermediate_trips):
    final_trips = np.zeros((len(demand), len(demand)))
    for i in range(0, len(initial_trips)):
        for o in range(0, len(initial_trips)):
            final_trips[i, o] = demand[o, i]
            for j in range(0, len(demand)):
                final_trips[i, o] -= intermediate_trips[o, i, j]
    return final_trips
