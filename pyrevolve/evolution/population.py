# [(G,P), (G,P), (G,P), (G,P), (G,P)]

from pyrevolve.evolution.individual import Individual
from pyrevolve.SDF.math import Vector3
import time
import asyncio


class PopulationConfig:
    def __init__(self,
                 population_size: int,
                 genotype_constructor,
                 genotype_conf,
                 mutation_operator,
                 mutation_conf,
                 crossover_operator,
                 crossover_conf,
                 selection,
                 parent_selection,
                 population_management,
                 population_management_selector,
                 evaluation_time,
                 experiment_name,
                 exp_management,
                 settings,
                 offspring_size=None,
                 next_robot_id=0):
        """
        Creates a PopulationConfig object that sets the particular configuration for the population

        :param population_size: size of the population
        :param genotype_constructor: class of the genotype used
        :param genotype_conf: configuration for genotype constructor
        :param mutation_operator: operator to be used in mutation
        :param mutation_conf: configuration for mutation operator
        :param crossover_operator: operator to be used in crossover
        :param selection: selection type
        :param parent_selection: selection type during parent selection
        :param population_management: type of population management ie. steady state or generational
        :param offspring_size (optional): size of offspring (for steady state)
        """
        self.population_size = population_size
        self.genotype_constructor = genotype_constructor
        self.genotype_conf = genotype_conf
        self.mutation_operator = mutation_operator
        self.mutation_conf = mutation_conf
        self.crossover_operator = crossover_operator
        self.crossover_conf = crossover_conf
        self.parent_selection = parent_selection
        self.selection = selection
        self.population_management = population_management
        self.population_management_selector = population_management_selector
        self.evaluation_time = evaluation_time
        self.experiment_name = experiment_name
        self.exp_management = exp_management
        self.settings = settings
        self.offspring_size = offspring_size
        self.next_robot_id = next_robot_id

class Population:
    def __init__(self, conf: PopulationConfig, simulator, next_robot_id):
        """
        Creates a Population object that initialises the
        individuals in the population with an empty list
        and stores the configuration of the system to the
        conf variable.

        :param conf: configuration of the system
        :param simulator: connection to the simulator
        """
        self.conf = conf
        self.individuals = []
        self.simulator = simulator
        self.next_robot_id = next_robot_id

    def new_individual(self, genotype):
        individual = Individual(genotype)
        individual.develop()
        self.individuals.append(individual)
        self.conf.exp_management.export_genotype(individual)
        self.conf.exp_management.export_phenotype(individual)
        if self.conf.settings.measure_individuals:
            individual.phenotype.measure_phenotype(self.conf.settings)

    # def list_snapshot_robots(self):


    async def load_pop(self, robots_list):
        #list_snapshot_robots()
        print('fijsnfisd')

    async def init_pop(self):
        """
        Populates the population (individuals list) with Individual objects that contains their respective genotype.
        """
        for i in range(self.conf.population_size):
           self.new_individual(self.conf.genotype_constructor(self.conf.genotype_conf, self.next_robot_id))
           self.next_robot_id += 1
            
        await self.evaluate(self.individuals, 0)

    async def next_gen(self, gen_num):
        """
        Creates next generation of the population through selection, mutation, crossover

        :param gen_num: generation number

        :return: new population
        """

        new_individuals = []

        for _i in range(self.conf.offspring_size):
            # Selection operator (based on fitness)
            # Crossover
            if self.conf.crossover_operator is not None:
                parents = self.conf.parent_selection(self.individuals)
                child = self.conf.crossover_operator(parents, self.conf.crossover_conf, self.next_robot_id)
            else:
                # gotta add next_robot_id to the selection method later!!!!!!
                child = self.conf.selection(self.individuals, self.next_robot_id)
            self.next_robot_id += 1

            # Mutation operator
            child_genotype = self.conf.mutation_operator(child.genotype, self.conf.mutation_conf)
            # Insert individual in new population
            self.new_individual(child_genotype)

        # evaluate new individuals
        await self.evaluate(new_individuals, gen_num)

        # create next population
        if self.conf.population_management_selector is not None:
            new_individuals = self.conf.population_management(self.individuals, new_individuals,
                                                              self.conf.population_management_selector)
        else:
            new_individuals = self.conf.population_management(self.individuals, new_individuals)
        # return self.__class__(self.conf, new_individuals)
        new_population = Population(self.conf, self.simulator, self.next_robot_id)
        new_population.individuals = new_individuals
        return new_population

    async def evaluate(self, new_individuals, gen_num):
        """
        Evaluates each individual in the new gen population

        :param new_individuals: newly created population after an evolution itertation
        :param gen_num: generation number
        """
        # Parse command line / file input arguments
        await self.simulator.pause(True)
        # await self.simulator.reset(rall=True, time_only=False, model_only=False)
        # await asyncio.sleep(2.5)

        for individual in new_individuals:
            print(f'---\nEvaluating individual (gen {gen_num}) {individual.genotype.id} ...')
            await self.evaluate_single_robot(individual)
            print(f'Evaluation complete! Individual {individual.genotype.id} has a fitness of {individual.fitness}.')

    async def evaluate_single_robot(self, individual):

        """
        Evaluate an individual

        :param individual: an individual from the new population
        """
        # Insert the robot in the simulator
        insert_future = await self.simulator.insert_robot(individual.phenotype, Vector3(0, 0, 0.25))
        robot_manager = await insert_future

        # Resume simulation
        await self.simulator.pause(False)

        # Start a run loop to do some stuff
        max_age = self.conf.evaluation_time # + self.conf.warmup_time
        while robot_manager.age() < max_age:
            individual.fitness = robot_manager.fitness()
            await asyncio.sleep(1.0 / 5) # 5= state_update_frequency

        print(robot_manager.sum_of_contacts())

        await self.simulator.pause(True)
        delete_future = await self.simulator.delete_robot(robot_manager)
        await delete_future
        # await self.simulator.reset(rall=True, time_only=False, model_only=False)
