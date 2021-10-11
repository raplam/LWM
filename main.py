# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    # print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

# Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#    print_hi('PyCharm')

import numpy as np
from numpy import ndarray

import alt1
import alt1_retoursfin
import alt2
import tb_freight
import tools


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

# global variables

# input variables
prod_file = "C:\\Users\\MRE\PycharmProjects\\LiferwagenModellierung\\input\\ARE-productions.txt"
attr_file = "C:\\Users\\MRE\\PycharmProjects\\LiferwagenModellierung\\input\\ARE-attractions.txt"
costs_file = "C:\\Users\\MRE\\PycharmProjects\\LiferwagenModellierung\\input\\ARE-distances.txt"
nb_stops_by_trips = 2
beta_dem = 1
beta_ini = 10
beta_inter = -1
beta_final = 10
furness_epsilon = 0.01
max_furness_steps = 100
output = "C:\\Users\\MRE\\PycharmProjects\\LiferwagenModellierung\\output\\output"

tb_freight.tb_freight(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, furness_epsilon, max_furness_steps, output)

# Alt 1
# alt1.alt_1(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_ini, beta_inter, beta_final, furness_epsilon, max_furness_steps, output)

# Alt 1 retours à la fin
# alt1_retoursfin.alt_1r(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_ini, beta_inter, beta_final, furness_epsilon, max_furness_steps, output)

# Alt 2
# alt2.alt_2(prod_file, attr_file, costs_file, nb_stops_by_trips, beta_dem, beta_ini, beta_inter, furness_epsilon, max_furness_steps, output)