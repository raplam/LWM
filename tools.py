import math
import numpy as np
from numpy import ndarray

EPSILON_CSTR: float = 0.001

def logit_zero(costs, beta):
    total = 0
    p: ndarray = np.zeros((len(costs), len(costs)))
    for i in range(0, len(costs)):
        for j in range(0, len(costs)):
            p[i, j] = math.exp(-beta * costs[i][j])
    return p
"""
def logit(costs, beta):
    total = 0
    p: ndarray = np.zeros((len(costs), len(costs)))
    for i in range(0, len(costs)):
        total = 0
        # calcul du dénominateur
        for j in range(0, len(costs)):
            total += math.exp(-beta * costs[i][j])
        # calcul du dénominateur
        for j in range(0, len(costs)):
            p[i, j] = math.exp(-beta * costs[i][j]) # / total
    return p


def logit(costs, beta):
    total = 0
    p: ndarray = np.zeros((len(costs), len(costs)))
    for j in range(0, len(costs)):
        total = 0
        # calcul du dénominateur
        for i in range(0, len(costs)):
            total += math.exp(-beta * costs[i][j])
        # calcul du dénominateur
        for i in range(0, len(costs)):
            p[i, j] = math.exp(-beta * costs[i][j]) / total
    return p
"""

# algorithme de Furness avec Tuple structure for constraints - reworked
def furness_old(variables, constraints_sets, epsilon, max_steps: int):
    # variables principales
    mod_variables = np.copy(variables)

    # initialisations tests d'arrêts
    nb_of_constraints = 0
    for i_set in range(0, len(constraints_sets)):
        nb_of_constraints += len(constraints_sets[i_set])
    normalizations = np.zeros((nb_of_constraints, 1))  # normalisations pour respect des contraintes
    epsilon_test = float('inf')  # vérification des tolérances
    steps_counter: int = 1  # compteur d'étapes

    #  algorithme de furness
    while steps_counter < max_steps and epsilon_test > epsilon:
        # itération sur les sets de contraintes
        normalization_counter = 0
        epsilon_test = 0
        for i_set in range(0, len(constraints_sets)):

            # itération sur les contraintes
            for i_cons in range(0, len(constraints_sets[i_set])):
                constraint_type = constraints_sets[i_set][i_cons][0][0]
                goal_value = constraints_sets[i_set][i_cons][0][1]

                # Calcul de la contrainte
                line_sum = 0
                for i_sc in range(1, len(constraints_sets[i_set][i_cons])):
                    i = constraints_sets[i_set][i_cons][i_sc][0]  # row number
                    j = constraints_sets[i_set][i_cons][i_sc][1]  # col number
                    scal = constraints_sets[i_set][i_cons][i_sc][2]  # scalar
                    line_sum += scal * mod_variables[i, j]

                # Vérification de la normalisation
                normalize = 0
                if constraint_type == -1 and line_sum > goal_value:  # inequality leq
                    normalize = 1
                elif constraint_type == 1 and line_sum < goal_value:  # inequality geq
                    normalize = 1
                elif constraint_type == 0:  # equality
                    normalize = 1
                if normalize and line_sum != 0:  # if line_sum = 0, toutes ces variables ont été fixées à 0 plus tôt
                    curr_normalization = goal_value / line_sum
                    for i_sc in range(1, len(constraints_sets[i_set][i_cons])):
                        i = constraints_sets[i_set][i_cons][i_sc][0]  # row number
                        j = constraints_sets[i_set][i_cons][i_sc][1]  # col number
                        mod_variables[i, j] = mod_variables[i, j] * curr_normalization
                        if goal_value != 0:
                            epsilon_test = max(epsilon_test, abs((curr_normalization - normalizations[
                                normalization_counter]) / curr_normalization))
                else:  # si les inégalités sont respectées, la normalisation vaut 1
                    curr_normalization = 1
                normalizations[normalization_counter] = curr_normalization
                normalization_counter += 1

        # plusieurs solutions existent lorsqu'il y a des inégalités :
        # compteur d'étapes
        steps_counter += 1

    return mod_variables


