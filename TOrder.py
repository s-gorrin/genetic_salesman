"""
TERMS:
route:  a relative route where each step is the nth-nearest city from the current
path:   a list of cities, by name, which can be generated from a route, wherein
                each path starts and ends with the first city in the list
"""

import random
import time


# a genetic algorithm implementation for a traveling salesman problem
class TOrder:

    population_size = 450
    SAMPLE_SIZE = 0.3
    MUTATION_RATE = 500  # lower == more often

    # to preserve the order of cities
    cities = []

    # for reference and calculating value (in whole miles)
    distances = {}

    # to convert cities to indices in cities/distances
    # this is redundant, but it's faster than calling cities.index() a bunch of times
    lookup = {}

    # for use in routes, filled by generate_proximity_table()
    proximity = {}

    routes = []

    def __init__(self, filename):
        self.cities_from_file(filename)
        self.num_cities = len(self.cities)
        self.population_size = (self.num_cities * 100) // 2  # this is somewhat arbitrary but seems reasonable
        self.route_len = self.num_cities - 2  # the last city does not get a choice
        # set up random population of routes
        for r in range(self.population_size):
            if 0 < r < self.num_cities:
                route = [r] * self.route_len  # add some constant routes to the gene pool
            else:
                route = []
                for i in range(self.route_len):
                    route.append(random.randint(1, self.route_len))  # randint is [start, end]
            self.routes.append(route)
        self.generate_lookup_table()
        self.generate_proximity_table()

    def cities_from_file(self, filename):
        """
        read a city file and populate the cities list and distances table from it
        """
        try:
            with open(filename, 'r') as city_file:
                # fill the cities list with the proper city order
                self.cities = city_file.readline()[:-1].split(sep=',')[1:]

                # fill the distances table from the file
                for line in city_file.readlines():
                    city = line[:-1].split(sep=',')
                    self.distances[city[0]] = [int(d) for d in city[1:]]
        except FileNotFoundError:
            print("That filename appears to be incorrect.")
            exit()

    def generate_proximity_table(self):
        """
        generate a proximity table from the existing city distance table

        procedure:
        create a dict of distances with cities as keys
            sort the keys
            take the sorted key list and generate a list of values in that order
                for key in keys.sorted(): prox.append(dict[key])
            replace that city's proximity list with the new list
            done
        """
        # for each city...
        for city in self.distances.keys():
            pro_dict = {}
            for i in range(len(self.distances[city])):
                pro_dict[self.distances[city][i]] = self.cities[i]
            order = list(pro_dict.keys())
            order.sort()
            cities_in_order = [pro_dict[d] for d in order]
            self.proximity[city] = cities_in_order

    def generate_lookup_table(self):
        for i in range(len(self.cities)):
            self.lookup[self.cities[i]] = i

    def decode_route(self, route):
        """
        convert a relative-distance route to an absolute city path

        each route starts at Boston and each member n is the nth nearest city
        if the nth nearist city is already included, try to get closer first, then further
        """
        path = [self.cities[0]]
        for p in route:
            # try to add by absolute proximity first
            if self.proximity[path[-1]][p] not in path:
                path.append(self.proximity[path[-1]][p])
            else:
                # generate a list of available cities
                available = [c for c in self.proximity[path[-1]] if c not in path]
                # if the p-proximal city is available, use it
                if p < len(available):
                    path.append(available[p])
                # if not, use the last city
                else:
                    path.append(available[-1])
        for letter in self.lookup.keys():
            if letter not in path:
                path.append(letter)
                break
        return path

    def city_distance(self, first, second):
        """
        first and second are cities in the tables

        return the distance between the two cities
        """
        # this does not need to be a method, but it makes the code cleaner
        return self.distances[first][self.lookup[second]]

    def route_distance(self, route):
        """
        Evaluation Function

        measure the full distance of a route, from start back to start
        """
        # first convert the relative route to an absolute path of cities
        path = self.decode_route(route)
        total_dist = 0
        for i in range(len(path) - 1):
            total_dist += self.city_distance(path[i], path[i + 1])
        return total_dist + self.city_distance(path[-1], path[0])

    def get_parents(self):
        """
        get a sample of the population (20%) and try to select parents from the best half
        """
        sample = random.sample(self.routes, int(self.population_size * self.SAMPLE_SIZE))
        values = [self.route_distance(r) for r in sample]  # this part is gonna be slow ¯\_(ツ)_/¯
        num_parents = len(sample) // 2
        max_val, min_val = max(values), min(values)
        parents = []
        r = 0  # the index of a route
        assert(len(values) == len(sample))

        # track tries so that after a certain number, we can just fill the container
        # because filling a container randomly might never end
        tries = 0
        # collect parents, attempting to get lower values
        while len(parents) < num_parents:
            tries += 1
            if values[r] < random.uniform(min_val, max_val):  # this can hang
                parents.append(sample[r])
            elif tries > self.population_size:  # arbitrary but scaled
                lowest = values.index(min_val)  # may result in duplicates, but so can other methods
                parents.append(sample[lowest])  # replace with min of the dataset
                tries //= 2  # reduce try count but not a full reset
            # keep looping through sample until enough parents are found
            r += 1
            if r == len(sample):
                r = 0

        return parents

    def mate(self, parents):
        """
        make a list of children from a list of parents, one child per parent

        every child has a 1/1000 chance of mutating, the selector of which is randomly chosen each generation
        """
        mutate_number = random.randint(1, self.MUTATION_RATE)
        crossover = random.randint(1, self.route_len - 1)  # [1, 4]
        children = []
        for a in parents:
            # this is a bit ugly, but it is the best I've got
            b = a
            tries = 0
            while b == a:
                b = random.choice(parents)  # this can hang
                tries += 1
                if tries > self.population_size:
                    rand_parents = parents.copy()
                    random.shuffle(rand_parents)
                    if a == rand_parents[0]:
                        b = rand_parents[1]
                    else:
                        b = rand_parents[0]
                    break

            child = a[:crossover] + b[crossover:]
            if random.randint(1, self.MUTATION_RATE) == mutate_number:
                child[crossover], child[crossover - 1] = child[crossover - 1], child[crossover]
            children.append(child)
        return children

    def next_generation(self, children):
        """
        randomly remove len(children) of the population to make room for the children
        then add the children
        """
        self.routes = random.sample(self.routes, len(self.routes) - len(children)) + children

    def path_string(self, path):
        """
        get a nice string representation of a path
        """
        ps = ""
        for c in path:
            ps += c + " -> "
        return ps + self.cities[0]

    def run(self, generations, timeout=60):
        """
        run the genetic algorithm to find a good route

        generations is a positive integer, the number of cycles to run
        if taking too long, stop after timeout seconds

        return the best route at the end of the run, its path, and its distance
        """
        start = time.time()

        while generations > 0 and time.time() - start < timeout:
            parents = self.get_parents()
            children = self.mate(parents)
            self.next_generation(children)
            generations -= 1

        if generations > 0:
            print(f"timed out after {timeout} seconds")

        best_route = min(self.routes, key=lambda x: self.route_distance(x))
        return best_route, self.decode_route(best_route), self.route_distance(best_route)
