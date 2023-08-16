from utils import NSGA2Utils
from individual import Individual
from population import Population

import time
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
import os
import json
import pickle



class Evolution:

    def __init__(self, problem, node_num, num_of_generations=60, num_of_individuals=200, num_of_tour_particips=2,
                 tournament_prob=0.8, crossover_param=0.8, mutation_param=0.8, input_fn='', fig_path='./output/',save_path='./output',sol={}):
        # print('init Evolution')
        self.utils = NSGA2Utils(problem, num_of_individuals, num_of_tour_particips, tournament_prob, crossover_param,
                                mutation_param)
        self.population = None
        self.node_num = node_num
        self.num_of_generations = num_of_generations
        self.on_generation_finished = []
        self.num_of_individuals = num_of_individuals
        self.fig_path=fig_path
        self.input_fn = input_fn
        self.sol=sol
        self.save_path=save_path


    # calculate the objective function for one specific placement
    def evolve_new_syn(self):
        # calculate the objective function for one specific placement
        solution_obj = {}
        temp=[]
        solution_temp = self.utils.problem.generate_individual_with_positive_nodes(self.sol)
        # print([solution_temp.objectives[0],solution_temp.objectives[1],solution_temp.objectives[2]])
        temp.append([solution_temp.objectives[0], solution_temp.objectives[1], solution_temp.objectives[2]])
        print(temp)

        print(solution_obj)

        save_path = self.save_path
        with open(save_path, 'wb') as f:
            pickle.dump(solution_obj, f)
        return solution_obj


    def evolve_new_single(self):
        # calculate the objective function for one specific placement
        solution_obj = {}
        temp=[]
        solution_temp = self.utils.problem.generate_individual_with_positive_nodes(self.sol)
        # print([solution_temp.objectives[0],solution_temp.objectives[1],solution_temp.objectives[2]])
        temp.append([solution_temp.objectives[0], solution_temp.objectives[1], solution_temp.objectives[2]])
        print(temp)

        print(solution_obj)

    def evolve_new(self):
        # calculate the objective function for one specific placement
        solution_obj={}
        to_cal = ['indegree', 'outdegree','upstream_size', 'closeness_centrality', 'betweenness_centrality','katz_centrality','random']
        #to_cal=['random']
        for x in to_cal:
            temp = []
            for ind in self.sol[x]:
                #print(ind)
                solution_temp= self.utils.problem.generate_individual_with_positive_nodes(ind)
                #print([solution_temp.objectives[0],solution_temp.objectives[1],solution_temp.objectives[2]])
                temp.append([solution_temp.objectives[0],solution_temp.objectives[1],solution_temp.objectives[2]])
                print(temp)

            solution_obj[x]=temp

            print(solution_obj)

        save_path=self.save_path
        with open(save_path, 'wb') as f:
            pickle.dump(solution_obj, f)
        return solution_obj


    # @profile
    def evolve(self):
        # begin=time.time()
        print('begin')
        if self.input_fn == "":
            print('Creating new initial population...')
            self.population = self.utils.create_initial_population_new()   # 初始化加coverage的限制
        else:
            print('Loading existing initial population from...')
            print('   filepath: {}'.format(self.input_fn))
            self.population = self.utils.load_initial_population(self.input_fn, self.node_num) # allows loading existing initialized population
        
        self.utils.fast_nondominated_sort(self.population)

        # first_population=[i.positive_nodes for i in self.population]
        first_population=[[i.objectives[0],i.objectives[1],i.objectives[2],i.positive_nodes] for i in self.population]
        # print(first_population)

        # json_str = json.dumps(first_population)
        fig_path=self.fig_path
        # print(first_population)

        if not os.path.exists(fig_path):
            os.makedirs(fig_path)

        with open(fig_path + '/first_population.pkl', 'wb') as fp:
            pickle.dump(first_population,fp)
            # json_file.write(json_str)

        # print('1st front')
        for front in self.population.fronts:
            # print('calc dis')
            self.utils.calculate_crowding_distance(front)
        # print('create children')
        # print('calc dis done')

        # print('create children')
        children = self.utils.create_children(self.population)   # 生成children时，对coverage加一些限制
        # print('create children finish')

        returned_population = None

        # objective function 1
        goal1_of_all = []
        q1_goal1_of_all=[]
        q2_goal1_of_all = []
        q3_goal1_of_all = []
        # objective function 2
        goal2_of_all = []
        q1_goal2_of_all = []
        q2_goal2_of_all = []
        q3_goal2_of_all = []
        # objective function 3
        goal3_of_all = []
        q1_goal3_of_all = []
        q2_goal3_of_all = []
        q3_goal3_of_all = []

        # objective function 1 的 front 0
        goal1_front_of_all = []
        q1_goal1_front_of_all=[]   # 25%
        q2_goal1_front_of_all = []  # 50%
        q3_goal1_front_of_all=[]    # 75%
        # objective function 2 的 front 0
        goal2_front_of_all = []
        q1_goal2_front_of_all = []
        q2_goal2_front_of_all = []
        q3_goal2_front_of_all = []
        # objective function 3 的 front 0
        goal3_front_of_all = []
        q1_goal3_front_of_all = []
        q2_goal3_front_of_all = []
        q3_goal3_front_of_all = []

        # front 0 的占比
        front_percent = []
        solutions_dict={}
        population_dict={}

        print('num_of_individials',self.num_of_individuals)
        print('initial front 0',len(self.population.fronts[0]) / self.num_of_individuals)
        # add first popu in record, only record the first front
        front_percent.append(len(self.population.fronts[0]) / self.num_of_individuals)
        # solutions_dict[0] = [[i.objectives[0],i.objectives[1],i.objectives[2],i.positive_nodes] for i in self.population.fronts[0]]
        # population_dict[0]=[[i.objectives[0],i.objectives[1],i.objectives[2],i.positive_nodes] for i in self.population]
        
    
        if not os.path.exists(fig_path):
            os.makedirs(fig_path)
        # print(fig_path)
        
        # start iterations
        # t = tqdm(range(1, self.num_of_generations+1))  # gen0 is init popu
        t = range(self.num_of_generations)
        for i in t:
            print(i)
            # begin_generate = time.time()
            # print('extend children')
            self.population.extend(children)
            print('population size',len(self.population))
            self.population=self.utils.duplication_elimination(self.population)
            print('population size after duplication elimination',len(self.population))

            self.utils.fast_nondominated_sort(self.population)
            # begin_new_pop = time.time()
            new_population = Population()
            front_num = 0

            while len(new_population) + len(self.population.fronts[front_num]) <= self.num_of_individuals:
                self.utils.calculate_crowding_distance(self.population.fronts[front_num])
                new_population.extend(self.population.fronts[front_num])
                front_num += 1

            self.utils.calculate_crowding_distance(self.population.fronts[front_num])
            self.population.fronts[front_num].sort(key=lambda individual: individual.crowding_distance, reverse=True)
            new_population.extend(self.population.fronts[front_num][0:self.num_of_individuals - len(new_population)])
            returned_population = self.population
            self.population = new_population
            # end_new_pop = time.time()

            self.utils.fast_nondominated_sort(self.population)

            # front_sort_begin = time.time()

            for front in self.population.fronts:
                self.utils.calculate_crowding_distance(front)

            children = self.utils.create_children(self.population)
            
            # end_generate = time.time()
            # print( str(i)+"th "+"generation time: " + str(end_generate - begin_generate))
           
            #t.set_description('{0:3d} th Generation of '.format(i) + str(self.num_of_generations))   ## open with tqdm


            total_val1=[i.objectives[0] for i in self.population]
            total_val2 = [-i.objectives[1] for i in self.population]
            total_val3 = [i.objectives[2] for i in self.population]
            # print(total_val3)


            front_val1=[i.objectives[0] for i in self.population.fronts[0]]
            front_val2 = [-i.objectives[1] for i in self.population.fronts[0]]
            front_val3 = [i.objectives[2] for i in self.population.fronts[0]]

            goal1_front_of_all.append(np.mean(front_val1))  #平均值作为converge的衡量标准
            q1_goal1_front_of_all.append(np.percentile(front_val1,25))
            q2_goal1_front_of_all.append(np.percentile(front_val1, 50))
            q3_goal1_front_of_all.append(np.percentile(front_val1, 75))
            goal2_front_of_all.append(np.average(front_val2))
            q1_goal2_front_of_all.append(np.percentile(front_val2, 25))
            q2_goal2_front_of_all.append(np.percentile(front_val2, 50))
            q3_goal2_front_of_all.append(np.percentile(front_val2, 75))
            goal3_front_of_all.append(np.average(front_val3))
            q1_goal3_front_of_all.append(np.percentile(front_val3, 25))
            q2_goal3_front_of_all.append(np.percentile(front_val3, 50))
            q3_goal3_front_of_all.append(np.percentile(front_val3, 75))

            goal1_of_all.append(np.mean(total_val1))
            q1_goal1_of_all.append(np.percentile(total_val1,25))
            q2_goal1_of_all.append(np.percentile(total_val1, 50))
            q3_goal1_of_all.append(np.percentile(total_val1, 75))
            goal2_of_all.append(np.mean(total_val2))
            q1_goal2_of_all.append(np.percentile(total_val2, 25))
            q2_goal2_of_all.append(np.percentile(total_val2, 50))
            q3_goal2_of_all.append(np.percentile(total_val2, 75))
            goal3_of_all.append(np.mean(total_val3))
            q1_goal3_of_all.append(np.percentile(total_val3, 25))
            q2_goal3_of_all.append(np.percentile(total_val3, 50))
            q3_goal3_of_all.append(np.percentile(total_val3, 75))
            # print(goal3_of_all)

            front_percent.append(len(self.population.fronts[0]) / self.num_of_individuals)
            solutions_dict[i]=[[i.objectives[0],i.objectives[1],i.objectives[2],i.positive_nodes] for i in self.population.fronts[0]]
            population_dict[i]=[[i.objectives[0],i.objectives[1],i.objectives[2],i.positive_nodes] for i in self.population]

            # if i%100:
            #     with open(fig_path + '/solution.pkl', 'ab') as f:
            #         pickle.dump(solutions_dict, f)
            #
            #     with open(fig_path + '/population.pkl', 'ab') as f:
            #         pickle.dump(population_dict, f)

        plt.figure(figsize=(50, 20))
        print(front_percent)

        ax = plt.subplot(2, 4, 1)
        ax.set_title('Avg Sensor Num in Whole Population', fontsize=20)
        # ax.scatter(range(self.num_of_generations), goal1_of_all, s=6)
        ax.plot(range(self.num_of_generations), goal1_of_all)
        ax.fill_between(range(self.num_of_generations), q3_goal1_of_all,q1_goal1_of_all, alpha=0.2)
        ax.fill_between(range(self.num_of_generations), q3_goal1_of_all, q2_goal1_of_all, alpha=0.2,color='y')

        ax=plt.subplot(2, 4, 2)
        ax.set_title('Avg Coverage in Whole Population', fontsize=20)
        # ax.scatter(range(self.num_of_generations), goal2_of_all, s=6)
        ax.plot(range(self.num_of_generations), goal2_of_all)
        ax.fill_between(range(self.num_of_generations), q3_goal2_of_all, q1_goal2_of_all, alpha=0.2)
        ax.fill_between(range(self.num_of_generations), q3_goal2_of_all, q2_goal2_of_all, alpha=0.2, color='y')

        ax=plt.subplot(2, 4, 3)
        ax.set_title('Avg Search Cost in Whole Population', fontsize=20)
        # ax.scatter(range(self.num_of_generations), goal3_of_all, s=6)
        ax.plot(range(self.num_of_generations), goal3_of_all)
        ax.fill_between(range(self.num_of_generations), q3_goal3_of_all, q1_goal3_of_all, alpha=0.2)
        ax.fill_between(range(self.num_of_generations), q3_goal3_of_all, q2_goal3_of_all, alpha=0.2, color='y')


        ax=plt.subplot(2, 4, 4)
        ax.set_title('%of Front 0 in Whole (including initial front 0)', fontsize=20)
        # ax.scatter(range(self.num_of_generations), front_percent, s=6)
        ax.plot(range(self.num_of_generations+1),front_percent)


        # plt.figure(figsize=(15, 5))
        ax=plt.subplot(2, 4, 5)
        ax.set_title('Avg Sensor Num in Front 0', fontsize=20)
        # ax.scatter(range(self.num_of_generations), goal1_front_of_all, s=6)
        ax.plot(range(self.num_of_generations), goal1_front_of_all)
        ax.fill_between(range(self.num_of_generations), q3_goal1_front_of_all, q1_goal1_front_of_all, alpha=0.2)
        ax.fill_between(range(self.num_of_generations), q3_goal1_front_of_all, q2_goal1_front_of_all, alpha=0.2, color='y')

        ax=plt.subplot(2, 4, 6)
        ax.set_title('Avg Coverage in Front 0', fontsize=20)
        # ax.scatter(range(self.num_of_generations), goal2_front_of_all, s=6)
        ax.plot(range(self.num_of_generations), goal2_front_of_all)
        # ax.plot(range(self.num_of_generations),q1_goal2_front_of_all,color='r')
        # ax.plot(range(self.num_of_generations), q3_goal2_front_of_all, color='y')
        ax.fill_between(range(self.num_of_generations), q3_goal2_front_of_all, q1_goal2_front_of_all, alpha=0.2,color='C0')
        ax.fill_between(range(self.num_of_generations), q3_goal2_front_of_all, q2_goal2_front_of_all, alpha=0.2,
                        color='y')

        ax=plt.subplot(2, 4, 7)
        ax.set_title('Avg Search Cost in Front 0', fontsize=20)
        # ax.scatter(range(self.num_of_generations), goal3_front_of_all, s=6)
        ax.plot(range(self.num_of_generations), goal3_front_of_all)
        ax.fill_between(range(self.num_of_generations), q3_goal3_front_of_all, q1_goal3_front_of_all, alpha=0.2)
        ax.fill_between(range(self.num_of_generations), q3_goal3_front_of_all, q2_goal3_front_of_all, alpha=0.2,
                        color='y')


        plt.savefig(fig_path+'/75-50-25.png')
        # plt.show()
        with open(fig_path+'/solution.pkl', 'ab') as f:
            pickle.dump(solutions_dict, f)

        with open(fig_path+'/population.pkl', 'ab') as f:
            pickle.dump(population_dict, f)


        print('len of total population:',len(self.population.population))
        print('number of fronts:', len(self.population.fronts))
        print('len of front 0:',len(self.population.fronts[0]))

        return returned_population.fronts[0]
