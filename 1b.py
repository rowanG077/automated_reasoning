from z3 import *
import sys

num_trucks = 8
num_cooled = 3
max_weight = 8000
max_pallets = 8

nuzzle_weight = 700
nuzzle_required = 4 
prittle_weight = 400
skipple_weight = 1000
skipple_required = 8
crottle_weight = 2500
crottle_required = 10
dupple_weight = 200
dupple_required = 20

nuzzles_in_trucks = []
prittles_in_trucks = []
skipples_in_trucks = []
crottles_in_trucks = []
dupples_in_trucks = []

opt = Optimize()

# Generate constraints for every truck
for n in range(num_trucks):
    nuzzle_in_truck = Int(f"nuzzle_in_truck{n}")
    prittle_in_truck = Int(f"prittle_in_truck{n}")
    skipple_in_truck = Int(f"skipple_in_truck{n}")
    crottle_in_truck = Int(f"crottle_in_truck{n}")
    dupple_in_truck = Int(f"dupple_in_truck{n}")
    nuzzles_in_trucks.append(nuzzle_in_truck)
    prittles_in_trucks.append(prittle_in_truck)
    skipples_in_trucks.append(skipple_in_truck)
    crottles_in_trucks.append(crottle_in_truck)
    dupples_in_trucks.append(dupple_in_truck)

    opt.add(nuzzle_in_truck >= 0)
    opt.add(nuzzle_in_truck <= 1)
    opt.add(prittle_in_truck >= 0)
    opt.add(skipple_in_truck >= 0)
    opt.add(crottle_in_truck >= 0)
    opt.add(dupple_in_truck >= 0)

    # explosive mix
    opt.add(Not(And(prittle_in_truck > 0, crottle_in_truck > 0)))

    total_weight = nuzzle_weight * nuzzle_in_truck \
                   + prittle_weight * prittle_in_truck \
                   + skipple_weight * skipple_in_truck \
                   + crottle_weight * crottle_in_truck \
                   + dupple_weight * dupple_in_truck
    
    total_pallets = nuzzle_in_truck \
                    + prittle_in_truck \
                    + skipple_in_truck \
                    + crottle_in_truck \
                    + dupple_in_truck

    opt.add(total_weight >= 0)
    opt.add(total_weight <= max_weight)
    opt.add(total_pallets >= 0)
    opt.add(total_pallets <= max_pallets)

    # The first num_cooled trucks have cooling
    if n >= num_cooled:
        opt.add(skipple_in_truck == 0)

opt.add(sum(nuzzles_in_trucks) == nuzzle_required)
opt.add(sum(skipples_in_trucks) == skipple_required)
opt.add(sum(crottles_in_trucks) == crottle_required)
opt.add(sum(dupples_in_trucks) == dupple_required)
opt.maximize(sum(prittles_in_trucks))

res = opt.check()
if res == unsat:
    print("unsat")
    sys.exit(1)

model = opt.model()
prittles = sum([model[var].as_long() for var in prittles_in_trucks])
print(f"maximum amount of prittles: {prittles}")