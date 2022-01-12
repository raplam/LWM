import math
import numpy as np
import datetime

EPSILON_CSTR: float = 0.001

# Calcul du terme de potentiel lié à la distance
def logit(costs, beta):
    p: np.ndarray = np.zeros((len(costs), len(costs)))
    for i in range(0, len(costs)):
        for j in range(0, len(costs)):
            p[i, j] = math.exp(-beta * costs[i][j])
    return p

def logit_LAR(costs, beta):
    p = np.exp(-beta*costs)
    return p

# Calcul des savings à partir des coûts
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

def calculate_savings_LAR(index, costs):
    N=np.shape(costs)[0]
    savings=np.matlib.repmat(costs[:,index],N,1).T+np.matlib.repmat(costs[index,:],N,1)-costs
    return savings

def Furness_LAR(matrix,cons_sum_rows,cons_sum_cols, cons_sum_rows_ineq:bool,cons_sum_cols_ineq:bool, EpsilonCriterion, max_steps:int):
  # matrix: matrix to be balanced
  # cons_sum_rows : vector of constraints for the sum of rows
  # cons_sum_cols : vector of constraints for the sum of columns
  # cons_sum_cols_ineq : equal true if the constraints on the sums of columns are inequalities (false if they are equalities)
  # cons_sum_rows_ineq : equal true if the constraints on the sums of rows are inequalities (false if they are equalities)
  # EpsilonCriterion: required precision (stopping criterion)
  # max_steps: maximum number of steps (stopping criterion)
  cons_sum_rows=np.atleast_1d(np.squeeze(cons_sum_rows))# to ensure that the constraints are always 1-dimensional arrays
  cons_sum_cols=np.atleast_1d(np.squeeze(cons_sum_cols))
  matrix=np.atleast_2d(matrix)

  if np.sum(cons_sum_rows)*np.sum(cons_sum_cols) > 0:
    if np.sum(matrix)==0:
      print("the initial matrix contains only zeros, but not the constraints")
    else:
      StepNb=0
      SumRows=np.sum(matrix,0)
      SumCols=np.sum(matrix,1)
      Nr=np.shape(matrix)[0]
      Nc=np.shape(matrix)[1]
      epsilon=EpsilonCriterion+1 # simply to ensure that we enter the loop.
    while StepNb <= max_steps and epsilon >   EpsilonCriterion:
      epsilon=0
      StepNb += 1
      if not cons_sum_rows_ineq: #equality constraints first
        alpha=np.divide(cons_sum_rows,SumRows, out=np.ones_like(cons_sum_rows),where=SumRows!=0)
        matrix=np.multiply(matrix,np.matlib.repmat(alpha,Nr,1))
        epsilon=max([epsilon,max(abs(alpha-np.ones_like(alpha)))])
        SumRows=np.sum(matrix,0)
        SumCols=np.sum(matrix,1)
      if not cons_sum_cols_ineq: #equality constraint first
        alpha=np.divide(cons_sum_cols,SumCols, out=np.ones_like(cons_sum_cols),where=SumCols!=0)
        matrix=np.multiply(matrix,np.matlib.repmat(alpha,Nc,1).T)
        epsilon=max([epsilon,max(abs(alpha-np.ones_like(alpha)))])
        SumRows=np.sum(matrix,0)
        SumCols=np.sum(matrix,1)
      if cons_sum_rows_ineq: # inequality constraints
        alpha=np.divide(cons_sum_rows,SumRows, out=np.ones_like(cons_sum_rows),where=SumRows!=0)
        alpha=np.minimum(np.ones_like(alpha),alpha)
        matrix=np.multiply(matrix,np.matlib.repmat(alpha,Nr,1))
        epsilon=max([epsilon,max(abs(alpha-np.ones_like(alpha)))])
        SumRows=np.sum(matrix,0)
        SumCols=np.sum(matrix,1)
      if cons_sum_cols_ineq: # inequality constraints
        alpha=np.divide(cons_sum_cols,SumCols, out=np.ones_like(cons_sum_cols),where=SumCols!=0)
        alpha=np.minimum(np.ones_like(alpha),alpha)
        matrix=np.multiply(matrix,np.matlib.repmat(alpha,Nc,1).T)
        epsilon=max([epsilon,max(abs(alpha-np.ones_like(alpha)))])
        SumRows=np.sum(matrix,0)
        SumCols=np.sum(matrix,1)
  else:
    matrix=np.zeros_like(matrix)
  return matrix
