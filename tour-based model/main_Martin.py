import datetime
import os
import alt1
import alt1_retoursfin
import alt2
import alt3
import tb_freight


"""
# Changement de type de demande
furness_epsilon = 0.01
max_furness_steps = 1000
nb_stops_by_trips = 5
beta_dem = 1

input_path = os.getcwd() + "/input/"
#folder_names = ("central_hub_grid7x7_interd1", "central_hub_grid14x14_interd1", "central_hub_grid28x28_interd1",
#                "central_hub_grid56x56_interd1", "central_hub_grid91x91_interd1")
folder_names = ("central_hub_grid28x28_interd1",)
for i_folder in range(0, len(folder_names)):
    input_folder = input_path + folder_names[i_folder]

    # tb-freight
    beta_ini = 1
    beta_inter = -1
    try:
        tb_freight.tb_freight_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter,
                                     furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)


    # Alt 1
    beta_ini = 1
    beta_inter = 1
    beta_final = 1
    try:
        alt1.alt1_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter, beta_final,
                                     furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)

    # Alt 3
    beta_ini = 1
    beta_inter = 1
    beta_final = 1
    try:
        alt3.alt3_folder(input_folder, nb_stops_by_trips,
                          beta_dem, beta_ini, beta_inter, beta_final,
                          furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)

    # Alt 2
    beta_ini = 1
    beta_inter = -1
    try:
        alt2.alt2_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter,
                                     furness_epsilon, max_furness_steps)
    except Exception as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)
"""
"""
# Test de temps de calcul
furness_epsilon = 0.01
max_furness_steps = 1000
nb_stops_by_trips = 5
beta_dem = 1

input_path = os.getcwd() + "/input/"
#folder_names = ("central_hub_grid7x7_interd1", "central_hub_grid14x14_interd1", "central_hub_grid28x28_interd1",
#                "central_hub_grid56x56_interd1", "central_hub_grid91x91_interd1")
folder_names = ("central_hub_grid7x7_interd1", "central_hub_grid14x14_interd1", "central_hub_grid21x21_interd1", "central_hub_grid28x28_interd1", "central_hub_grid35x35_interd1")
for i_folder in range(0, len(folder_names)):
    input_folder = input_path + folder_names[i_folder]

    # tb-freight
    beta_ini = 1
    beta_inter = -1
    try:
        tb_freight.tb_freight_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter,
                                     furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)


    # Alt 1
    beta_ini = 1
    beta_inter = 1
    beta_final = 1
    try:
        alt1.alt1_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter, beta_final,
                                     furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)

    # Alt 3
    beta_ini = 1
    beta_inter = 1
    beta_final = 1
    try:
        alt3.alt3_folder(input_folder, nb_stops_by_trips,
                          beta_dem, beta_ini, beta_inter, beta_final,
                          furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)

    # Alt 2
    beta_ini = 1
    beta_inter = -1
    try:
        alt2.alt2_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter,
                                     furness_epsilon, max_furness_steps)
    except Exception as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)


furness_epsilon = 0.01
max_furness_steps = 1000
nb_stops_by_trips = 2
beta_dem = 1
input_path = os.getcwd() + "/input/"
folder_names = ("central_hub_grid28x28_interd1", "central_hub_grid14x14_interd1")
for i_folder in range(0, len(folder_names)):
    input_folder = input_path + folder_names[i_folder]

    # tb-freight
    beta_ini = 1
    beta_inter = -1
    try:
        tb_freight.tb_freight_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter,
                                     furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)


    # Alt 1
    beta_ini = 1
    beta_inter = 1
    beta_final = 1
    try:
        alt1.alt1_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter, beta_final,
                                     furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)

    # Alt 3
    beta_ini = 1
    beta_inter = 1
    beta_final = 1
    try:
        alt3.alt3_folder(input_folder, nb_stops_by_trips,
                          beta_dem, beta_ini, beta_inter, beta_final,
                          furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)


    # Alt 2
    beta_ini = 1
    beta_inter = -1
    try:
        alt2.alt2_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter,
                                     furness_epsilon, max_furness_steps)
    except Exception as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)

furness_epsilon = 0.01
max_furness_steps = 1000
nb_stops_by_trips = 10
beta_dem = 1
input_path = os.getcwd() + "/input/"
folder_names = ("central_hub_grid14x14_interd1", "central_hub_grid28x28_interd1")  # "central_hub_grid14x14_interd1")
for i_folder in range(0, len(folder_names)):
    input_folder = input_path + folder_names[i_folder]

    # tb-freight
    beta_ini = 1
    beta_inter = -1
    try:
        tb_freight.tb_freight_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter,
                                     furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)
      
    # Alt 1
    beta_ini = 1
    beta_inter = 1
    beta_final = 1
    try:
        alt1.alt1_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter, beta_final,
                                     furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)

    # Alt 3
    beta_ini = 1
    beta_inter = 1
    beta_final = 1
    try:
        alt3.alt3_folder(input_folder, nb_stops_by_trips,
                          beta_dem, beta_ini, beta_inter, beta_final,
                          furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)

    # Alt 2
    beta_ini = 1
    beta_inter = -1
    try:
        alt2.alt2_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter,
                                     furness_epsilon, max_furness_steps)
    except Exception as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)

# Modification de la tolérance de Furness
furness_epsilon = 0.001
max_furness_steps = 1000
nb_stops_by_trips = 5
beta_dem = 1
input_path = os.getcwd() + "/input/"
folder_names = ("central_hub_grid28x28_interd1",)
for i_folder in range(0, len(folder_names)):
    input_folder = input_path + folder_names[i_folder]

    # tb-freight
    beta_ini = 1
    beta_inter = -1
    try:
        tb_freight.tb_freight_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter,
                                     furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)

    # Alt 1
    beta_ini = 1
    beta_inter = 1
    beta_final = 1
    try:
        alt1.alt1_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter, beta_final,
                                     furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)

    # Alt 3
    beta_ini = 1
    beta_inter = 1
    beta_final = 1
    try:
        alt3.alt3_folder(input_folder, nb_stops_by_trips,
                          beta_dem, beta_ini, beta_inter, beta_final,
                          furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)

    # Alt 2
    beta_ini = 1
    beta_inter = -1
    try:
        alt2.alt2_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter,
                                     furness_epsilon, max_furness_steps)
    except Exception as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)

# Modification de la tolérance de Furness
furness_epsilon = 0.1
max_furness_steps = 1000
nb_stops_by_trips = 5
beta_dem = 1
input_path = os.getcwd() + "/input/"
folder_names = ("central_hub_grid28x28_interd1",)
for i_folder in range(0, len(folder_names)):
    input_folder = input_path + folder_names[i_folder]

    # tb-freight
    beta_ini = 1
    beta_inter = -1
    try:
        tb_freight.tb_freight_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter,
                                     furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)

    # Alt 1
    beta_ini = 1
    beta_inter = 1
    beta_final = 1
    try:
        alt1.alt1_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter, beta_final,
                                     furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)

    # Alt 3
    beta_ini = 1
    beta_inter = 1
    beta_final = 1
    try:
        alt3.alt3_folder(input_folder, nb_stops_by_trips,
                          beta_dem, beta_ini, beta_inter, beta_final,
                          furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)


    # Alt 2
    beta_ini = 1
    beta_inter = -1
    try:
        alt2.alt2_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter,
                                     furness_epsilon, max_furness_steps)
    except Exception as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)

# Valeurs de beta
furness_epsilon = 0.01
max_furness_steps = 1000
nb_stops_by_trips = 5
beta_dem = 1
input_path = os.getcwd() + "/input/"
folder_names = ("central_hub_grid14x14_interd1", "central_hub_grid28x28_interd1")
for i_folder in range(0, len(folder_names)):
    input_folder = input_path + folder_names[i_folder]

    betas_ini = [1, 3]
    betas_inter = [-1, -3]
    for i_1 in range(0, len(betas_ini)):
        for j_1 in range(0, len(betas_inter)):
            # tb-freight
            try:
                tb_freight.tb_freight_folder(input_folder, nb_stops_by_trips,
                                             beta_dem, betas_ini[i_1], betas_inter[j_1],
                                             furness_epsilon, max_furness_steps)
            except MemoryError as error:
                print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(
                    error) + '\r')
                print(error)

            # Alt 2
            try:
                alt2.alt2_folder(input_folder, nb_stops_by_trips,
                                  beta_dem, betas_ini[i_1], betas_inter[j_1],
                                  furness_epsilon, max_furness_steps)
            except MemoryError as error:
                print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(
                    error) + '\r')
                print(error)

    betas_ini = [1, 3]
    betas_inter = [1, 3]
    betas_final = [1, 3]
    for i_2 in range(0, len(betas_ini)):
        for j_2 in range(0, len(betas_inter)):
            for k_2 in range(0, len(betas_final)):
                # Alt 1
                try:
                    alt1.alt1_folder(input_folder, nb_stops_by_trips,
                                      beta_dem, betas_ini[i_2], betas_inter[j_2], betas_final[k_2],
                                      furness_epsilon, max_furness_steps)
                except MemoryError as error:
                    print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(
                        error) + '\r')
                    print(error)

                # Alt 3
                try:
                    alt3.alt3_folder(input_folder, nb_stops_by_trips,
                                      beta_dem, betas_ini[i_2], betas_inter[j_2], betas_final[k_2],
                                      furness_epsilon, max_furness_steps)
                except MemoryError as error:
                    print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(
                        error) + '\r')
                    print(error)
"""
# far-grid
furness_epsilon = 0.01
max_furness_steps = 1000
nb_stops_by_trips = 5
beta_dem = 1
input_path = os.getcwd() + "/input/"
folder_names = ("far_point_grid14x14_interd1",)
for i_folder in range(0, len(folder_names)):
    input_folder = input_path + folder_names[i_folder]

    # Alt 3
    beta_ini = 1
    beta_inter = 1
    beta_final = 1
    try:
        alt3.alt3_folder(input_folder, nb_stops_by_trips,
                          beta_dem, beta_ini, beta_inter, beta_final,
                          furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)

    # tb-freight
    beta_ini = 1
    beta_inter = -1
    try:
        tb_freight.tb_freight_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter,
                                     furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)

    # Alt 1
    beta_ini = 1
    beta_inter = 1
    beta_final = 1
    try:
        alt1.alt1_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter, beta_final,
                                     furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)

    # Alt 2
    beta_ini = 1
    beta_inter = -1
    try:
        alt2.alt2_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter,
                                     furness_epsilon, max_furness_steps)
    except Exception as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)

