import datetime
import math
import os
import numpy as np
from numpy import ndarray
import time

import tools
from analysis import LWM_analysis


# TB-Freight

#  Fonction utilisée pour faire des runs à partir d'un dossier contenant les inputs de production, attraction et coûts
#  Les inputs portent le même nom que le dossier en y accolant un suffixe selon le type d'input
#  "-productions.txt" (productions) : liste des valeurs de production de chaque zone sous forme de colonne
#  "-attractions.txt" (attractions) : liste des valeurs d'attraction de chaque zone sous forme de colonne
#  "-distances" : coûts généralisés (costs) : matrice des coûts pour laquelle les stations sont ordonnées
#                 selon les lignes comme dans les fichiers de productions et d'attractions
def tb_freight_folder(input_folder, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, epsilon, max_steps):
    prod_file = input_folder + "/" + input_folder[input_folder.rfind("/")+1:] + "-productions.txt"
    attr_file = input_folder + "/" + input_folder[input_folder.rfind("/")+1:] + "-attractions.txt"
    costs_file = input_folder + "/" + input_folder[input_folder.rfind("/")+1:] + "-distances.txt"
    # Chemin du dossier d'output des résultats
    output_folder = os.getcwd() + "/output/" + input_folder[input_folder.rfind("/")+1:]
    if not os.path.exists(output_folder):  # Création du dossier d'output si non existant
        os.mkdir(output_folder)
    # Chemin et nom du fichier d'output des résultats
    output_file_name = output_folder + "/" + output_folder[output_folder.rfind("/")+1:] + \
                       "_tbf_nb" + str(nb_stops_by_trips) + "_bd" + \
                       str(beta_dem) + "_bi" + str(beta_ini) + "_bint" + str(beta_inter) + \
                       "_e" + str(math.log10(epsilon)) + "_ms" + str(max_steps)
    # Exécution du modèle selon les inputs désirés
    tb_freight(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, epsilon, max_steps,
               output_file_name, input_folder[input_folder.rfind("/")+1:])

def tb_freight_folder_LAR(input_folder, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, epsilon, max_steps):
    prod_file = input_folder + "/" + input_folder[input_folder.rfind("/")+1:] + "-productions.txt"
    attr_file = input_folder + "/" + input_folder[input_folder.rfind("/")+1:] + "-attractions.txt"
    costs_file = input_folder + "/" + input_folder[input_folder.rfind("/")+1:] + "-distances.txt"
    # Chemin du dossier d'output des résultats
    output_folder = os.getcwd() + "/output/" + input_folder[input_folder.rfind("/")+1:] + "_LAR"
    if not os.path.exists(output_folder):  # Création du dossier d'output si non existant
        os.mkdir(output_folder)
    # Chemin et nom du fichier d'output des résultats
    output_file_name = output_folder + "/" +output_folder[output_folder.rfind("/")+1:] + \
                       "_tbf_nb" + str(nb_stops_by_trips) + "_bd" + \
                       str(beta_dem) + "_bi" + str(beta_ini) + "_bint" + str(beta_inter) + \
                       "_e" + str(math.log10(epsilon)) + "_ms" + str(max_steps)
    # Exécution du modèle selon les inputs désirés
    tb_freight_LAR(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, epsilon, max_steps, output_file_name, input_folder[input_folder.rfind("/")+1:]+"_LAR")

