#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import csv
import LWE_classes
import processLWE

# Import STATENT
statent=pd.read_csv("data/STATENT_2013_nach_PLZ.csv", sep=";", encoding = "utf-8", index_col=0)
statent.fillna(0, inplace=True)
statent.drop("(vide)", inplace=True)
#print(statent.index.inferred_type)
statent.index=pd.to_numeric(statent.index)
#print(statent.index.dtype)

NPA_list=statent.index.values

# Import & process LWE
LWE_file="data/LWE_2013_TRANSPORT.csv"
survey_dict, summary_statistics=processLWE.get_survey_dict(LWE_file)

# segment names    
segments=['KEP', 'food','other_goods_transporter', 'other_goods_own_vehicle', 'service', 'rest']



hierarchical_indexing=pd.MultiIndex.from_product([segments,['sent', 'received']], names=["segment", "direction"])
individual_shipments_pro_npa=pd.DataFrame(0,columns=NPA_list, index=hierarchical_indexing)
grouped_shipments_pro_npa=pd.DataFrame(0,columns=NPA_list, index=segments) # we only save the sent shipments as we don't know the receiving zones

# compute the number of sent / received shipments pro NPA pro segment
NPA_not_found=[]
non_localized_sent_shipments=0
non_localized_received_shipments=0
for i in survey_dict:
    survey_inst=survey_dict[i]
    # Deal first with all individual shipments
    for shipment_inst in survey_inst.shipment_list:
        # segment definition
        if shipment_inst.wg == 93:
            segment= 'KEP'
        elif shipment_inst.wg in [21,22,81]:
            segment= 'food'
        else:
            if survey_inst.main_use_goods_transport:
                if survey_inst.noga==8:
                    segment= 'other_goods_transporter'
                else:
                    segment= 'other_goods_own_vehicle'
            elif survey_inst.main_use_service:
                segment= 'service'
            else:
                segment = 'rest'
        # add shipment to dataframe
        if shipment_inst.npa_o < 10000: # keep only swiss NPAs
            if shipment_inst.npa_o in NPA_list:
                individual_shipments_pro_npa.at[(segment, 'sent'),shipment_inst.npa_o] += 1 # alt: survey_inst.weight
            else:
                NPA_not_found.append(shipment_inst.npa_o)
                non_localized_sent_shipments+=1 #alt: survey_inst.weight
        if shipment_inst.npa_d < 10000: # keep only swiss NPAs
            if shipment_inst.npa_d in NPA_list:
                individual_shipments_pro_npa.at[(segment,'received'),shipment_inst.npa_d] +=1 # alt: survey_inst.weight
            else:
                NPA_not_found.append(shipment_inst.npa_d)
                non_localized_received_shipments+=1 # alt: survey_inst.weight

    # Second, deal with grouped shipments (those inside simplified tours)
    for simplified_tour_inst in survey_inst.simplified_tour_list:
        # segment definition
        if simplified_tour_inst.wg == 93:
            segment= 'KEP'
        elif simplified_tour_inst.wg in [21,22,81]:
            segment= 'food'
        else:
            if survey_inst.main_use_goods_transport:
                if survey_inst.noga==8:
                    segment= 'other_goods_transporter'
                else:
                    segment= 'other_goods_own_vehicle'
            elif survey_inst.main_use_service:
                segment= 'service'
            else:
                segment = 'rest'
        # add shipment to dataframe
        if simplified_tour_inst.npa_0 < 10000: # keep only swiss NPAs
            if simplified_tour_inst.npa_0 in NPA_list:
                grouped_shipments_pro_npa.at[segment,simplified_tour_inst.npa_0] += simplified_tour_inst.nb_stops # alt : * survey_inst.weight
            else:
                NPA_not_found.append(simplified_tour_inst.npa_0)
                non_localized_sent_shipments+=1 # alt: survey_inst.weight


# remove duplicates
NPA_not_found=list(map(int,set(NPA_not_found)))
NPA_not_found.sort()

individual_shipments_sum=individual_shipments_pro_npa.sum(axis=1)
grouped_shipments_sum=grouped_shipments_pro_npa.sum(axis=1)

## Linear regressions (ou log-linear ou autres, si on veut éviter de générer trop de trajets pour les grosses industries, qui génèrent de toute façon plutôt des trajets avec des gros camions)

# Natural candidates for explanatory variables?

# KEP, sent: NOGA 53 (activité de poste et de courrier) - bemol: les centres de tri auront sûrement beaucoup d'employés mais peu de trajets émis.
# KEP, received: population, nombre d'emplois total

# food, sent : NOGA 10 (industrie alimentaire), 11 (fabrication de boissons), 56 (restauration) 
# food, received: same candidates as for "sent"

# other_goods_transporter, sent: régression multilinéaire ou sur la somme (NOGA A+C+D+E+F+G) ou 
# other_goods_transporter, received:

# other_goods_own_vehicle, sent:
# other_goods_own_vehicle, received:

# service, sent:
# service, received:

# rest, sent:
# rest, received:

