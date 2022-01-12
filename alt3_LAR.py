import datetime
import math
import os
import numpy as np
from numpy import ndarray
import time

import tools
from analysis import LWM_analysis


# Alt-3

#  Fonction utilisée pour faire des runs à partir d'un dossier contenant les inputs de production, attraction et coûts
#  Les inputs portent le même nom que le dossier en y accolant un suffixe selon le type d'input
#  "-productions.txt" (productions) : liste des valeurs de production de chaque zone sous forme de colonne
#  "-attractions.txt" (attractions) : liste des valeurs d'attraction de chaque zone sous forme de colonne
#  "-distances" : coûts généralisés (costs) : matrice des coûts pour laquelle les stations sont ordonnées
#                 selon les lignes comme dans les fichiers de productions et d'attractions

def alt3_folder_LAR(input_folder, nb_stops_by_trips, beta_ini, beta_inter, epsilon, max_steps):
    prod_file = input_folder + "/" + input_folder[input_folder.rfind("/")+1:] + "-productions.txt"
    attr_file = input_folder + "/" + input_folder[input_folder.rfind("/")+1:] + "-attractions.txt"
    costs_file = input_folder + "/" + input_folder[input_folder.rfind("/")+1:] + "-distances.txt"
    # Chemin du dossier d'output des résultats
    output_folder = os.getcwd() + "/output/" + input_folder[input_folder.rfind("/")+1:] + "_LAR"
    if not os.path.exists(output_folder):  # Création du dossier d'output si non existant
        os.mkdir(output_folder)
    # Chemin et nom du fichier d'output des résultats
    output_file_name = output_folder + "/" +output_folder[output_folder.rfind("/")+1:] + \
                       "_alt3_nb" + str(nb_stops_by_trips) + \
                       + "_bi" + str(beta_ini) + "_bint" + str(beta_inter) + \
                       "_e" + str(math.log10(epsilon)) + "_ms" + str(max_steps)
    # Exécution du modèle selon les inputs désirés
    alt3_LAR(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_ini, beta_inter, epsilon, max_steps, output_file_name, input_folder[input_folder.rfind("/")+1:]+"_LAR")

def alt3_LAR(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_ini, beta_inter, epsilon, max_steps, output_file_name, folder_name):
    # Lecture des données d'entrée
    costs = np.loadtxt(costs_file)
    productions = np.loadtxt(prod_file)
    attractions = np.loadtxt(attr_file)
    
    start_time = time.time()

    N=np.shape(costs)[0]

    # initialize the matrices for initial, intermediary and final trips
    initial_trips=np.zeros((N,N))
    intermediate_trips=np.zeros((N,N))
    final_trips=np.zeros((N,N))
    
    # Trajets initiaux
    initial_trips_from_o=np.multiply(np.exp(-beta_ini*costs[o,:]),demand[o,:])
    initial_trips_from_o = tools.Furness_LAR(initial_trips_from_o, demand[o,:], np.sum(demand[o,:]) / nb_stops_by_trips, True, False, epsilon, max_steps)
    initial_trips[o,:]=initial_trips_from_o

    # Trajets intermédiaires
    for k in range(1,nb_stops_by_trips)
      savings=tools.calculate_savings_LAR(o,costs)
      intermediate_trips_from_o=np.multiply(np.exp(-beta_inter*savings),np.matlib.repmat(demand[o,:],N,1).T)
      intermediate_trips_from_o=tools.Furness_LAR(intermediate_trips_from_o,demand[o,:]-initial_trips_from_o,demand[o,:], False, True, epsilon, max_steps)
      intermediate_trips = intermediate_trips + intermediate_trips_from_o

      # Trajets finaux
      final_trips[:,o] = demand[o,:]-np.sum(intermediate_trips_from_o,axis=1) #axis=1: sum over columns (axis=0 for sum over rows)  
    
    end_time = time.time()
    # Output
    np.savetxt((output_file_name + "-demand.txt"), demand, fmt='%1.6f', delimiter='\t')
    np.savetxt((output_file_name + "-initial.txt"), initial_trips, fmt='%1.6f', delimiter='\t')
    np.savetxt((output_file_name + "-intermediate.txt"), intermediate_trips, fmt='%1.6f', delimiter='\t')
    np.savetxt((output_file_name + "-final.txt"), final_trips, fmt='%1.6f', delimiter='\t')

    post_process = LWM_analysis.post_processing(demand, nb_stops_by_trips, initial_trips,intermediate_trips, final_trips, costs)
    LWM_analysis.save_output(post_process, end_time - start_time, folder_name, output_file_name)
