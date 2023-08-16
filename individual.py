import numpy as np
import random

class Individual(object):
    def __init__(self,chromosome_length):
        self.rank = None
        self.crowding_distance = None
        self.domination_count = None
        self.dominated_solutions = None
        self.objectives = None
        self.Gsub=None
        self.chromosome_length=chromosome_length
        self.chromosome = np.zeros(chromosome_length,int)
        self.positive_nodes=[]
        self.coverage_set=set()
        self.sub_conn=[]


    def __eq__(self, other):
        if isinstance(self, other.__class__):
            # return self.features==other.features
            return all(self.chromosome == other.chromosome)
        return False

    def dominates(self, other_individual):
        and_condition = True
        or_condition = False
        for first, second in zip(self.objectives, other_individual.objectives):
            #  if self dominates other_individual
            and_condition = and_condition and first <= second
            # for all indicators k, k(self)<=k(other_individual)
            or_condition = or_condition or first < second
            # for at least one indicator k, k(self)<k(other_individual)

        return (and_condition and or_condition)

    # @profile
    def upbound_constraint(self,sensor_upbound,pos_num):

        flip_num=pos_num-sensor_upbound

        self.positive_nodes=np.array(np.where(self.chromosome==1))[0].tolist()
        
        flip_index=np.random.choice(self.positive_nodes,flip_num,replace=False)

        for i in flip_index:
            self.chromosome[i] = 0
        self.positive_nodes = [i for i, x in enumerate(self.chromosome) if x == 1]