# import beta_test
# import behavioral_test
# import speed_test


furness_epsilon = 0.01
max_furness_steps = 1000
nb_stops_by_trips = 5
beta_dem = 1
input_path = os.getcwd() + "/input/"
furness_epsilon = 0.01
folder_names = ("central_hub_grid56x56_interd1", "central_hub_grid91x91_interd1",)  # "central_hub_grid7x7_interd1", "central_hub_grid14x14_interd1", "central_hub_grid56x56_interd1",
for i_folder in range(0, len(folder_names)):
    input_folder = input_path + folder_names[i_folder]

    # Alt 1
    beta_ini = 1
    beta_inter = 1
    beta_final = 1
    try:
        alt1.alt1_folder(input_folder, nb_stops_by_trips,
                                     beta_dem, beta_ini, beta_inter, beta_final,
                                     furness_epsilon, max_furness_steps)
    except MemoryError as error:
        print(('An exception occurred during the run of tbf_' + folder_names[i_folder] + ': {}').format(error) + '\r')
        print(error)

    # Alt 3
    beta_ini = 1
    beta_inter = 1
    beta_final = 1
    alt3.alt3_folder(input_folder, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, beta_final,
                                 furness_epsilon, max_furness_steps)

print(str(datetime.datetime.now()) + " END")
"""
# Test des fonctions de base
# Logit
# costs: ndarray = np.zeros((3, 3))
# costs[0, 0] = 0
# costs[1, 1] = 0
# costs[2, 2] = 0
# costs[0, 1] = np.log(2)
# costs[1, 0] = np.log(2)
# costs[0, 2] = 2*np.log(2)
# costs[2, 0] = 2*np.log(2)
# costs[1, 2] = np.log(3)
# costs[2, 1] = np.log(3)
# beta = 0.2
# p = tools.logit(costs, beta)

# Furness
# demand =
# productions =
# attractions =
# epsilon =
# max_steps =


# input variables
# prod_file = "C:/Users/MRE\PycharmProjects/LiferwagenModellierung/input/central_hub_grid14x14_interd1/central_hub_grid14x14_interd1-productions.txt"
# attr_file = "C:/Users/MRE/PycharmProjects/LiferwagenModellierung/input/central_hub_grid14x14_interd1/central_hub_grid14x14_interd1-attractions.txt"
# costs_file = "C:/Users/MRE/PycharmProjects/LiferwagenModellierung/input/central_hub_grid14x14_interd1/central_hub_grid14x14_interd1-distances.txt"


# prod_file = "C:/Users/MRE\PycharmProjects/LiferwagenModellierung/input/ARE2/ARE2-productions.txt" # ARE2-productions.txt"
# attr_file = "C:/Users/MRE/PycharmProjects/LiferwagenModellierung/input/ARE2/ARE2-attractions.txt" # ARE2-attractions.txt"
# costs_file = "C:/Users/MRE/PycharmProjects/LiferwagenModellierung/input/ARE2/ARE2-distances.txt" # ARE2-distances.txt"


# prod_file = "C:/Users/MRE\PycharmProjects/LiferwagenModellierung/input/3stations/3stations-productions.txt"
# attr_file = "C:/Users/MRE/PycharmProjects/LiferwagenModellierung/input/3stations/3stations-attractions.txt"
# costs_file = "C:/Users/MRE/PycharmProjects/LiferwagenModellierung/input/3stations/3stations-distances.txt"

# general parameters
furness_epsilon = 0.01
max_furness_steps = 100
nb_stops_by_trips = 20
beta_dem = 1

# input_folder = "C:/Users/MRE/PycharmProjects/LiferwagenModellierung/input/3stations"
# output = "C:/Users/MRE/PycharmProjects/LiferwagenModellierung/output/"

# tb-freight
# beta_ini = 10
# beta_inter = -1
# tb_freight.tb_freight_folder(input_folder, nb_stops_by_trips, beta_dem, beta_ini, beta_inter,
                             #furness_epsilon, max_furness_steps)
# tb_freight.tb_freight(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_dem, beta_ini, beta_inter,
                      # furness_epsilon, max_furness_steps, output)

# Alt 1
# beta_ini = 10
# beta_inter = -1
# beta_final = 10
# alt1.alt_1(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_ini, beta_inter, beta_final, furness_epsilon,
           # max_furness_steps, output)

# Alt 1 retours à la fin
# beta_ini = 10
# beta_inter = -1
# alt1_retoursfin.alt_1r(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_ini, beta_inter, beta_final,
                       # furness_epsilon, max_furness_steps, output)

# Alt 2
# beta_ini = 10
# beta_inter = -1
# alt2.alt_2(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, furness_epsilon,
           # max_furness_steps, output)


input_path = os.getcwd() + "/input/"
folder_names = ("central_hub_grid7x7_interd1",)  # "central_hub_grid7x7_interd1", "central_hub_grid14x14_interd1", "central_hub_grid56x56_interd1",
for i_folder in range(0, len(folder_names)):
    input_folder = input_path + folder_names[i_folder]

    # Alt 3
    beta_ini = 1
    beta_inter = 1
    alt3.alt3_folder(input_folder, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, furness_epsilon,
                         max_furness_steps)

    # Alt 1 retours à la fin
    beta_ini = 1
    beta_inter = 1
    beta_final = 1
    alt1_retoursfin.alt_1r_folder(input_folder, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, beta_final,
                                      furness_epsilon, max_furness_steps)
    # alt1_retoursfin.alt_1r(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_ini, beta_inter, beta_final,
    # furness_epsilon, max_furness_steps, output)

    # Alt 2
    beta_ini = 1
    beta_inter = -1
    alt2.alt_2_folder(input_folder, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, furness_epsilon,
                          max_furness_steps)
    # alt2.alt_2(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, furness_epsilon,
    # max_furness_steps, output)

    # tb-freight
    beta_ini = 1
    beta_inter = -1
    tb_freight.tb_freight_folder(input_folder, nb_stops_by_trips, beta_dem, beta_ini, beta_inter,
                                     furness_epsilon, max_furness_steps)
    # tb_freight.tb_freight(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_dem, beta_ini, beta_inter,
    # furness_epsilon, max_furness_steps, output)


    # Alt 1
    beta_ini = 1
    beta_inter = 1
    beta_final = 1
    alt1.alt_1_folder(input_folder, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, beta_final,
                          furness_epsilon, max_furness_steps)
    # alt1.alt_1(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_ini, beta_inter, beta_final, furness_epsilon,
    # max_furness_steps, output)

input_path = os.getcwd() + "/input/"
folder_names = ("central_hub_grid84x84_interd1",)
for i_folder in range(0, len(folder_names)):
    input_folder = input_path + folder_names[i_folder]

    # Alt 1
    beta_ini = 1
    beta_inter = 1
    beta_final = 1
    alt1.alt_1_folder(input_folder, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, beta_final,
                          furness_epsilon, max_furness_steps)
    # alt1.alt_1(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_ini, beta_inter, beta_final, furness_epsilon,
    # max_furness_steps, output)

    # Alt 3
    beta_ini = 1
    beta_inter = 1
    alt3.alt3_folder(input_folder, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, furness_epsilon,
                     max_furness_steps)
"""



