import json
import cpmpy as cp
from itertools import product
from collections import defaultdict

class var:
    def __init__(self, values):
        self.idFromStr = {s : i for i, s in enumerate(values)}
        self.strFromId = {i : s for i, s in enumerate(values)}
        self.ids = range(len(values))
        self.values = list(values)

        print(values)

    @property
    def all(self):
        return self.ids

    @property
    def allNames(self):
        return self.values

    @property
    def n(self):
        return len(self.values)

    def toId(self, name):
        return self.idFromStr[name]
    
    def toName(self, id):
        return self.strFromId[id]

def getAvailabilityDict(rotaData, names, dates):
    result = defaultdict(dict)
    for name, data in rotaData["Volunteers"].items():
        for date in dates.all:
            result[names.toId(name)][date] = dates.toName(date) in data["Availability"]
    return result
    
def getRolesDict(rotaData, names, roles):
    result = defaultdict(dict)
    for name, data in rotaData["Volunteers"].items():
        for role in roles.all:
            result[names.toId(name)][role] = roles.toName(role) in data["Roles"]
    return result

def score(shifts, names, roles, dates):
    scale_factor = 10
    total_per_person = [cp.sum(cp.sum(shifts[(n, r, d)] for r in roles.all) for d in dates.all) for n in names.all]
    mean_shifts = cp.sum(total_per_person) * scale_factor // names.n
    dist_from_mean = [(n * scale_factor) - mean_shifts for n in total_per_person]
    dist_from_mean = [d *d for d in dist_from_mean]
    var = cp.sum(dist_from_mean) // names.n
    return var

def printResult(shifts, names, roles, dates):
    print(" ".join(dates.allNames))
    for r in roles.all:
        line = [roles.toName(r)]
        for d in dates.all:
            for n in names.all:
                if shifts[(n, r, d)].value() == 1:
                    line.append(names.toName(n))
                    break
        print(" ".join(line))

def count(shifts, names, roles, dates):
    result = defaultdict(int)
    for n, r, d in product(names.all, roles.all, dates.all):
        result[names.toName(n)] += shifts[(n,r,d)].value()
    return result

class rotaSolver:
    def __init__(self, names, roles, dates):
        self.names = var(names)
        self.roles = var(roles)
        self.dates = var(dates)
        # Setup decisison variables
        # boolean, person n, works role r, on date d
        self.shifts = {}
        for n, r, d in product(self.names.all, self.roles.all, self.dates.all):
            self.shifts[(n, r, d)] = cp.boolvar(name=f"shift_n{n}_r{r}_d{d})]")

        # Create Model
        self.model = cp.Model()

    def setupBasicConstraints(self):
        # Each shift is assigned to one person
        for r, d in product(self.roles.all, self.dates.all):
            self.model += cp.sum(self.shifts[(n, r, d)] for n in self.names.all) == 1

        # Each person fills one role on a given date
        for n, d in product(self.names.all, self.dates.all):
            self.model += cp.sum(self.shifts[(n, r, d)] for r in self.roles.all) <= 1

    def addAvailability(self, availabilityMap):
        for n, r, d in product(self.names.all, self.roles.all, self.dates.all):
            self.model += self.shifts[(n, r, d)] <= availabilityMap[n][d]

    def addRoleAllocations(self, roleMap):
        for n, r, d in product(self.names.all, self.roles.all, self.dates.all):
            self.model += self.shifts[(n, r, d)] <= roleMap[n][r]

    def objectiveFunction(self):
        scale_factor = 10
        total_per_person = [cp.sum( cp.sum(self.shifts[(n, r, d)] for r in self.roles.all) 
                                                                  for d in self.dates.all)
                                                                  for n in self.names.all]
        mean_shifts = cp.sum(total_per_person) * scale_factor // self.names.n
        dist_from_mean = [(n * scale_factor) - mean_shifts for n in total_per_person]
        dist_from_mean = [d * d for d in dist_from_mean]
        var = cp.sum(dist_from_mean) // self.names.n
        return var

    def solve(self):
        self.model.minimize(self.objectiveFunction())

        return self.model.solve()

    def print(self):
        print("Status:", self.model.status())
    
        # Print result
        if success:
            print("Objective value:", self.model.objective_value())
            printResult(self.shifts, self.names, self.roles, self.dates)
            print(count(self.shifts, self.names, self.roles, self.dates))
        else:
            print("Failed to obtain result")


if __name__ == "__main__":
    with open('example.rota', 'r') as rotaFile:
        rotaData = json.load(rotaFile)

    names = var(rotaData["Volunteers"].keys())
    dates = var(rotaData["Dates"])
    roles = var(rotaData["Roles"])
    print(names.values)
    print(names.strFromId)
    print(dates.strFromId)
    print(roles.strFromId)

    rs = rotaSolver(rotaData["Volunteers"].keys(),
                    rotaData["Roles"],
                    rotaData["Dates"])

    rs.setupBasicConstraints()

    availability = getAvailabilityDict(rotaData, names, dates)
    rs.addAvailability(availability) 

    roleDict = getRolesDict(rotaData, names, roles)
    rs.addRoleAllocations(roleDict) 

    success = rs.solve()
    rs.print()