def tb_freight_LAR(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, epsilon, max_steps, output_file_name, folder_name):
    # Lecture des données d'entrée
    costs = np.loadtxt(costs_file)
    productions = np.loadtxt(prod_file)
    attractions = np.loadtxt(attr_file)
    
    start_time = time.time()

    N=np.shape(costs)[0]

    # Matrice initiale
    demand= np.exp(-beta_dem*costs)
    # Furness avec égalités sur les lignes et colonnes
    demand=tools.Furness_LAR(demand,attractions,productions,False,False,epsilon,max_steps)

    ## Conversion de la demande en trajets
    # initialize the matrices for initial, intermediary and final trips
    initial_trips=np.zeros((N,N))
    intermediate_trips=np.zeros((N,N))
    final_trips=np.zeros((N,N))
    for o in range(0,N-1):
      # Trajets initiaux
      print("Trajets initiaux")
      #initial_trips_from_o=np.multiply(np.exp(-beta_ini*costs[o,:]),demand[o,:])
      initial_trips_from_o=np.exp(-beta_ini*costs[o,:])
      initial_trips_from_o = tools.Furness_LAR(initial_trips_from_o, demand[o,:], np.sum(demand[o,:]) / nb_stops_by_trips, True, False, epsilon, max_steps)
      initial_trips[o,:]=initial_trips_from_o


      # Trajets intermédiaires
      print("Trajets intermédiaires")
      savings=tools.calculate_savings_LAR(o,costs)
      intermediate_trips_from_o=np.multiply(np.exp(-beta_inter*savings),np.matlib.repmat(demand[o,:],N,1).T)
      intermediate_trips_from_o=tools.Furness_LAR(intermediate_trips_from_o,demand[o,:]-initial_trips_from_o,demand[o,:], False, True, epsilon, max_steps)
      intermediate_trips = intermediate_trips + intermediate_trips_from_o

      # Trajets finaux
      print("Trajets finaux")
      final_trips[:,o] = demand[o,:]-np.sum(intermediate_trips_from_o,axis=1) #axis=1: sum over columns (axis=0 for sum over rows)  
    
    end_time = time.time()
    # Output
    np.savetxt((output_file_name + "-demand.txt"), demand, fmt='%1.6f', delimiter='\t')
    np.savetxt((output_file_name + "-initial.txt"), initial_trips, fmt='%1.6f', delimiter='\t')
    np.savetxt((output_file_name + "-intermediate.txt"), intermediate_trips, fmt='%1.6f', delimiter='\t')
    np.savetxt((output_file_name + "-final.txt"), final_trips, fmt='%1.6f', delimiter='\t')

    post_process = LWM_analysis.post_processing(demand, nb_stops_by_trips, initial_trips,intermediate_trips, final_trips, costs)
    LWM_analysis.save_output(post_process, end_time - start_time, folder_name, output_file_name)


def tb_freight(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, epsilon, max_steps,output_file_name, folder_name):
    # Lecture des données d'entrée
    costs = np.loadtxt(costs_file)
    productions = np.loadtxt(prod_file)
    attractions = np.loadtxt(attr_file)

    start_time = time.time()
    # Distribution de la demande
    demand = calc_potential_to_demand(productions, attractions, costs, beta_dem, epsilon, max_steps)
    # demand = tools.cut_values(demand, 0.99)
    # Conversion de la demande en trajets
    initial_trips = calc_initial_trips(demand, productions, nb_stops_by_trips, costs, beta_ini, epsilon, max_steps)
    intermediate_trips = calc_intermediate_trips(demand, productions, initial_trips, costs, beta_inter, epsilon, max_steps)
    final_trips = calc_final_trips(demand, productions, initial_trips, intermediate_trips)
    end_time = time.time()

    # Output
    np.savetxt((output_file_name + "-demand.txt"), demand, fmt='%1.6f', delimiter='\t')
    np.savetxt((output_file_name + "-initial.txt"), initial_trips, fmt='%1.6f', delimiter='\t')
    np.savetxt((output_file_name + "-intermediate.txt"), np.sum(intermediate_trips, 0), fmt='%1.6f', delimiter='\t')
    np.savetxt((output_file_name + "-final.txt"), final_trips, fmt='%1.6f', delimiter='\t')

    post_process = LWM_analysis.post_processing(demand, nb_stops_by_trips, initial_trips, np.sum(intermediate_trips, 0), final_trips, costs)
    LWM_analysis.save_output(post_process, end_time - start_time, folder_name, output_file_name)

# Etape 1 : données
# Utilisation de fonctions existantes


