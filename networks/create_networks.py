import math
import numpy as np
import network_creations_tools as nct

# 8 zones - 80 zones - 800 zones - 8'000 zones
"""
### GRID 3 - points lointains
grid_name = "far_point"  # Nom du réseau dans l'output
## Définition des motifs
# attractions
attr_pattern = np.array([[1, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 1, 1, 1, 0, 0],
                         [0, 0, 1, 0, 1, 0, 0],
                         [0, 0, 1, 1, 1, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0]])
# productions
prod_pattern = np.zeros((7, 7))
prod_pattern[3, 3] = 1
# distance entre zones contigues
grid_interdistance = 1
## Multiplication du pattern à l'horizontale et à la verticale
pattern_horizontal_copy = 6
pattern_vertical_copy = 6
## Création des fichiers de patterns correspondants
nct.create_regular_pattern_grid(prod_pattern, attr_pattern,
                                pattern_horizontal_copy, pattern_vertical_copy,
                                grid_interdistance, grid_name)

"""
### GRID 1 - regular
grid_name = "central_hub" # Nom du réseau dans l'output
## Définition des motifs
# attractions
attr_pattern = np.ones((7, 7))
attr_pattern[3, 3] = 0
# productions
prod_pattern = np.zeros((7, 7))
prod_pattern[3, 3] = 1
# distance entre zones contigues
grid_interdistance = 1
## Multiplication du pattern à l'horizontale et à la verticale
pattern_horizontal_copy = 0
pattern_vertical_copy = 1
## création des fichiers de patterns correspondants
nct.create_regular_pattern_grid(prod_pattern, attr_pattern,
                                pattern_horizontal_copy, pattern_vertical_copy,
                                grid_interdistance, grid_name)


# GRID 2 - irregular
# grid_name = "central_hub_irreg"
# attr_pattern = np.array([[1, 1, 1, 1, 1, 1], [1, 0, 1, 1, 1, 1], [1, 1, 1, 1, 0, 1]])
# prod_pattern = np.array([[0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0]])
# grid_interdistance = 1
# pattern_horizontal_copy = 10
# pattern_vertical_copy = 20
# nct.create_regular_pattern_grid(prod_pattern, attr_pattern,
#                                 pattern_horizontal_copy, pattern_vertical_copy,
#                                 grid_interdistance, grid_name)




