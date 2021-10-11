import tools
import numpy as np
from numpy import ndarray

# Alternative 2 en générant toutes les tournées explicitement


def alt_2(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, epsilon, max_steps,
               output_file_name):
    # Lecture des données d'entrée
    costs = np.loadtxt(costs_file)
    productions = np.loadtxt(prod_file)
    attractions = np.loadtxt(attr_file)

    # Distribution de la demande
    demand = calc_potential_to_demand(productions, attractions, costs, beta_dem, epsilon, max_steps)

    # Conversion de la demande en trajets
    initial_trips = calc_initial_trips(demand, productions, nb_stops_by_trips, costs, beta_ini, epsilon, max_steps)
    intermediate_trips = calc_intermediate_trips(demand, initial_trips, nb_stops_by_trips, costs, beta_inter, epsilon, max_steps)
    final_trips = calc_final_trips(demand, intermediate_trips, nb_stops_by_trips)

    # ecrire dans un fichier de sortie
    np.savetxt((output_file_name + "_alt2_initial.txt"), initial_trips, fmt='%1.2f', delimiter='\t')
    sum1 = np.sum(intermediate_trips, 0)
    np.savetxt((output_file_name + "_alt2_intermediate.txt"), np.sum(sum1, 0), fmt='%1.2f', delimiter='\t')
    np.savetxt((output_file_name + "_alt2_final.txt"), final_trips, fmt='%1.2f', delimiter='\t')

# Etape 1 : Données : productions et attractions
# Utilisation de fonctions existantes

# Etape 2 : Distribution de la demande
def calc_potential_to_demand(productions, attractions, costs, beta, furness_epsilon, max_furness_steps):
    # 1. initialisation
    demand0 = np.zeros((len(productions), len(attractions)))

    # 2. Calcul des valeurs de demande à partir du logit
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
    # Deuxième set de contraintes : sum(j in S) x[i,j] = Ai
    constraints_set_2 = []
    for i in range(0, demand0_size[0]):
        curr_constraint = [(0, productions[i])]
        for j in range(0, demand0_size[1]):
            curr_constraint.append((i, j, 1))
        constraints_set_2.append(curr_constraint)

    constraints = (constraints_set_1, constraints_set_2)
    eq_constraints = (constraints_set_1, constraints_set_2)
    ineq_constraints = ()

    # 3.2 Application algorithme de Furness
    return tools.furness(demand0, eq_constraints, ineq_constraints, furness_epsilon, max_furness_steps)


# Etape 3.1 - Trajets initiaux - renvoie la matrice des trajets initiaux
def calc_initial_trips(demand, productions, nb_stops_by_trips, costs, beta, epsilon, max_steps):
    # initialisation des variables
    initial_trips: ndarray = np.ndarray((len(demand), len(demand)))

    # distribution avec logit
    prob = tools.logit(costs, beta)
    for o in range(0, len(demand)):
        initial_trips_0 = np.ndarray((1, len(demand)))
        for j in range(0, len(demand)):
            initial_trips_0[0, j] = prob[o, j] * productions[o] / nb_stops_by_trips

        # Définitions des sets de contraintes dans Furness
        # Premier set de contraintes : sum(j in S) s[o, j] = 1/nb_stops_by_trips * sum(j in S) x[o,j] for all o
        constraints_set_1 = []
        curr_constraint = [(0, 0)]
        goal_value = 0
        for j in range(0, len(demand)):
            goal_value += demand[o, j]
            curr_constraint.append((0, j, 1))
        curr_constraint[0] = (0, goal_value / nb_stops_by_trips)  # contrainte d'égalite
        constraints_set_1.append(curr_constraint)
        # Deuxième set de contraintes : s[o, j] <= x[o,j] for every o and j
        constraints_set_2 = []
        for j in range(0, len(demand)):
            curr_constraint = [(-1, demand[o, j]), (0, j, 1)]  # contrainte d'inégalité leq
            constraints_set_2.append(curr_constraint)
        # All constraints
        constraints = (constraints_set_2, constraints_set_1)
        eq_constraints = (constraints_set_1,)
        ineq_constraints = (constraints_set_2,)

        # Application de Furness pour chaque o
        initial_trips[o] = tools.furness(initial_trips_0, eq_constraints, ineq_constraints, epsilon, max_steps)

    return initial_trips


