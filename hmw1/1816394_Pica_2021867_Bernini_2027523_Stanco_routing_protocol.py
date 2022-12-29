from collections import defaultdict
 
import numpy as np
 
from src.routing_algorithms.BASE_routing import BASE_routing
import random
import src.utilities.utilities as util
 
 
class AIRouting_1816394_Pica_2021867_Bernini_2027523_Stanco(BASE_routing):
    exploration = 0
    exploitation = 0
 
    def __init__(self, drone, simulator):
        BASE_routing.__init__(self, drone, simulator)
        # random generator
        self.rnd_for_routing_ai = np.random.RandomState(self.simulator.seed)
        self.taken_actions = {}  # id event : (old_action)
        self.epsilon = 0.02
        self.n = [0, 0]
        self.q_value = [0, 0]
        self.dictionary = defaultdict(list)  # {id_event : [drones already rewarded]}
        self.expired_packets = defaultdict(list)  # {id_event : [drones that expired packet id_event]}
 
    def feedback(self, drone, id_event, delay, outcome):
        """ return a possible feedback, if the destination drone has received the packet """
        # already feedbacked drones
        if drone in self.dictionary[id_event]:
            return None
 
        if outcome == -1:
            print("Expired packet -> " + str(id_event) + " " + str(drone) + " outcome -> " + str(outcome))
            self.dictionary[id_event].append(drone)
            if drone not in self.expired_packets[id_event]:
                self.expired_packets[id_event].append(drone)
        else:
            print("Delivered packet -> " + str(id_event) + " " + str(drone) + " outcome -> " + str(outcome))
            self.dictionary[id_event].append(drone)
            if drone in self.expired_packets[id_event]:
                self.expired_packets[id_event].remove(drone)
        reward = self.simulator.event_duration - delay
 
        if id_event not in self.taken_actions:
            return None
 
        action = self.taken_actions[id_event]
 
        self.n[action] += 1
 
        self.q_value[action] = self.q_value[action] + ((reward - self.q_value[action])/self.n[action])
 
    def relay_selection(self, opt_neighbors, pkd):
        # now epsilon greedy selection of the action
        # 1) case epsilon, we take a random action
        if random.uniform(0, 1) < self.epsilon:
            action = random.randint(0, 1)
        # 2) case of 1 - epsilon we take the greatest q-value
        else:
            action = np.argmax(self.q_value) # with funcion argmax of numpy we take the max of the q_value array
        # take the action
        self.taken_actions[pkd.event_ref.identifier] = action
        # exploration keep the packet
        if self.taken_actions[pkd.event_ref.identifier] == 1:
            AIRouting_1816394_Pica_2021867_Bernini_2027523_Stanco.exploration += 1
            return None
        # exploitation give the packet with GEO routing and check if packets expired from the drone choose
        else:
            AIRouting_1816394_Pica_2021867_Bernini_2027523_Stanco.exploitation += 1
            drone_to_send = self.ModGeoRouting(opt_neighbors)
 
        return drone_to_send
 
    def print(self):
        """
            This method is called at the end of the simulation, can be usefull to print some
                metrics about the learning process
        """
        print("Which times we got exploration and exploitation?")
        print("Exploration  -> ", AIRouting_1816394_Pica_2021867_Bernini_2027523_Stanco.exploration)
        print("Exploitation -> ", AIRouting_1816394_Pica_2021867_Bernini_2027523_Stanco.exploitation)
 
    def ModGeoRouting(self, opt_neighbors):
        drone_to_send = None
        # check if the drone is near to the depot
        if util.euclidean_distance(self.drone.depot.coords,
                                   self.drone.coords) <= self.simulator.depot_com_range and self.drone not in self.expired_packets:
            return drone_to_send
 
        # GEO Routing with check if this drone is successful
        best_drone_distance_from_depot = util.euclidean_distance(self.simulator.depot.coords, self.drone.coords)
        for hpk, drone_istance in opt_neighbors:
            exp_position = hpk.cur_pos  # without estimation, a simple geographic approach
            exp_distance = util.euclidean_distance(exp_position, self.simulator.depot.coords)
            if not self.expired_packets:
                if exp_distance < best_drone_distance_from_depot:
                    best_drone_distance_from_depot = exp_distance
                    drone_to_send = drone_istance
            else:
                if exp_distance < best_drone_distance_from_depot and drone_istance not in self.expired_packets:
                    best_drone_distance_from_depot = exp_distance
                    drone_to_send = drone_istance
 
        return drone_to_send
