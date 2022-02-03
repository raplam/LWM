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
                       "_bi" + str(beta_ini) + "_bint" + str(beta_inter) + \
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
    demand=np.zeros((N,N)) # in alternative 3, it is an output only, not an input
    initial_trips=np.zeros((N,N))
    intermediate_trips=np.zeros((N,N))
    
    # Trajets initiaux
    initial_trips=np.exp(-beta_ini*costs)
    initial_trips = tools.Furness_LAR(initial_trips, attractions, productions / nb_stops_by_trips, True, False, epsilon, max_steps)
    demand=demand+initial_trips
 
    # Trajets intermédiaires # defined only because the post_processing function requires it, but it is not used by Alternative 3.
    current_positions=np.sum(initial_trips,axis=0)
    relation_to_origins=initial_trips # the value (i,j) says how many vehicles have origin i and are currently in j. After iterating over all ranks of intermediate trips, the matrix of return trips is simply the transpose of the matrix of relaion_to_origins.
    for k in range(1,nb_stops_by_trips):
      # Furness for legs of rank k
      intermediate_trips_rank_k=tools.Furness_LAR(np.exp(-beta_inter*costs),attractions-np.sum(intermediate_trips+initial_trips,axis=0),current_positions, True, False, epsilon, max_steps)
      # add them to the previous ones
      intermediate_trips = intermediate_trips + intermediate_trips_rank_k
      # update the current positions
      current_positions=np.sum(intermediate_trips_rank_k,axis=0)
      # update the current relations to origins
      matrix_f=np.divide(relation_to_origins,np.matlib.repmat(np.sum(relation_to_origins, axis=0),N,1),out=np.zeros_like(relation_to_origins),where=np.matlib.repmat(np.sum(relation_to_origins, axis=0),N,1)!=0)
      relation_to_origins=np.matmul(matrix_f,intermediate_trips_rank_k)

      # update the demand matrix
      demand=demand+relation_to_origins
      
    # Trajets finaux
    final_trips=relation_to_origins.T
    
    end_time = time.time()
    # Output
    np.savetxt((output_file_name + "-demand.txt"), demand, fmt='%1.6f', delimiter='\t')
    np.savetxt((output_file_name + "-initial.txt"), initial_trips, fmt='%1.6f', delimiter='\t')
    np.savetxt((output_file_name + "-intermediate.txt"), intermediate_trips, fmt='%1.6f', delimiter='\t')
    np.savetxt((output_file_name + "-final.txt"), final_trips, fmt='%1.6f', delimiter='\t')

    post_process = LWM_analysis.post_processing(demand, nb_stops_by_trips, initial_trips,intermediate_trips, final_trips, costs)
    LWM_analysis.save_output(post_process, end_time - start_time, folder_name, output_file_name)