# Deernière version de l'algorithme de Furness
def furness(variables, eqcons_sets, ineqcons_sets, epsilon, max_steps: int):
    # variables principales
    mod_variables = np.copy(variables)
    mat_size = (len(mod_variables[0]), len(mod_variables[0]))
    fixed_variables = np.zeros(mat_size) # 1 if the variables are to be fixed during the next eq constraints step

    # initialisations tests d'arrêts
    epsilon_test = float('inf')  # vérification des tolérances
    steps_counter: int = 1  # compteur d'étapes

    # normalisations pour les contraintes d'égalité / test d'arrêt ?
    nb_of_eqcons = 0
    for i_set in range(0, len(eqcons_sets)):
        nb_of_eqcons += len(eqcons_sets[i_set])
    normalizations = np.zeros((nb_of_eqcons, 1))  # normalisations pour respect des contraintes

    #  algorithme de furness
    while steps_counter < max_steps and epsilon_test > epsilon:
        # itération sur les sets de contraintes
        epsilon_test = 0
        normalization_counter = 0

        for i_set in range(0, len(eqcons_sets)):
            # itération sur les contraintes d'égalité
            for i_cons in range(0, len(eqcons_sets[i_set])):
                goal_value = eqcons_sets[i_set][i_cons][0][1]

                # Calcul de la contrainte
                line_sum = 0
                for i_sc in range(1, len(eqcons_sets[i_set][i_cons])):
                    i = eqcons_sets[i_set][i_cons][i_sc][0]  # row number
                    j = eqcons_sets[i_set][i_cons][i_sc][1]  # col number
                    scal = eqcons_sets[i_set][i_cons][i_sc][2]  # scalar
                    if fixed_variables[i, j] == 0:  # if the current variable is not fixed
                        line_sum += scal * mod_variables[i, j]
                    else:  # if the current variable is fixed
                        goal_value -= scal * mod_variables[i, j]

                # Normalisation
                if line_sum != 0:  # if line_sum = 0, all variables were already fixed to 0
                    curr_normalization = goal_value / line_sum
                    for i_sc in range(1, len(eqcons_sets[i_set][i_cons])):
                        i = eqcons_sets[i_set][i_cons][i_sc][0]  # row number
                        j = eqcons_sets[i_set][i_cons][i_sc][1]  # col number
                        if fixed_variables[i, j] == 0:  # if the variable is not fixed, normalize
                            mod_variables[i, j] = mod_variables[i, j] * curr_normalization
                        if goal_value != 0:
                            epsilon_test = max(epsilon_test, abs((curr_normalization - normalizations[
                                normalization_counter]) / curr_normalization))
                else:
                    curr_normalization = 1
                normalizations[normalization_counter] = curr_normalization
                normalization_counter += 1

        # Reset fixed variables : should such variables be definitely fixed ? No
        fixed_variables = np.zeros(mat_size)
        for i_set in range(0, len(ineqcons_sets)):
            # itération sur les contraintes d'inégalité
            for i_cons in range(0, len(ineqcons_sets[i_set])):
                constraint_type = ineqcons_sets[i_set][i_cons][0][0]
                goal_value = ineqcons_sets[i_set][i_cons][0][1]
                line_sum = 0

                for i_sc in range(1, len(ineqcons_sets[i_set][i_cons])):
                    i = ineqcons_sets[i_set][i_cons][i_sc][0]  # row number
                    j = ineqcons_sets[i_set][i_cons][i_sc][1]  # col number
                    scal = ineqcons_sets[i_set][i_cons][i_sc][2]  # scalar
                    # Calcul de la contrainte
                    line_sum += scal * mod_variables[i, j]

                    # Vérification de la contrainte d'inégalité
                if line_sum != 0:  # if line_sum = 0, all variables were set to 0 earlier
                    if (line_sum > goal_value and constraint_type == -1) \
                            or (line_sum < goal_value and constraint_type == 1):
                        #  Si la normalisation n'est pas bonne, on l'applique sur toutes les variables équitablement
                        #  On bloque davantage de variables qu'en en fixant une seule à sa valeur max
                        # on préserve la relation existante entre ces variables (dûe à la distribution initiale)
                        curr_normalization = goal_value / line_sum
                        for i_sc in range(1, len(ineqcons_sets[i_set][i_cons])):
                            i = ineqcons_sets[i_set][i_cons][i_sc][0]  # row number
                            j = ineqcons_sets[i_set][i_cons][i_sc][1]  # col number
                            mod_variables[i, j] = mod_variables[i, j] * curr_normalization
                            fixed_variables[i, j] = 1

        # compteur d'étapes
        steps_counter += 1

    if (not constraint_check(mod_variables, eqcons_sets, ineqcons_sets, EPSILON_CSTR)) and steps_counter < max_steps:
        # it may happen that the normalization has somehow stabilized but the constraints are not respected
        # if the algorithm has converged but constraints are not respected, we go for another round
        return furness(mod_variables, eqcons_sets, ineqcons_sets, epsilon * 0.1, max_steps-steps_counter)

    return mod_variables
    # return mod_variables, (steps_counter > max_steps)


def calculate_savings(index, costs):
    savings = np.zeros((len(costs), len(costs)))
    for i in range(0, len(costs)):
        if i != index:
            for j in range(0, len(costs)):
                if j != index:
                    pendelfahrt = costs[index, i] + costs[i, index] + costs[j, index] + costs[index, j]
                    rundfahrt = costs[index, i] + costs[i, j] + costs[j, index]
                    savings[i, j] = pendelfahrt - rundfahrt

    return savings


# function used to check that the algorithm has really converged
def constraint_check(variables, eqcons_sets, ineqcons_sets, epsilon_cstr):
    for i_set in range(0, len(eqcons_sets)):
        # itération sur les contraintes d'égalité
        for i_cons in range(0, len(eqcons_sets[i_set])):
            goal_value = eqcons_sets[i_set][i_cons][0][1]

            # Calcul de la contrainte
            line_sum = 0
            for i_sc in range(1, len(eqcons_sets[i_set][i_cons])):
                i = eqcons_sets[i_set][i_cons][i_sc][0]  # row number
                j = eqcons_sets[i_set][i_cons][i_sc][1]  # col number
                scal = eqcons_sets[i_set][i_cons][i_sc][2]  # scalar
                line_sum += scal * variables[i, j]

            # Normalisation
            if abs(line_sum - goal_value) > epsilon_cstr:
                return 0

    for i_set in range(0, len(ineqcons_sets)):
        # itération sur les contraintes d'inégalité
        for i_cons in range(0, len(ineqcons_sets[i_set])):
            constraint_type = ineqcons_sets[i_set][i_cons][0][0]
            goal_value = ineqcons_sets[i_set][i_cons][0][1]
            line_sum = 0

            for i_sc in range(1, len(ineqcons_sets[i_set][i_cons])):
                i = ineqcons_sets[i_set][i_cons][i_sc][0]  # row number
                j = ineqcons_sets[i_set][i_cons][i_sc][1]  # col number
                scal = ineqcons_sets[i_set][i_cons][i_sc][2]  # scalar
                line_sum += scal * variables[i, j]

                if (line_sum - goal_value > epsilon_cstr and constraint_type == -1) \
                        or (line_sum - goal_value < epsilon_cstr and constraint_type == 1):
                    return 0

    return 1
