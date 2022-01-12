import datetime
import math
import os
import numpy as np
from numpy import ndarray
import time

import tools
from analysis import LWM_analysis


# alt 3

#  Fonction utilisée pour faire des runs à partir d'un dossier contenant les inputs de production, attraction et coûts
#  Les inputs portent le même nom que le dossier en y accolant un suffixe selon le type d'input
#  productions (productions) : liste des valeurs de production de chaque zone sous forme de colonne
#  attractions (attractions) : liste des valeurs d'attraction de chaque zone sous forme de colonne
#  coûts (costs) : matrice des coûts pour laquelle les stations sont ordonnées dans les lignes et les colonnes
#                  comme dans les fichiers de productions et d'attractions
def alt3_folder(input_folder, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, beta_final, epsilon, max_steps):
    prod_file = input_folder + "/" + input_folder[input_folder.rfind("/")+1:] + "-productions.txt"
    attr_file = input_folder + "/" + input_folder[input_folder.rfind("/")+1:] + "-attractions.txt"
    costs_file = input_folder + "/" + input_folder[input_folder.rfind("/")+1:] + "-distances.txt"
    print(costs_file)
    # Chemin du dossier d'output des résultats
    output_folder = os.getcwd() + "/output/" + input_folder[input_folder.rfind("/")+1:]
    if not os.path.exists(output_folder): # Création du dossier d'output si non existant
        os.mkdir(output_folder)
    # Chemin et nom du fichier d'output des résultats
    output_file_name = output_folder + "/" + output_folder[output_folder.rfind("/")+1:] + \
                       "_alt3_nb" + str(nb_stops_by_trips) + "_bd" + \
                       str(beta_dem) + "_bi" + str(beta_ini) + "_bint" + str(beta_inter) + "_bf" + str(beta_final) + \
                       "_e" + str(math.log10(epsilon)) + "_ms" + str(max_steps)
    # Exécution du modèle selon les inputs désirés
    alt_3(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, beta_final, epsilon, max_steps,
          output_file_name)


def alt_3(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, beta_final, epsilon, max_steps,
               output_file_name):
    # Lecture des données d'entrée
    costs = np.loadtxt(costs_file)
    productions = np.loadtxt(prod_file)
    attractions = np.loadtxt(attr_file)

    # Distribution de la demande
    demand = calc_potential_to_demand(productions, attractions, costs, beta_dem, epsilon, max_steps)

    # Conversion de la demande en trajets
    start_time = time.time()
    initial_trips = calc_initial_trips(productions, attractions, demand, nb_stops_by_trips, costs, beta_ini, epsilon, max_steps)
    intermediate_trips = calc_intermediate_trips(attractions, initial_trips, nb_stops_by_trips, costs, beta_inter, epsilon, max_steps)
    final_trips = calc_final_trips(productions, attractions, initial_trips, intermediate_trips, nb_stops_by_trips, costs, beta_final, epsilon, max_steps)
    end_time = time.time()

    # Output
    np.savetxt((output_file_name + "-demand.txt"), demand, fmt='%1.6f', delimiter='\t')
    np.savetxt((output_file_name + "-initial.txt"), initial_trips, fmt='%1.6f', delimiter='\t')
    np.savetxt((output_file_name + "-intermediate.txt"), np.sum(intermediate_trips, 0), fmt='%1.6f', delimiter='\t')
    np.savetxt((output_file_name + "-final.txt"), final_trips, fmt='%1.6f', delimiter='\t')

    post_process = LWM_analysis.post_processing(demand, nb_stops_by_trips, initial_trips, np.sum(intermediate_trips, 0), final_trips, costs)
    LWM_analysis.save_output(post_process, end_time - start_time, output_file_name)

# Etape 1 : données
# Utilisation de fonctions existantes


# Etape 2 : Distribution de la demande (non utilisée par la suite)
def calc_potential_to_demand(productions, attractions, costs, beta, furness_epsilon, max_furness_steps):
    print("alt3_demand :" + str(datetime.datetime.now()))
    ### Initialisation de la variable de sortie
    demand0 = np.zeros((len(productions), len(attractions)))

    prob = tools.logit(costs, beta)
    for i in range(0, np.size(productions)):
        for j in range(0, np.size(attractions)):
            demand0[i, j] = prob[i, j] * productions[i]  # normalization does not matter because 2 equality constraints

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

    #  Définition des sets de contraintes d'inégalité et d'égalité
    eq_constraints = (constraints_set_1, constraints_set_2) #  Deux sets de contrainte d'égalité
    ineq_constraints = ()  # Pas de contraintes d'inégalité

    # Exécution de l'algorithme de Furness
    demand = tools.furness(demand0, eq_constraints, ineq_constraints, furness_epsilon, max_furness_steps)

    return demand