# Etape 2 : Distribution de la demande
def calc_potential_to_demand(productions, attractions, costs, beta, furness_epsilon, max_furness_steps):
    print("tbf_demand :" + str(datetime.datetime.now()))
    # Initialisation
    demand0 = np.zeros((len(productions), len(attractions)))

    # Calcul des valeurs de demande à partir du logit
    prob = tools.logit(costs, beta)
    for i in range(0, np.size(productions)):
        if productions[i] == 0:  # dans ce cas, la demande est nulle
            continue
        for j in range(0, np.size(attractions)):
            if attractions[j] == 0: # dans ce cas, la demande est nulle
                continue
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
            if demand0[i, j] == 0: # dans ce cas, la demande restera nulle
                continue
            curr_constraint.append((i, j, 1))
        constraints_set_1.append(curr_constraint)
    # Deuxième set de contraintes :
    # sum(j in S) x[i,j] = Pi
    constraints_set_2 = []
    for i in range(0, demand0_size[0]):
        curr_constraint = [(0, productions[i])]
        for j in range(0, demand0_size[1]):
            if demand0[i, j] == 0:  # dans ce cas, la demande restera nulle
                continue
            curr_constraint.append((i, j, 1))
        constraints_set_2.append(curr_constraint)

    #  Définition des sets de contraintes d'inégalité et d'égalité
    eq_constraints = (constraints_set_1, constraints_set_2) #  Deux sets de contrainte d'égalité
    ineq_constraints = ()  # Pas de contraintes d'inégalité

    # Exécution de l'algorithme de Furness
    demand = tools.furness(demand0, eq_constraints, ineq_constraints, furness_epsilon, max_furness_steps)

    return demand


# Trajets initiaux - renvoie la matrice des trajets initiaux
def calc_initial_trips(demand, productions, nb_stops_by_trips, costs, beta, epsilon, max_steps):
    print("tbf_initial :" + str(datetime.datetime.now()))
    ### Initialisation de la variable de sortie
    initial_trips: ndarray = np.ndarray((len(demand), len(demand)))

    ### Calcul préliminaire pour distribution des trajets
    prob = tools.logit(costs, beta)

    ### Génération pour chaque zone de production successivement
    for o in range(0, len(demand)):
        ## Distribution initiale des trajets
        # si la production de la zone d'origine est nulle, pas de trajets
        if productions[o] == 0:
            initial_trips[o] = np.zeros((1, len(demand)))
            continue
        # si la production de la zone d'origine n'est pas nulle, il peut y avoir des trajets
        initial_trips_0 = np.ndarray((1, len(demand)))
        for j in range(0, len(demand)):
            initial_trips_0[0, j] = prob[o, j] * demand[o, j]  # normalisation par l'attraction
            # normalization par emission -> productions[o] / nb_stops_by_trips

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
        curr_constraint = [(0, 0)]  # Initialisation des type et valeur de contrainte
        goal_value = 0  # Valeur objectif de la contrainte (ce set de contraintes ne contient qu'une seule contrainte)
        for j in range(0, len(demand)):
            goal_value += demand[o, j]
            curr_constraint.append((0, j, 1))
        curr_constraint[0] = (0, goal_value / nb_stops_by_trips)  # Mise à jour des type et valeur de la contrainte
        constraints_set_1.append(curr_constraint)  # Ajout de la contrainte au set

        # Deuxième set de contraintes :
        # pour chaque j, s[o, j] <= x[o,j]
        constraints_set_2 = []  # Initialisation du set de contraintes
        for j in range(0, len(demand)):
            curr_constraint = [(-1, demand[o, j]), (0, j, 1)]  # Définition de la contrainte d'inégalité leq
            constraints_set_2.append(curr_constraint)  # Ajout de la contrainte au set
        #  Définition des sets de contraintes d'égalité et d'inégalité
        eq_constraints = (constraints_set_1,)  # virgule nécessaire pour un représenter un tuple à un seul élément
        ineq_constraints = (constraints_set_2,)  # virgule nécessaire pour un représenter un tuple à un seul élément

        # Application de Furness à partir des variables, sets de contraintes et paramètres définis
        initial_trips[o] = tools.furness(initial_trips_0, eq_constraints, ineq_constraints, epsilon, max_steps)

    return initial_trips


