
import os
import tb_freight

import math
import numpy as np
import numpy.matlib
import datetime
import tools

# central hub
furness_epsilon = 0.000001
max_furness_steps = 100000
nb_stops_by_trips = 5
beta_dem = 1
input_path = os.getcwd() + "/input/"
folder_names = ("central_hub_grid14x7_interd1",)
for i_folder in range(0, len(folder_names)):
    input_folder = input_path + folder_names[i_folder]

    # tb-freight_LAR
    beta_ini = 1
    beta_inter = -1
    try:
        tb_freight.tb_freight_folder_LAR(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter,
                                     furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)
    
    # tb-freight Martin
    '''
    try:
        tb_freight.tb_freight_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter,
                                     furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)
    '''

# import beta_test
# import behavioral_test
# import speed_test