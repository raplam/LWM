#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
 
@dataclass
class SummaryStatistics:
    nb_reconstructed_tours: int=0
    nb_simplified_tours: int=0
    nb_legs: int=0
    nb_shipments: int=0

@dataclass
class SimplifiedTour:
    # Class for describing simplified tours, in the sense of tours for which the LWE data only contains summarizing information (when the tour is too int and in a sufficiently small radius)
    wg: int
    load: int
    km_0: int
    km_1: int
    km_n_1: int
    km_n: int
    npa_0: int
    npa1: int
    npa_n_1: int
    npa_n: int
    nb_stops: int
    is_pickup: bool = False
    is_delivery: bool = False       
 
@dataclass
class ReconstructedTour:
    npa_0: int
    km_total: int
    km_first: int
    km_last: int
    known_stop_list: dict
    nb_unknown_stops: int
   
    def remaining_load(self) -> int:
        stop_inst = self.known_stop_list(self.km_last)
        remaining_load = stop_inst.remaining_load
 
@dataclass
class Leg:
    leg_length: int
    quelle: object
    ziel: object
    load: int
    is_first_leg: bool = False
    is_last_leg: bool = False
    is_intermed_leg: bool = False

# class Leg:
#     def __init__(self,leg_length: int, quelle: object, ziel: object, load: int,
#     is_first_leg: bool, is_last_leg: bool, is_intermed_leg: bool):
#         self.leg_length = leg_length
#         self.quelle = quelle
#         self.ziel = ziel
#         self.load = load
#         self.is_first_leg=is_first_leg
#         self.is_last_leg = is_last_leg
#         self.is_intermed_leg=is_intermed_leg
 
@dataclass
class MyStop:
    def __init__(self, km: int, npa: int):
        self.km=km
        self.npa=npa
        self.wg_list =[]
        self.load = 0
        self.unload = 0
        self.is_tour_start = False
        self.is_tour_end= False
        self.remaining_load= 0
   
    def add_load(self, vdata: int, wg:int):
        self.load += vdata
        if not(wg in self.wg_list):
            self.wg_list.append(wg)
 
    def add_unload(self, vdata: int, wg:int):
        self.unload += vdata
        if not(wg in self.wg_list):
            self.wg_list.append(wg)   
 
@dataclass
class Npa:
    npa: int
    nb_visits: int
    sum_nb_stops_visits: int # sum of the number of known stops of the tours visiting this npa (if the same tour visits this npa twice, it is counted twice)
    sum_loads: int
    sum_unloads: int
    nb_visits_group: dict #  [key=wg]: total number of visits at this npa that either picked up or collected a good of group i
    sum_nb_stops_visits_group: dict # [key=wg]: sum of the number of stops of the tours that either picked up or collected a good of group i at this npa
 
    def add_visit(self, nb_stops: int, stop_inst: MyStop):
        self.nb_visits += 1
        self.sum_nb_stops_visits += nb_stops
        self.sum_loads += stop_inst.load
        self.sum_unloads += stop_inst.unload
        for wg in stop_inst.wg_list:
            if wg in self.nb_visits_group:
                tmp_visits=self.nb_visits_group[wg]
                tmp_stops = self.sum_nb_stops_visits_group[wg]
            else:
                tmp_visits=0
                tmp_stops = 0
            self.nb_visits_group[wg]= tmp_visits+1
            self.sum_nb_stops_visits_group[wg]=tmp_stops+ nb_stops
 
@dataclass
class Shipment:
    wg: int
    load: int
    km_o: int #km of the origin
    km_d: int #km of the destination
    npa_o: int
    npa_d: int
    is_first_leg: bool = False
    is_last_leg: bool = False
   

