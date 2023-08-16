class Population:
    def __init__(self):
        self.population=[]
        self.fronts=[]

    def __len__(self):
        return len(self.population)

    def __iter__(self):
        return self.population.__iter__()

    def extend(self, new_individuals):
        # add multiple new individuals into the population
        self.population.extend(new_individuals)

    def append(self, new_individual):
        # add one individual into the population
        self.population.append(new_individual)