# Etape 3.2 - Trajets intermédiaires - renvoie la matrice des trajets intermédiaires
def calc_intermediate_trips(demand, initial_trips, nb_stops_by_trips, costs, beta, epsilon, max_steps):
    # nb_stops_by_trips is the number of places served during the trip by the vehicle
    # nb_stops_by_trips-1 is the number of intermediate trips realized
    # 1. initialisation de la variable de sortie
    nb_intermediate_trips = nb_stops_by_trips - 1
    intermediate_trips = np.zeros((len(demand), nb_intermediate_trips, len(demand), len(demand)))


    for o in range(0, len(demand)):  # traitement séparés pour chaque zone d'origine
        savings = tools.calculate_savings(o, costs)
        prob = tools.logit(savings, beta)
        intermediate_trips_o = np.zeros((nb_intermediate_trips, len(demand), len(demand)))

        goal_value_1 = np.zeros(len(demand))
        goal_value_2 = np.zeros(len(demand))
        for j in range(0, len(demand)):
            goal_value_1[j] = max(0, demand[o, j] - initial_trips[o, j])  # goal value of constraint set 1 : x[o, :] - s[o, :]
            goal_value_2[j] = initial_trips[o, j]  # goal value of constraint set 2 : s[o, :]

        for n in range(0, nb_intermediate_trips):  # for each stop, starts at 0 until (nb_stops_by_trips-1)-1
            intermediate_trips_o_n = np.zeros((len(demand), len(demand)))

            # definition des limites de contraintes et des valeurs selon le numéro d'arrêt
            if n == 0:  # premier trajet intermédiaire
                emit = initial_trips[o]  # s[o, :]
            else:  # tous les autres trajets intermédiaires
                emit = np.zeros(len(demand))
                goal_value_2 = np.zeros(len(demand))
                for i in range(0, len(demand)):
                    for j in range(len(demand)):
                        emit[i] += intermediate_trips[o, n-1, j, i]  # sum (j in S) t[o, n-1, j, i]
                        goal_value_2[i] += intermediate_trips[o, n - 1, j, i]  # sum (j in S) t[o, n-1, i, j]
                        goal_value_1[j] -= max(0, goal_value_1[j] - intermediate_trips[o, n-1, i, j])
                        # x[o, :] - s[o, :] - sum (i in S, m = 0:n-1) t[o, m, i, j]

            # Distribution via le logit
            for i in range(0, len(demand)):
                for j in range(0, len(demand)):
                    intermediate_trips_o_n[i, j] = prob[i, j] * emit[i]

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
            # All constraints
            # constraints = (constraints_set_1, constraints_set_2)
            eq_constraints = (constraints_set_2, )
            ineq_constraints = (constraints_set_1, )

            # Application de Furness pour chaque o et chaque n
            intermediate_trips_o_n_fin = tools.furness(intermediate_trips_o_n, eq_constraints, ineq_constraints, epsilon, max_steps)
            intermediate_trips_o[n] = intermediate_trips_o_n_fin

        intermediate_trips[o] = intermediate_trips_o

    return intermediate_trips


# Etape 3.3 - Trajets finaux
def calc_final_trips(demand, intermediate_trips, nb_stops_by_trips):
    nb_intermediate_trips = (nb_stops_by_trips - 1)
    final_trips = np.zeros((len(demand), len(demand)))
    for o in range(0, len(demand)):
        for i in range(0, len(demand)):
            final_trips[i, o] = 0
            for j in range(0, len(demand)):
                final_trips[i, o] += intermediate_trips[o, nb_intermediate_trips-1, j, i]

    return final_trips