class Survey:
    # Main class, containing all the others related to a survey (tours, stops, shipments, etc.)
    def __init__(self, oid:  int, weight:  float, strata:  int, main_use_empty_journey: bool, 
                 main_use_goods_transport: bool, main_use_other: bool, main_use_passenger: bool,
                 main_use_private: bool, main_use_rental: bool, main_use_service: bool, curb_weight:  int,
                 load_capa:  int, noga: int):
        self.oid=oid
        self.weight=weight
        self.strata=strata
        self.main_use_empty_journey=main_use_empty_journey
        self.main_use_goods_transport=main_use_goods_transport
        self.main_use_other=main_use_other
        self.main_use_passenger=main_use_passenger
        self.main_use_private=main_use_private
        self.main_use_rental=main_use_rental
        self.main_use_service=main_use_service
        self.curb_weight=curb_weight
        self.load_capa=load_capa
        self.noga=noga
        self.stop_dict={}
        self.leg_list= []
        self.reconstructed_tour_list= []
        self.simplified_tour_list= []
        self.shipment_list= []
        self.sortedkm_list= []

 
    def read_row(self,wg: int, load: int, km_o: int, km_d: int, npa_o: int, npa_d: int, nb_stops: int):
        if nb_stops > 0: # Tour
            # See whether previously read rows qualify to be first or last leg
            is_pick_up= False
            is_delivery = False
            km_0=-1
            km_n=-1
            npa_0=-1
            npa_n=-1
            for shipment_inst in self.shipment_list:
                is_last_leg = False
                is_first_leg = False
                if shipment_inst.wg == wg or (shipment_inst.wg == 1 and shipment_inst.load == 0):
                    if shipment_inst.km_o == km_d:
                        is_last_leg = True
                        if abs(shipment_inst.load / 2 - load) < 1:
                            is_pick_up = True
                    if shipment_inst.km_d == km_o:
                        is_first_leg = True
                        if abs(shipment_inst.load / 2 - load) < 1:
                            is_delivery = True
                    if is_first_leg:
                        shipment_inst.is_first_leg=True
                        km_0 = shipment_inst.km_o
                        npa_0 = shipment_inst.npa_o
                    if is_last_leg:
                        shipment_inst.is_last_leg=True
                        km_n = shipment_inst.km_d
                        npa_n = shipment_inst.npa_d
            # Add: Tour
            simplified_tour_inst=SimplifiedTour(wg, load, km_0, km_o, km_d, km_n, npa_0, npa_o, npa_d, npa_n, nb_stops, is_pick_up, is_delivery)
            self.simplified_tour_list.append(simplified_tour_inst)
            # update stop list (We do not know whether it is a pick up or a delivery => ignore the tour loads inside the tour (not for first and last leg))
            self.__add_stop(km_o, npa_o, 0, 0, True, False, wg)
            self.__add_stop(km_d, npa_d, 0, 0, False, True, wg)
        else:
            is_last_leg = False
            is_first_leg = False
            # See whether this row qualifies to be first or last leg of a previously read tour
            for i in range(0,len(self.simplified_tour_list)):
                tour_inst=self.simplified_tour_list[i]
                if tour_inst.wg == wg or (wg == 1 and load == 0):
                    if tour_inst.km_n_1 == km_o:
                        is_last_leg = True
                        if abs(load / 2 - tour_inst.load) < 1:
                            self.simplified_tour_list[i].is_pick_up = True
                    if tour_inst.km_1 == km_d:
                        is_first_leg = True
                        if abs(load / 2 - tour_inst.load) < 1:
                            self.simplified_tour_list[i].is_delivery = True
                    if is_last_leg:
                        self.simplified_tour_list[i].km_n = km_d
                        self.simplified_tour_list[i].npa_n = npa_d
                    if is_first_leg:
                        self.simplified_tour_list[i].km_0 = km_o
                        self.simplified_tour_list[i].npa_0 = npa_o
            # Add: Shipment
            shipment_inst=Shipment(wg, load, km_o, km_d, npa_o, npa_d, is_first_leg, is_last_leg)
            self.shipment_list.append(shipment_inst)
            # update stop list
            self.__add_stop(km_o, npa_o, load, 0, False, False, wg)
            self.__add_stop(km_d, npa_d, 0, load, False, False, wg)
           
    def max_load(self):
        max_load = 0
        for leg_inst in self.leg_list:
            if leg_inst.load > max_load:
                max_load = leg_inst.load
 
    def dist_travelled(self):
        dist_travelled = self.sortedkm_list[len(self.stop_dict)-1] - self.sortedkm_list[0]
 
    def generate_leg_list(self):
        cum_load = 0
        for i in range(0,len(self.stop_dict) - 1):
            is_first_leg = False
            is_last_leg = False
            is_intermed_leg = False
            quelle = self.stop_dict[self.sortedkm_list[i]]
            ziel = self.stop_dict[self.sortedkm_list[i + 1]]
            cum_load = cum_load - quelle.unload + quelle.load
            quelle.remaining_load = cum_load - quelle.load
            ziel.remaining_load = cum_load - ziel.unload
            if cum_load < 0:
                print("cum_load <0")
            # LegType
            for j in range(0,len(self.simplified_tour_list)):
                if self.simplified_tour_list[j].km_0 == self.sortedkm_list[i] and self.simplified_tour_list[j].km_1 == self.sortedkm_list[i+1]: is_first_leg = True
                if self.simplified_tour_list[j].km_1 == self.sortedkm_list[i] and self.simplified_tour_list[j].km_n_1 == self.sortedkm_list[i+1]: is_intermed_leg = True
                if self.simplified_tour_list[j].km_n_1 == self.sortedkm_list[i] and self.simplified_tour_list[j].km_n == self.sortedkm_list[i+1]: is_last_leg = True
            leg_inst = Leg(self.sortedkm_list[i+1] - self.sortedkm_list[i], quelle, ziel, cum_load, is_first_leg, is_last_leg, is_intermed_leg)
            self.leg_list.append(leg_inst)
 
    def generate_reconstructed_tour_list(self):
    # Might be improved by adding the criterion that no shipment must be over several tours (except perhaps non-marketable ones?)
        index_start = 0
        for i in range(0,len(self.stop_dict)):
            km = self.sortedkm_list[i]
            stop_inst = self.stop_dict[km]
            if index_start == 0:
                npa_0 = stop_inst.npa
                index_start = i
                stop_dict={}
                stop_dict[km]=stop_inst
            else:
                stop_dict[km]=stop_inst # Add it: last stop of previous tour
                if stop_inst.npa == npa_0: #Save self tour and start a new one
                    # count the number of unknown stops (in explicit tours)
                    nb_unknown_stops = 0
                    for j in range(0, len(self.simplified_tour_list)):
                        simplified_tour_inst = self.simplified_tour_list[j]
                        if (simplified_tour_inst.km_1 >= self.sortedkm_list[index_start]) and (simplified_tour_inst.km_n_1 <= self.sortedkm_list[i]):
                            if simplified_tour_inst.nb_stops > 2:
                                nb_unknown_stops = nb_unknown_stops + simplified_tour_inst.nb_stops - 2 #-2: we remove the origin and final destination, which are known stops
                    # Generate an implicit tour and add it to the reconstructed_tour_list
                    reconstructed_tour_inst=ReconstructedTour(npa_0, self.sortedkm_list[i] - self.sortedkm_list[index_start],
                    self.sortedkm_list[index_start], self.sortedkm_list[i], stop_dict, nb_unknown_stops)
                    self.reconstructed_tour_list.append(reconstructed_tour_inst)
                    # Reinitialize the reconstructed_tour_list
                    stop_dict = {}
                    index_start = i
                    stop_dict[km]=stop_inst # Add it again: first stop of next tour
 
    def total_nb_stops(self)-> int:
        total_nb_stops = len(self.stop_dict)
        for i in range(0,len(self.simplified_tour_list)):
            simplified_tour_inst = self.simplified_tour_list[i]
            if simplified_tour_inst.nb_stops > 2:
                total_nb_stops += simplified_tour_inst.nb_stops - 2
   
    def __add_stop(self, km: int, npa: int, load: int, unload: int, is_tour_start: bool, is_tour_end: bool, wg: int):
        this_stop=MyStop(km, npa)
        if not (km in self.stop_dict):
            self.stop_dict[km]=this_stop
            # Update sortedkm_list
            self.sortedkm_list.append(km)
            self.sortedkm_list.sort()
        self.stop_dict[km].add_load(load, wg)
        self.stop_dict[km].add_unload(unload, wg)
        if is_tour_start:
            self.stop_dict[km].is_tour_start= True
        if is_tour_end:
            self.stop_dict[km].is_tour_end = True