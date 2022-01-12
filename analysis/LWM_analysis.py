import pickle
import os
import datetime


# all saving characteristics in one
def save_output(post_process, run_time: float, folder_name, output_file_name):
    # save entire data base in dictionary form
    post_process_save_file = open(output_file_name + "-post_process.pkl", "wb")
    pickle.dump(post_process, post_process_save_file)
    # obtain directly usable information
    log_path = "output/"+folder_name+"/output_log.txt"
    log_file = open(log_path, "a")
    if os.stat(log_path).st_size == 0:
        header_string = "date\trun_id\trun_time\tinitial_trips_average\tinitial_trips_variance\tinterm_trips_average\t" \
                        "interm_trips_variance\tfinal_trips_average\tfinal_trips_variance\ttour_eff_ratio\r"
        log_file.write(header_string)
    w_string = str(datetime.datetime.now())
    w_string += "\t" + output_file_name[output_file_name.rfind("/") + 1:]
    w_string += "\t" + str(run_time)
    w_string += "\t" + str(post_process["initial_trips_average"])
    w_string += "\t" + str(post_process["initial_trips_variance"])
    w_string += "\t" + str(post_process["intermediate_trips_average"])
    w_string += "\t" + str(post_process["intermediate_trips_variance"])
    w_string += "\t" + str(post_process["final_trips_average"])
    w_string += "\t" + str(post_process["final_trips_variance"])
    w_string += "\t" + str(post_process["tour_efficiency_ratio"])
    w_string += "\r"
    log_file.write(w_string)
    log_file.close()


# post-processing function
def post_processing(demand, nb_stops_by_trips, initial_trips,intermediate_trips, final_trips, costs):
    ini_dict = trip_length_distribution(initial_trips, costs)
    ini_av = dict_average(ini_dict)
    ini_var = dict_variance(ini_dict)
    interm_dict = trip_length_distribution(intermediate_trips, costs)
    interm_av = dict_average(interm_dict)
    interm_var = dict_variance(interm_dict)
    final_dict = trip_length_distribution(final_trips, costs)
    final_av = dict_average(final_dict)
    final_var = dict_variance(final_dict)

    tour_eff_ratio = tour_efficiency_ratio(demand, initial_trips,
                                           intermediate_trips, final_trips,
                                           costs)

    post_process_dict = {
        "number_of_stops_by_trip": nb_stops_by_trips,
        "initial_trips_distribution": ini_dict,
        "initial_trips_average": ini_av,
        "initial_trips_variance": ini_var,
        "intermediate_trips_distribution": interm_dict,
        "intermediate_trips_average": interm_av,
        "intermediate_trips_variance": interm_var,
        "final_trips_distribution": final_dict,
        "final_trips_average": final_av,
        "final_trips_variance": final_var,
        "tour_efficiency_ratio": tour_eff_ratio
    }

    return post_process_dict


#  distribution des trajets en termes de longueurs
def trip_length_distribution(trips, costs):
    ini_dict = {}
    for i in range(0, len(trips)):
        for j in range(0, len(trips[0])):
            if costs[i, j] in ini_dict:
                ini_dict[costs[i, j]] += trips[i, j]
            else:
                ini_dict[costs[i, j]] = trips[i, j]
    return ini_dict


def dict_average(curr_dict):
    pond_sum = 0
    coeff_sum = 0
    for key in curr_dict:
        pond_sum += key * curr_dict[key]
        coeff_sum += curr_dict[key]
    return pond_sum / coeff_sum


def dict_variance(curr_dict):
    pond_sum = 0
    coeff_sum = 0
    for key in curr_dict:
        pond_sum += key**2 * curr_dict[key]
        coeff_sum += curr_dict[key]
    return pond_sum / coeff_sum


# indicateur agrégé sur la qualité des tours réalisés
def total_trip_length_without_tours(demand, costs):
    value = 0
    for i in range(0, len(costs)):
        for j in range(0, len(costs)):
            value += demand[i, j] * (costs[i, j] + costs[j, i])
    return value


def total_trip_length_with_tours(initial_trips, intermediate_trips,
                                 final_trips, costs):
    value = 0
    for i in range(0, len(costs)):
        for j in range(0, len(costs)):
            value += (initial_trips[i, j] + intermediate_trips[i, j] +
                      final_trips[i, j]) * costs[i, j]
    return value


def tour_efficiency_ratio(demand, initial_trips, intermediate_trips,
                          final_trips, costs):
    return total_trip_length_with_tours(initial_trips, intermediate_trips, final_trips, costs) / \
           total_trip_length_without_tours(demand, costs)