# Trajets initiaux - renvoie la matrice des trajets initiaux
def calc_initial_trips(productions, attractions, demand, nb_stops_by_trips, costs, beta, epsilon, max_steps):
    print("alt3_initial :" + str(datetime.datetime.now()))
    ## Initialisation de la variable de sortie
    initial_trips: ndarray = np.ndarray((len(productions), len(attractions)))

    ## Distribution initiale des trajets
    prob = tools.logit(costs, beta)
    initial_trips_0 = np.zeros((len(productions), len(attractions)))
    for o in range(0, len(demand)):
        if productions[o] == 0:  # pas de productions, pas de trajets
            continue
        for j in range(0, len(demand)):
            initial_trips_0[o, j] = prob[o, j] * attractions[j]
            # normalization by emission -> productions[o] / nb_stops_by_trips -> not fine
            # normalization by attraction -> initial demand : demand[o, j]

    ## Algorithme de Furness
    # Définitions des sets de contraintes dans Furness
    # DEFINITION D'UNE CONTRAINTE
    # Chaque contrainte est une liste de tuple définie à partir de la notation suivante pour la contrainte,
    # dans laquelle l'ensemble des variables sont dans le membre de gauche et le reste à droite, i.e. :
    # "expression avec les variables < ou = ou > valeur de la contrainte"
    # 1er tuple de la contrainte : (type de contrainte, valeur de la contrainte)
    # Les tuples suivants sont sur le format : (coefficient associé à la variable considérée, ligne, colonne)
    # où ligne et colonne correspondent aux coordonnées de la variable considérée dans la matrice des variables
    # DEFINITION D'UN SET DE CONTRAINTE
    # Il s'agit d'une liste de contraintes, telle que définies auparavant

    # Premier set de contraintes : sum(j in S) s[o, j] = 1/nb_stops_by_trips * sum(j in S) x[o,j]
    constraints_set_1 = []  # Initialisation du set de contraintes
    for o in range(0, len(demand)):
        if productions[o] == 0:  # pas de productions, pas de trajets initiaux
            continue
        curr_constraint = [(0, productions[o]/nb_stops_by_trips)]
        for j in range(0, len(demand)):
            curr_constraint.append((o, j, 1))
        constraints_set_1.append(curr_constraint)  # Ajout de la contrainte au set

    # Deuxième set de contraintes : pour chaque j, sum (o in S), s[o, j] <= A[j]
    constraints_set_2 = []  # Initialisation du set de contraintes
    for j in range(0, len(demand)):
        for o in range(0, len(demand)):
            if productions[o] == 0:  # pas de productions, pas de trajets initiaux
                continue
            curr_constraint = [(-1, attractions[j]), (o, j, 1)]  # Définition de la contrainte d'inégalité leq
        constraints_set_2.append(curr_constraint)  # Ajout de la contrainte au set

    #  Définition des sets de contraintes d'égalité et d'inégalité
    eq_constraints = (constraints_set_1,)  # virgule nécessaire pour un représenter un tuple à un seul élément
    ineq_constraints = (constraints_set_2,)  # virgule nécessaire pour un représenter un tuple à un seul élément

    # Application de Furness à partir des variables, sets de contraintes et paramètres définis
    initial_trips = tools.furness(initial_trips_0, eq_constraints, ineq_constraints, epsilon, max_steps)

    return initial_trips