# Algorithme de Furness utilisant des matrices pleines
def furness(variables, eqcons_sets, ineqcons_sets, epsilon, max_steps: int):
    # COPIE DES VARIABLES PRINCIPALES (pas forcément nécessaire)
    mod_variables = np.copy(variables)

    # INITIALISATIONS DES TESTS D'ARRÊT
    keep_going = 1
    steps_counter: int = 1  # compteur d'étapes

    #  ALGORITHME DE FURNESS
    while steps_counter < max_steps and keep_going:
        keep_going = 0  # désactiver la boucle

        # ITERATION SUR LES CONTRAINTES D'EGALITE DANS LE SET DES CONTRAINTES D'EGALITE
        for i_set in range(0, len(eqcons_sets)):
            for i_cons in range(0, len(eqcons_sets[i_set])):
                # goal_value : valeur objectif de la contrainte d'égalité correspondante
                goal_value = eqcons_sets[i_set][i_cons][0][1]

                # CALCUL DE LA VALEUR DE LA CONTRAINTE
                line_sum = 0
                for i_sc in range(1, len(eqcons_sets[i_set][i_cons])):
                    i = eqcons_sets[i_set][i_cons][i_sc][0]  # numéro de ligne dans la matrice des variables
                    j = eqcons_sets[i_set][i_cons][i_sc][1]  # numéro de colonne dans la matrice des variables
                    scal = eqcons_sets[i_set][i_cons][i_sc][2]  # coefficient associé à la variable dans la contrainte
                    line_sum += scal * mod_variables[i, j]  # calcul incrémental de la valeur de la contrainte

                # CALCUL DE LA NORMALISATION ET APPLICATION AUX VARIABLES
                if line_sum != 0:  # si line_sum = 0, toutes les variables sont déjà fixées à 0
                    new_normalization = goal_value / line_sum  # nouvelle normalisation
                    if abs((new_normalization - 1)) > epsilon:
                        keep_going = 1  # réactiver la boucle
                        # MISE A JOUR DES VARIABLES SELON LA NORMALISATION
                        for i_sc in range(1, len(eqcons_sets[i_set][i_cons])):
                            i = eqcons_sets[i_set][i_cons][i_sc][0]  # numéro de ligne dans la matrice des variables
                            j = eqcons_sets[i_set][i_cons][i_sc][1]  # numéro de colonne dans la matrice des variables
                            mod_variables[i, j] = mod_variables[i, j] * new_normalization  # mise à jour de la variable

        # ITERATION SUR LES CONTRAINTES D'INEGALITE DANS LE SET DES CONTRAINTES D'INEGALITE
        for i_set in range(0, len(ineqcons_sets)):
            for i_cons in range(0, len(ineqcons_sets[i_set])):
                # goal_value : valeur objectif de la contrainte d'égalité correspondante
                goal_value = ineqcons_sets[i_set][i_cons][0][1]
                # constraint_type
                # -1 si la contrainte est de type geq
                # 1 si la contrainte est de type leq
                constraint_type = ineqcons_sets[i_set][i_cons][0][0]

                # CALCUL DE LA VALEUR DE LA CONTRAINTE
                line_sum = 0
                for i_sc in range(1, len(ineqcons_sets[i_set][i_cons])):
                    i = ineqcons_sets[i_set][i_cons][i_sc][0]  # numéro de ligne dans la matrice des variables
                    j = ineqcons_sets[i_set][i_cons][i_sc][1]  # numéro de colonne dans la matrice des variables
                    scal = ineqcons_sets[i_set][i_cons][i_sc][2]  # coefficient associé à la variable dans la contrainte
                    line_sum += scal * mod_variables[i, j]  # calcul incrémental de la valeur de la contrainte

                # CALCUL DE LA NORMALISATION ET APPLICATION AUX VARIABLES
                if line_sum != 0:  # si line_sum = 0, toutes les variables sont déjà fixées à 0
                    new_normalization = goal_value / line_sum  # nouvelle normalisation
                    # si la nouvelle normalisation engendre la violation de la contrainte, elle est limitée à 1.
                    # contrainte de type leq et normalisation > 1
                    if new_normalization > 1 and constraint_type == -1:
                        new_normalization = 1
                    # contrainte de type geq et normalisation < 1
                    if new_normalization < 1 and constraint_type == 1:
                        new_normalization = 1

                    # REACTIVATION DE LA BOUCLE SI LA NORMALISATION MODIFIE NOTABLEMENT LES VARIABLES
                    if abs((new_normalization - 1)) > epsilon:
                        keep_going = 1
                        # MISE A JOUR DES VARIABLES SELON LA NORMALISATION
                        for i_sc in range(1, len(ineqcons_sets[i_set][i_cons])):
                            i = ineqcons_sets[i_set][i_cons][i_sc][0]  # numéro de ligne dans la matrice des variables
                            j = ineqcons_sets[i_set][i_cons][i_sc][1]  # numéro de colonne dans la matrice des variables
                            mod_variables[i, j] = mod_variables[i, j] * new_normalization

        steps_counter += 1

    # pour afficher les cas dans lesquels furness n'a pas convergé
    if steps_counter >= max_steps:
        f = open('output_furness_it.txt', 'a')
        f.write(str(datetime.datetime.now()) +
                "Number of furness iterations :" + str(max_steps) + " steps have been exceeded \r")
        f.close()

    return mod_variables


