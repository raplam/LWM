import math
import numpy as np
import os

# Ajoute le motif de droite au motif de gauche. Les deux motifs doivent avoir le même nombre de lignes.
def add_right(left_pattern, right_pattern):
    return np.concatenate((left_pattern, right_pattern), axis=1)

# Ajoute le motif du bas au motif du haut. Les deux motifs doivent avoir le même nombre de colonne.
def add_down(up_pattern, down_pattern):
    return np.concatenate((up_pattern, down_pattern), axis=0)

# crée le réseau à partir du motif donné et des paramètres
def create_regular_pattern_grid(prod_pattern, attr_pattern, pattern_horizontal_copy, pattern_vertical_copy, grid_interdistance, network_name, norm_value=0):
    # initialisation des grilles
    prod_horizontal_grid = prod_pattern
    attr_horizontal_grid = attr_pattern

    # Concatenation des motifs selon input
    for i in range(0, pattern_horizontal_copy):
        prod_horizontal_grid = add_right(prod_horizontal_grid, prod_pattern)
        attr_horizontal_grid = add_right(attr_horizontal_grid, attr_pattern)
    prod_vertical_grid = prod_horizontal_grid
    attr_vertical_grid = attr_horizontal_grid
    for j in range(0, pattern_vertical_copy):
        prod_vertical_grid = add_down(prod_vertical_grid, prod_horizontal_grid)
        attr_vertical_grid = add_down(attr_vertical_grid, attr_horizontal_grid)

    # Normalisation des motifs en attractions et en productions
    # Normalisation de base à partir de l'attraction totale
    prod_grid = prod_vertical_grid
    attr_grid = attr_vertical_grid
    total_prod = sum(sum(prod_grid, 0), 0)
    total_attr = sum(sum(attr_grid, 0), 0)
    if norm_value == 0:
        normalization_value = total_attr
    else:
        normalization_value = norm_value
    prod_grid = normalization_value / total_prod * prod_grid
    attr_grid = normalization_value / total_attr * attr_grid

    # Transformation des grilles d'attraction en vecteur
    total_nb_zones = len(prod_grid)*len(prod_grid[0])
    prod_vec = np.zeros(total_nb_zones)
    attr_vec = np.zeros(total_nb_zones)
    x_vec = np.zeros(total_nb_zones)
    y_vec = np.zeros(total_nb_zones)
    for i1 in range(0, len(prod_grid)):
        for j1 in range(0, len(prod_grid[0])):
            prod_vec[i1*len(prod_grid[0])+j1] = prod_grid[i1, j1]
            attr_vec[i1 * len(prod_grid[0]) + j1] = attr_grid[i1, j1]
            x_vec[i1 * len(prod_grid[0]) + j1]=i1*grid_interdistance
            y_vec[i1 * len(prod_grid[0]) + j1]=j1*grid_interdistance

    # Définition de la matrice des distances
    distance_grid = np.zeros((total_nb_zones, total_nb_zones))
    for i2 in range(0, total_nb_zones):
        # x1 = i2 // len(prod_grid) # floor
        # y1 = i2 % len(prod_grid) # modulo
        for j2 in range(0, total_nb_zones):
            '''
            x2 = j2 // len(prod_grid) # floor
            y2 = j2 % len(prod_grid) # modulo
            square_dist = (x2 - x1)**2 + (y1 - y2)**2
            distance_grid[i2, j2] = grid_interdistance * math.sqrt(square_dist)
            '''
            square_dist = (x_vec[i2] - x_vec[j2])**2 + (y_vec[i2] - y_vec[j2])**2
            distance_grid[i2, j2] = grid_interdistance * math.sqrt(square_dist)

    # Sauvegarde
    network_instance = network_name + "_grid" + str(len(prod_grid)) + "x" + str(len(prod_grid[0])) + "_interd" + str(grid_interdistance)
    dirpath = os.getcwd() + "/" + network_instance
    # create directory if necessary
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)
    np.savetxt(dirpath + "/" + network_instance + "-productions.txt", prod_vec, fmt='%1.3f', delimiter='\t')
    np.savetxt(dirpath + "/" + network_instance + "-attractions.txt", attr_vec, fmt='%1.3f', delimiter='\t')
    np.savetxt(dirpath + "/" + network_instance + "-distances.txt", distance_grid, fmt='%1.3f', delimiter='\t')
    np.savetxt(dirpath + "/" + network_instance + "-x.txt", x_vec, fmt='%1.3f', delimiter='\t')
    np.savetxt(dirpath + "/" + network_instance + "-y.txt", y_vec, fmt='%1.3f', delimiter='\t')