# Trajets intermédiaires - renvoie la matrice des trajets intermédiaires
def calc_intermediate_trips(attractions, initial_trips, nb_stops_by_trips, costs, beta, epsilon, max_steps):
    print("alt3_intermediate :" + str(datetime.datetime.now()))
    ## Définition de paramètres accessoires
    # nb_stops_by_trips : nombre de points d'arrêt durant la tournée
    # nb_intermediate_trips = nb_stops_by_trips-1 : nombre de trajets intermédiaires
    nb_intermediate_trips = nb_stops_by_trips - 1

    ## Initialisation de la variable de sortie
    intermediate_trips = np.zeros((nb_stops_by_trips - 1, len(attractions), len(attractions)))

    ## Calculs préliminaires pour la définition des valeurs de contraintes
    ## et des potentiels dans les distributions initiales
    # Définition des valeurs de contraintes et de potentiels de distribution
    # emit - flux de trajets intermédiaires de rang n à émettre pour la zone o avec
    # receive - flux de trajets à recevoir avec des trajets intermédiaires de rang au moins n
    goal_value_1 = np.zeros(len(attractions))
    receive = attractions
    for n in range(0, nb_intermediate_trips):  # rang de trajet intermédiaire
        goal_value_2 = np.zeros(len(attractions))
        # emit = np.zeros(len(attractions))

        if n == 0:
            for i in range(0, len(attractions)):
                goal_value_1[i] = attractions[i]
                for o in range(0, len(attractions)):
                    # emit[i] += initial_trips[o, i]
                    receive[i] -= initial_trips[o, i]  # commenter si option 1
                    goal_value_2[i] += initial_trips[o, i]
                    goal_value_1[i] -= initial_trips[o, i]
                receive[i] = max(0, receive[i])
                goal_value_1[i] = max(0, goal_value_1[i])
        else:
            for i in range(0, len(attractions)):
                for j in range(0, len(attractions)):
                    receive[i] -= intermediate_trips[n-1, j, i]  # commenter si option 1
                    # emit[i] += intermediate_trips[n-1, j, i]
                    goal_value_2[i] += intermediate_trips[n-1, j, i]
                    goal_value_1[i] -= intermediate_trips[n-1, j, i]
                goal_value_1[i] = max(0, goal_value_1[i])
                receive[i] = max(0, receive[i])

        ## Distribution initiale via le logit
        prob = tools.logit(costs, beta)  # calcul de la distribution initiale à l'aide du logit
        intermediate_trips_n = np.zeros((len(attractions), len(attractions)))  # variable intermédiaire
        for i in range(0, len(attractions)):
            for j in range(0, len(attractions)):
                # intermediate_trips_n[i, j] = prob[i, j] * emit[i]
                intermediate_trips_n[i, j] = prob[i, j] * receive[j]

        ## Algorithme de Furness
        # Définition des sets de contraintes
        # Premier set de contraintes :
        # sum(i in S) t[n, i, j] <= A[j] - sum (i in S) s[i, j] - sum (i in S, m in 0..n-1) t[m, i, j] pour tout j
        constraints_set_1 = []
        for j in range(0, len(attractions)):
            if n < nb_intermediate_trips - 1:
                curr_constraint = [(-1, max(0, goal_value_1[j]))]
            else:
                curr_constraint = [(0, max(0, goal_value_1[j]))]
            for i in range(0, len(attractions)):
                curr_constraint.append((i, j, 1))
            constraints_set_1.append(curr_constraint)

        # Deuxième set de contraintes :
        # sum(j in S) t[n, i, j] = sum (j in S) t[n-1, j, i] pour tout i
        constraints_set_2 = []
        for i in range(0, len(attractions)):
            curr_constraint = [(0, max(0, goal_value_2[i]))]
            for j in range(0, len(attractions)):
                curr_constraint.append((i, j, 1))
            constraints_set_2.append(curr_constraint)

        #  Définition des sets de contraintes d'égalité et d'inégalité
        if n < nb_intermediate_trips - 1:
            eq_constraints = (constraints_set_2,)  # comma necessary to represent tuple with single element
            ineq_constraints = (constraints_set_1,)  # comma necessary to represent tuple with single element
        else:
            eq_constraints = (constraints_set_2, constraints_set_1)  # comma necessary to represent tuple with single element
            ineq_constraints = ()  # comma necessary to represent tuple with single element

        # Application de Furness à partir des variables, sets de contraintes et paramètres définis
        intermediate_trips[n] = tools.furness(intermediate_trips_n, eq_constraints, ineq_constraints,
                                              epsilon, max_steps)
        print(str(n) + " " + str(datetime.datetime.now()))
    return intermediate_trips


#  Trajets finaux - renvoie la matrice des trajets finaux
def calc_final_trips(productions, attractions, initial_trips, intermediate_trips,
                     nb_stops_by_trips, costs, beta, epsilon, max_steps):
    print("alt3_final :" + str(datetime.datetime.now()))

    # Initialisation de la variable
    final_trips_0 = np.zeros((len(attractions), len(attractions)))
    # Distribution initiale des trajets
    prob = tools.logit(costs, beta)
    # final_trips_0 = prob

    for i in range(0, len(productions)):
        for j in range(0, len(attractions)):
            final_trips_0[i, j] = prob[i, j] * productions[j] / nb_stops_by_trips
    # for i in range(0, len(attractions)):
    #    value = attractions[i]
    #    for j in range(0, len(attractions)):
    #        for n in range(0, nb_stops_by_trips-1):
    #            value -= intermediate_trips[n, i, j]
    #    for j in range(0, len(attractions)):
    #        final_trips_0[i, j] = prob[i, j] * max(value, 0)  # utilisation max si valeurs négatives


    ## Algorithme de Furness
    #Définition des contraintes
    # Les contraintes ne se correspondent peut-être pas avec les pertes ; on va les redresser vis-à-vis des plus faibles
    # selon la manière dont on somme, on n'a plus tout à fait la même chose avec toutes les étapes de calculs intermédiaires
    # on ne pourra pas converger avec furness et on dépassera automatiquement les valeurs considérées
    tot1 = np.sum(np.sum(intermediate_trips[nb_stops_by_trips-2], 0), 0)
    tot2 = np.sum(np.sum(initial_trips, 0), 0)
    # Définitions des sets de contraintes dans Furness
    # Premier set de contraintes : sum (j in S) r[i, j] = sum (j in S) t[n-1, j, i] pour tout i
    constraints_set_1 = []
    for i in range(0, len(attractions)):
        goal_value = 0
        curr_constraint = [(0, 0)]
        for j in range(0, len(attractions)):
            curr_constraint.append((i, j, 1))
            # tot2 / tot1 - renormalisation de la matrice des derniers trajets intermédiaires
            goal_value += intermediate_trips[nb_stops_by_trips-2, j, i] #*tot2/tot1
        curr_constraint[0] = (0, goal_value)
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