# Trajets intermédiaires - renvoie la matrice des trajets intermédiaires
def calc_intermediate_trips(demand, productions, initial_trips, costs, beta, epsilon, max_steps):
    print("tbf_intermediate :" + str(datetime.datetime.now()))
    ### Initialisation de la variable de sortie
    intermediate_trips = np.zeros((len(demand), len(demand), len(demand)))

    ### Génération pour chaque origine
    for o in range(0, len(demand)):
        if productions[o] == 0:  # si la production de la zone de référence est nulle, pas de trajets
            intermediate_trips[o] = np.zeros((len(demand), len(demand)))
            continue
        # si la production de la zone de référence n'est pas nulle, il peut y avoir des trajets
        ## Distribution initiale des trajets
        # calcul des coûts à appliquer à cette étape du modèle, i.e. les savings
        savings = tools.calculate_savings(o, costs)
        # calcul de la distribution initiale à l'aide du logit
        prob = tools.logit(savings, beta)
        intermediate_trips_0 = np.zeros((len(demand), len(demand)))
        for i in range(0, len(demand)):
            for j in range(0, len(demand)):
                intermediate_trips_0[i, j] = prob[i, j] * (demand[o, j] - initial_trips[o, j]) #demand[o, i]  # demand[o, i]
                # normalisation par attraction avec demande totale : demand[o, j]
                # normalisation par attraction avec demande restante : demand[o, j]  - initial_trips[o, j])
                # normalization par emission avec demande total : demand[o, i] -> tb_freight in VISUM

        ## Algorithme de Furness
        # Définitions des sets de contraintes dans Furness
        # Premier set de contraintes :
        # sum(i in S) t[o, i, j] = x[o,j] - s[o, j] for all j in S
        constraints_set_1 = []
        for j in range(0, len(demand)):
            # utilisation de la fonction max pour éviter les valeurs négatives dûes aux arrondis
            # si initial_trips[o, j] = demand[o, j]+alpha avec alpha < tolerance_furness, on aura des valeurs négatives
            curr_constraint = [(0, max(0, demand[o, j] - initial_trips[o, j]))]
            for i in range(0, len(demand)):
                curr_constraint.append((i, j, 1))
            constraints_set_1.append(curr_constraint)
        # Deuxième set de contraintes :
        # sum(j in S) t[o, i, j] <= x[o,i] for all i in S
        constraints_set_2 = []
        for i in range(0, len(demand)):
            curr_constraint = [(-1, demand[o, i])]
            for j in range(0, len(demand)):
                curr_constraint.append((i, j, 1))
            constraints_set_2.append(curr_constraint)

        #  Définition des sets de contraintes d'égalité et d'inégalité
        eq_constraints = (constraints_set_1,)  # comma necessary to represent tuple with single element
        ineq_constraints = (constraints_set_2,)  # comma necessary to represent tuple with single element

        # Application de Furness à partir des variables, sets de contraintes et paramètres définis
        intermediate_trips[o] = tools.furness(intermediate_trips_0, eq_constraints, ineq_constraints, epsilon,
                                              max_steps)

    return intermediate_trips


#  Trajets finaux - renvoie la matrice des trajets finaux
def calc_final_trips(demand, productions, initial_trips, intermediate_trips):
    print("tbf_final :" + str(datetime.datetime.now()))
    ### Initialisation de la variable
    final_trips = np.zeros((len(demand), len(demand)))
    for i in range(0, len(initial_trips)):
        for o in range(0, len(initial_trips)):
            # si la production de la zone de référence est nulle, pas de trajets retours
            if productions[o] == 0:
                continue
            final_trips[i, o] = demand[o, i]
            for j in range(0, len(demand)):
                final_trips[i, o] -= intermediate_trips[o, i, j]

    return final_trips