# Fonction qui permet de retirer les petites valeurs dans les inputs afin de diminuer la taille du problème
# lors du codage avec des matrices creuses
# La valeur de la tolérance correspond au pourcentage de demande qu'on souhaite au moins conserver
# # (par exemple 95 ou 99%)
def cut_values(values, tolerance):
    # look for the limit value based on tolerance
    mat_values = values.flatten('C')
    sort_values = -np.sort(-mat_values)
    counted_demand: float = 0
    total_demand = np.sum(np.sum(values, 0), 0)
    counter = 0
    while counted_demand < tolerance*total_demand:
        counted_demand += sort_values(counter)
        counter += 1
    ref_value = 0
    for i in range(0, counter):
        if sort_values(counter-1-i) != sort_values(counter-1-(i-1)):
            ref_value = sort_values(counter-1-i)
            break

    # modify values in the matrix as to reflect the changes
    output_values = mat_values
    sparse_output = {}
    nb_null_values = 0
    if ref_value != 0:
        for i in range(0, mat_values):
            for j in range(0, mat_values):
                if output_values[i, j] < ref_value:
                    output_values[i, j] = 0
                    nb_null_values += 1
                else:
                    if not (i in sparse_output):
                        sparse_output[i] = {}
                    sparse_output[i][j] = output_values[i, j]

    print("% of null values: " + str(nb_null_values / len(mat_values)**2))
    return sparse_output, output_values


# Fonction de vérification des contraintes (non utilisée)
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


# Anciennes fonctions
"""
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

# ne pas utiliser
def furness_old1(variables, eqcons_sets, ineqcons_sets, epsilon, max_steps: int):
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

# ne pas utiliser 
def furness_mre(variables, eqcons_sets, ineqcons_sets, epsilon, max_steps: int):
    # variables principales
    mod_variables = np.copy(variables)
    mat_size = (len(mod_variables[0]), len(mod_variables[0]))
    fixed_variables = np.zeros(mat_size)  # 1 if the variables are to be fixed during the next eq constraints step

    # initialisations tests d'arrêts
    keep_going = 1
    steps_counter: int = 1  # compteur d'étapes

    # normalisations pour les contraintes d'égalité / test d'arrêt ?
    nb_of_eqcons = 0
    for i_set in range(0, len(eqcons_sets)):
        nb_of_eqcons += len(eqcons_sets[i_set])
    eq_normalizations = np.zeros((nb_of_eqcons, 1))  # normalisations pour respect des contraintes
    nb_of_ineqcons = 0
    for i_set in range(0, len(ineqcons_sets)):
        nb_of_ineqcons += len(ineqcons_sets[i_set])
    ineq_normalizations = np.zeros((nb_of_ineqcons, 1))  # normalisations pour respect des contraintes

    #  algorithme de furness
    while steps_counter < max_steps and keep_going:
        keep_going = 0

        # itération sur les sets de contraintes d'égalité
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
                else:
                    curr_normalization = 1
                    if abs(curr_normalization-1) > epsilon:
                        keep_going = 1
                eq_normalizations[normalization_counter] = curr_normalization
                normalization_counter += 1

        fixed_variables = np.zeros(mat_size)
        normalization_counter = 0
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

    if steps_counter >= max_steps:
        print("Number of furness iterations has been exceeded")

    return mod_variables
    # return mod_variables, (steps_counter > max_steps)


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