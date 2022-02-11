#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import csv
import LWE_classes


def get_survey_dict(LWE_TRANSPORT_csv):
    lwe=pd.read_csv(LWE_TRANSPORT_csv, sep=";", encoding = "utf-8")
     
    lwe.drop_duplicates(inplace=True) # I could not find why keeping these duplicates would make sense. Ph. Marti (BFS) confirms that it is probably a mistake.
    
    lwe.to_csv("data/LWE_2013_TRANSPORT_ohne_duplicates.csv") 
    
    nb_rows = len(lwe.index)
    
    # I prefer to work with numpy, and will therefore extract only the columns of interest
    oid = np.squeeze(lwe[['OID']].to_numpy())
    anzahl_stopps = np.squeeze(lwe[['Anzahl_Stopps']].to_numpy())
    quelle_km = np.squeeze(lwe[['quelle_km']].to_numpy())
    ziel_km = np.squeeze(lwe[['ziel_km']].to_numpy())
    quelle_land = np.squeeze(lwe[['Quelle_Land']].to_numpy())
    quelle_npa = np.squeeze(lwe[['Quelle_NPA']].to_numpy())
    ziel_land = np.squeeze(lwe[['Ziel_Land']].to_numpy())
    ziel_npa = np.squeeze(lwe[['Ziel_NPA']].to_numpy())
    warengewicht = np.squeeze(lwe[['Warengewicht']].to_numpy())
    warengruppe = np.squeeze(lwe[['Warengruppe']].to_numpy())
    wh_tot_cal= np.squeeze(lwe[['wh_tot_cal']].to_numpy())
    strata= np.squeeze(lwe[['STRATA_ID']].to_numpy())
    main_use_goods_transport= np.squeeze(lwe[['MAIN_USE_GOODS_TRANSPORT']].to_numpy())
    main_use_service= np.squeeze(lwe[['MAIN_USE_SERVICE']].to_numpy())
    main_use_empty_journey= np.squeeze(lwe[['MAIN_USE_EMPTY_JOURNEY']].to_numpy())
    main_use_passenger= np.squeeze(lwe[['MAIN_USE_PASSENGER']].to_numpy())
    main_use_rental= np.squeeze(lwe[['MAIN_USE_RENTAL']].to_numpy())
    main_use_private= np.squeeze(lwe[['MAIN_USE_PRIVATE']].to_numpy())
    main_use_other= np.squeeze(lwe[['MAIN_USE_OTHER']].to_numpy())
    curb_weight= np.squeeze(lwe[['CURB_WEIGHT']].to_numpy())
    load_capa= np.squeeze(lwe[['LOADING_CAPACITY']].to_numpy())
    noga= np.squeeze(lwe[['NOGA_2008']].to_numpy())
    
    # modify NPA from zones abroad, such that they don't look like Swiss NPAs.
    quelle_npa=quelle_npa*(1+9999*(1-(np.equal(quelle_land,"CH"))))
    ziel_npa=ziel_npa*(1+9999*(1-(np.equal(ziel_land,"CH"))))
    
    # process the LWE into a dict of survey objects
    survey_dict={}
    summary_statistics=LWE_classes.SummaryStatistics()
    # Assumes the file is sorted by OID$
    for i in range (0, nb_rows):
        if i == 0:
            survey_inst=LWE_classes.Survey(oid[i], wh_tot_cal[i], strata[i],
                                           bool(main_use_empty_journey[i]), bool(main_use_goods_transport[i]),
                                           bool(main_use_other[i]), bool(main_use_passenger[i]),
                                           bool(main_use_private[i]), bool(main_use_rental[i]),
                                           bool(main_use_service[i]), curb_weight[i], load_capa[i], noga[i])
        elif survey_inst.oid != oid[i]:
            survey_inst.generate_leg_list()
            survey_inst.generate_reconstructed_tour_list()
            # Save the Survey instance
            survey_dict[survey_inst.oid]= survey_inst
            summary_statistics.nb_reconstructed_tours += len(survey_inst.reconstructed_tour_list)
            summary_statistics.nb_simplified_tours += len(survey_inst.simplified_tour_list)
            summary_statistics.nb_legs += len(survey_inst.leg_list)
            summary_statistics.nb_shipments += len(survey_inst.shipment_list)
            # Reinitialize the Survey instance
            survey_inst=LWE_classes.Survey(oid[i], wh_tot_cal[i], strata[i],
                                           bool(main_use_empty_journey[i]), bool(main_use_goods_transport[i]),
                                           bool(main_use_other[i]), bool(main_use_passenger[i]),
                                           bool(main_use_private[i]), bool(main_use_rental[i]),
                                           bool(main_use_service[i]), curb_weight[i], load_capa[i], noga[i])
        survey_inst.read_row(warengruppe[i], warengewicht[i], quelle_km[i], ziel_km[i], quelle_npa[i], ziel_npa[i], anzahl_stopps[i])
    
    # Add the last survey
    survey_inst.generate_leg_list()
    survey_inst.generate_reconstructed_tour_list()
    # Save the Survey instance
    survey_dict[survey_inst.oid]= survey_inst
    summary_statistics.nb_reconstructed_tours += len(survey_inst.reconstructed_tour_list)
    summary_statistics.nb_simplified_tours +=len(survey_inst.simplified_tour_list)
    summary_statistics.nb_legs += len(survey_inst.leg_list)
    summary_statistics.nb_shipments += len(survey_inst.shipment_list)
    return survey_dict, summary_statistics


def write_shipment_list_into_csv(LWE_TRANSPORT_csv):
    survey_dict, summary_statistics=get_survey_dict(LWE_TRANSPORT_csv)
    # Generate list of shipments (includes first and last legs of tours, but not intermediary legs)
    shipment_data=np.empty((summary_statistics.nb_shipments, 14))
    k = 0
    for i in survey_dict:
        survey_inst = survey_dict[i]
        for shipment_inst in survey_inst.shipment_list:
            shipment_data[k, 0] = survey_inst.oid
            shipment_data[k, 1] = survey_inst.weight
            shipment_data[k, 2] = shipment_inst.wg
            shipment_data[k, 3] = shipment_inst.load
            shipment_data[k, 4] = shipment_inst.km_d - shipment_inst.km_o
            shipment_data[k, 5] = shipment_inst.npa_o
            shipment_data[k, 6] = shipment_inst.npa_d
            shipment_data[k, 7] = abs(int(shipment_inst.is_first_leg))
            shipment_data[k, 8] = abs(int(shipment_inst.is_last_leg))
            shipment_data[k, 9] = shipment_inst.km_o
            shipment_data[k, 10] = shipment_inst.km_d
            shipment_data[k, 11] = survey_inst.noga
            shipment_data[k, 12] = survey_inst.main_use_goods_transport
            shipment_data[k, 13] = survey_inst.main_use_service
            k = k + 1
    
    
    header = ['oid', 'weight', 'wg', 'load', 'length', 'NPA_O', 'NPA_D', 'IsFirstLeg', 'IsLastLeg', 'km_o', 'km_d', 'noga', 'main_use_goods_transport', 'main_use_service']
    with open('shipments.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f, delimiter = ';', lineterminator='\r')
        writer.writerow(header)
        writer.writerows(shipment_data)
