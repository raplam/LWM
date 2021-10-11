import tools
import numpy as np
from numpy import ndarray

# Alternative 1 en générant les trajets retours au début


def alt_1(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_ini, beta_inter, beta_final, epsilon, max_steps,
               output_file_name):
    # Lecture des données d'entrée
    costs = np.loadtxt(costs_file)
    productions = np.loadtxt(prod_file)
    attractions = np.loadtxt(attr_file)

    # Conversion de la demande en trajets
    initial_trips = calc_initial_trips(productions, attractions, nb_stops_by_trips, costs, beta_ini, epsilon, max_steps)
    final_trips = calc_final_trips(productions, attractions, nb_stops_by_trips, costs, beta_final, epsilon, max_steps)
    intermediate_trips = calc_intermediate_trips(attractions, initial_trips, final_trips, costs, beta_inter, epsilon, max_steps)

    # ecrire dans un fichier de sortie
    np.savetxt((output_file_name + "_alt1_initial.txt"), initial_trips, fmt='%1.2f', delimiter='\t')
    np.savetxt((output_file_name + "_alt1_intermediate.txt"), intermediate_trips, fmt='%1.2f', delimiter='\t')
    np.savetxt((output_file_name + "_alt1_final.txt"), final_trips, fmt='%1.2f', delimiter='\t')

# Etape 1 : Données : productions et attractions
# Utilisation de fonctions existantes


# Etape 2.1 : Trajets initiaux - renvoie la matrice des trajets initiaux et la demande mise à jour
def calc_initial_trips(productions, attractions, nb_stops_by_trips, costs, beta, epsilon, max_steps):
    # Initialisation des variables
    trips_0: ndarray = np.zeros((len(productions), len(attractions)))

    # Distribution avec logit
    prob = tools.logit(costs, beta)
    for o in range(0, len(productions)):
        for j in range(0, len(attractions)):
            trips_0[o, j] = prob[o, j] * productions[o] / nb_stops_by_trips

    # Définitions des sets de contraintes dans Furness
    # Premier set de contraintes : sum(j in S) s[o, j] = 1/nb_stops_by_trips * productions[o] for every o
    constraints_set_1 = []
    for o in range(0, len(productions)):
        curr_constraint = [(0, productions[o] / nb_stops_by_trips)]
        for j in range(0, len(attractions)):
            curr_constraint.append((o, j, 1))
        constraints_set_1.append(curr_constraint)
    # Deuxième set de contraintes : sum(o in S) s[o, j] <= Aj for every j
    constraints_set_2 = []
    for j in range(0, len(attractions)):
        curr_constraint = [(-1, attractions[j])]  # contrainte d'inégalité leq
        for o in range(0, len(productions)):
            curr_constraint.append((o, j, 1))
        constraints_set_2.append(curr_constraint)
    # Contraintes
    constraints = (constraints_set_2, constraints_set_1)
    eq_constraints = (constraints_set_1,)
    ineq_constraints = ( constraints_set_2,)

    # Algorithme de Furness
    trips = tools.furness(trips_0, eq_constraints, ineq_constraints, epsilon, max_steps)

    return trips


# Etape 2.2 : Trajets finaux - renvoie la matrice des trajets finaux
def calc_final_trips(productions, attractions, nb_stops_by_trips, costs, beta, epsilon, max_steps):
    # Initialisation des variables
    trips_0: ndarray = np.zeros((len(productions), len(attractions)))

    # Distribution avec logit
    prob = tools.logit(costs, beta)
    for o in range(0, len(productions)):
        for j in range(0, len(attractions)):
            trips_0[j, o] = prob[j, o] * productions[o] / nb_stops_by_trips

    # Définitions des sets de contraintes dans Furness
    # Premier set de contraintes : sum(j in S) r[j, o] = 1/nb_stops_by_trips * productions[o] for all o
    constraints_set_1 = []
    for o in range(0, len(productions)):
        curr_constraint = [(0, productions[o] / nb_stops_by_trips)]
        for i in range(0, len(attractions)):
            curr_constraint.append((i, o, 1))
        constraints_set_1.append(curr_constraint)
    # Deuxième set de contraintes : sum(o in S) r[i, o] <= Ai for all i
    constraints_set_2 = []
    for i in range(0, len(attractions)):
        curr_constraint = [(-1, attractions[i])]  # contrainte d'inégalité leq
        for o in range(0, len(productions)):
            curr_constraint.append((i, o, 1))
        constraints_set_2.append(curr_constraint)
    # Contraintes
    constraints = (constraints_set_2, constraints_set_1)
    eq_constraints = (constraints_set_1,)
    ineq_constraints = (constraints_set_2,)

    # Algorithme de Furness
    trips = tools.furness(trips_0, eq_constraints, ineq_constraints, epsilon, max_steps)

    return trips


# Etape 2.3 : Trajets intermédiaires - renvoie la matrice des trajets intermédiaires
def calc_intermediate_trips(attractions, initial_trips, final_trips, costs, beta, epsilon, max_steps):
    # Initialisation des variables
    intermediate_trips_0 = np.zeros((len(attractions), len(attractions)))

    # Distribution avec logit
    prob = tools.logit(costs, beta)
    for i in range(0, len(attractions)):
        value = attractions[i]
        for o in range(0, len(attractions)):
            value -= final_trips[i, o]
        for j in range(0, len(attractions)):
            intermediate_trips_0[i, j] = prob[i, j] * max(value, 0)  # max in case we get negative values instead of zero because of roundings

    # Définitions des sets de contraintes dans Furness
    # Premier set de contraintes: sum(i in S) t[i, j] = A[j] - sum(i in S) s[i, j] for all j in S
    constraints_set_1 = []
    for j in range(0, len(attractions)):
        goal_value = attractions[j]
        curr_constraint = [(0, 0)]
        for i in range(0, len(attractions)):
            curr_constraint.append((i, j, 1))
            goal_value -= initial_trips[i, j]
        curr_constraint[0] = (0, max(0, goal_value))
        constraints_set_1.append(curr_constraint)
    # Deuxième set de contraintes : sum(j in S) t[i, j] = A[i] - sum(j in S) r[i, j] for all i in S
    constraints_set_2 = []
    for i in range(0, len(attractions)):
        goal_value = attractions[i]
        curr_constraint = [(0, attractions[i])]
        for j in range(0, len(attractions)):
            curr_constraint.append((i, j, 1))
            goal_value -= final_trips[i, j]
        curr_constraint[0] = (0, max(0, goal_value))
        constraints_set_2.append(curr_constraint)
    # All constraints
    # constraints = (constraints_set_1, constraints_set_2)
    eq_constraints = (constraints_set_1, constraints_set_2)
    ineq_constraints = ()

    # Algorithme de Furness
    intermediate_trips = tools.furness(intermediate_trips_0, eq_constraints, ineq_constraints, epsilon, max_steps)

    return intermediate_trips

