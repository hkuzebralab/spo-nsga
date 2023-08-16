# from nsga.population import Population
from individual import Individual
from population import Population
import random
import time
import numpy as np
import pickle as pk
# from nsga import topology



class NSGA2Utils:

    def __init__(self, problem, num_of_individuals,
                 num_of_tour_particips, tournament_prob, crossover_param, mutation_param):
        self.problem = problem
        self.num_of_individuals = num_of_individuals
        self.num_of_tour_particips = num_of_tour_particips
        self.tournament_prob = tournament_prob
        self.crossover_param = crossover_param
        self.mutation_param = mutation_param
        # self.node_num=problem.node_num


    def _choose_with_prob(self, prob):
        if random.random() <= prob:
            return True
        return False


    def _tournament(self, population):

        front_num=len(population.fronts)
        pool=[]
        for i in range(int(front_num/2)):
            pool.extend(population.fronts[i])

        # participants = random.sample(population.population[0:int(len(population.population)/2)], self.num_of_tour_particips)
        participants=random.sample(pool,self.num_of_tour_particips)

        best = None

        for participant in participants:
            if best is None or (
                        self.crowding_operator(participant, best) == 1 ):
                best = participant

        return best

    # @profile
    def create_initial_population(self):
    # 初始不加限制
        population = Population()
        for i in range(self.num_of_individuals):
            # print(i,'th individual')
            individual = self.problem.generate_individual()
            self.problem.calculate_objectives(individual)
            population.append(individual)
        return population


    def load_initial_population(self, input_fn, node_num):
        with open(input_fn, 'rb') as f:
            population_data = pk.load(f)  
            
        # list to population object
        population = Population()
        for p in population_data:
            individual=Individual(node_num)
            
            positive_nodes = p[3]
            individual.positive_nodes=positive_nodes
            
            for i in positive_nodes:
                individual.chromosome[i]=1
            self.problem.calculate_objectives(individual)
            
            population.append(individual)

        return population


    def create_initial_population_new(self):
        # 初始化individual加一些限制
        population = Population()
        count=0
        constrained_coverage = self.problem.node_num * self.problem.coverage_constrain
        while count < self.num_of_individuals:
            individual = self.problem.generate_individual()
            self.problem.calculate_objectives(individual)
            if np.abs(individual.objectives[1])>constrained_coverage:
                population.append(individual)
                count+=1
        return population


    def fast_nondominated_sort(self, population):
        #start = time.time()
        population.fronts = [[]]
        for individual in population:
            individual.domination_count = 0
            individual.dominated_solutions = []
            for other_individual in population:
                if individual.dominates(other_individual):
                    individual.dominated_solutions.append(other_individual)
                elif other_individual.dominates(individual):
                    individual.domination_count += 1

            if individual.domination_count == 0:
                individual.rank = 0
                population.fronts[0].append(individual)
        i = 0
        while len(population.fronts[i]) > 0:
            # print('loop')
            temp = []
            for individual in population.fronts[i]:
                for other_individual in individual.dominated_solutions:
                    other_individual.domination_count -= 1
                    if other_individual.domination_count == 0:
                        other_individual.rank = i + 1
                        temp.append(other_individual)
            i = i + 1
            population.fronts.append(temp)
        #end = time.time()
        #print('\n' + 'Fast Nondominated Sorting Time: %fs' % (end - start))

    def calculate_crowding_distance(self, front):

        if len(front) > 0:
            solutions_num = len(front)
            for individual in front:
                individual.crowding_distance = 0

            for m in range(len(front[0].objectives)):
                # print(front[0].objectives)
                front.sort(key=lambda individual: individual.objectives[m])
                front[0].crowding_distance = 10 ^ 9
                front[solutions_num - 1].crowding_distance = 10 ^ 9
                m_values = [individual.objectives[m] for individual in front]
                scale = max(m_values) - min(m_values)
                if scale == 0:
                    scale = 1
                for i in range(1, solutions_num - 1):
                    front[i].crowding_distance += (front[i + 1].objectives[m] - front[i - 1].objectives[m]) / scale


    def crowding_operator(self, individual, other_individual):
        if (individual.rank < other_individual.rank) or ((
                                                                 individual.rank == other_individual.rank) and individual.crowding_distance > other_individual.crowding_distance):
            return 1
        else:
            return -1

    # @profile
    def create_children(self, population):
        # print('create children')

        children = []
        constrained_coverage=self.problem.node_num*self.problem.coverage_constrain

        while len(children) < len(population):  # 得到一个和population一样大小的children的解
            # print('more children')
            parent1 = self._tournament(population)
            parent2 = self._tournament(population)

            # while parent1.chromosome == parent2.chromosome:
            while parent1 == parent2:
                parent2 = self._tournament(population)
                
            r = random.random()
            if r < self.crossover_param:
                child1, child2 = self._crossover(parent1, parent2)
            else:
                child1 = self.problem.generate_individual_with(parent1)
                child2 = self.problem.generate_individual_with(parent2)
                self._mutate(child1)
                self._mutate(child2)
            
            # check and fix sensor upbound
            sensor_upbound = self.problem.sensor_upbound
            # sensor_lowerbound=20

            pos_num1 = np.sum(child1.chromosome)
            if pos_num1>sensor_upbound:
                child1.upbound_constraint(sensor_upbound, pos_num1)

            pos_num2 = np.sum(child2.chromosome)
            if pos_num2 > sensor_upbound:
                child2.upbound_constraint(sensor_upbound, pos_num2)
          
            self.problem.calculate_objectives(child1)
            self.problem.calculate_objectives(child2)
            
            # coverage lowerbound
            if np.abs(child1.objectives[1])>constrained_coverage:
                children.append(child1)

            # if np.abs(child2.objectives[1])>0.5*len(child1.chromosome):
            if np.abs(child2.objectives[1]) > constrained_coverage:
                children.append(child2)

        return children


    def _crossover(self, individual1, individual2):
        child1 = self.problem.generate_individual_with(individual1)
        child2 = self.problem.generate_individual_with(individual2)

        # Assume that there is only one feature
        # single-point crossover
        # node_num = len(child1.chromosome)

        # p = random.randint(1, node_num)
        p=random.randint(1,self.problem.node_num)
        child1.chromosome[p:] = child2.chromosome[p:]
        child2.chromosome[0:p] = child1.chromosome[0:p]
        # child1.positive_nodes = [i for i, x in enumerate(child1.chromosome) if x == 1]
        # child2.positive_nodes = [i for i, x in enumerate(child2.chromosome) if x == 1]

        return child1, child2


    def _mutate(self, child):

        # Assume that there is only one feature, which is a 1*n vector representing
        # whether we put a sensor on the edges
        # 0 - no sensor / 1 - put a sensor
        
        # chromosome_length = len(child.chromosome)
        # arr = np.random.rand(chromosome_length)
        
        ## arr = np.random.rand(self.problem.node_num)
        ## index_list=np.array(np.where(arr<self.mutation_param))[0].tolist()
        # self.positive_nodes = np.array(np.where(self.chromosome == 1))[0].tolist()
        # print(len(index_list))

        flip_count = int(self.problem.node_num*self.mutation_param)
        index_list = random.sample(range(self.problem.node_num), flip_count)
        for i in index_list:
            child.chromosome[i] = 1 - child.chromosome[i]


    def duplication_elimination(self,population):
        individual_no_duplication=Population()   # 而不是空的list
        for individual in population:
            if individual not in individual_no_duplication:
                individual_no_duplication.append(individual)
        return individual_no_duplication


