from z3 import *
from copy import deepcopy
import sys

num_stores = 1
num_villages = 4

route_costs_list = [
    [-1, 15, -1, 15, -1],
    [15, -1, 17, 12, -1],
    [-1, 17, -1, 10, 20],
    [15, 12, 10, -1, 20],
    [-1, -1, 20, 20, -1],
]

assignment_b = True

capacities = [
    260 if assignment_b else 250,
    110,
    160,
    110,
    160,
]

num_eval = 15 if assignment_b else 31

route_costs = Array('routes', IntSort(), ArraySort(IntSort(), IntSort()))

truck_pos = [Int(f"truck_pos_{i}") for i in range(num_eval)]
truck_store = [Int(f"truck_store_{i}") for i in range(num_eval)]

village_store = [[Int(f"vilage_store_{chr(ord('A') + v)}_{i}") for v in range(num_villages)] for i in range(num_eval)]

if assignment_b:
    world_hunger_save = [[Bool(f"world_hunger_{n1}_{n2}") for n2 in range(n1 + 1, num_eval)] for n1 in range(num_eval)]

def print_solution(model):
    cycle_arrows = ["   " for i in range(num_eval)]

    if assignment_b:
        for n1 in range(num_eval):
            for n2 in range(n1 + 1, num_eval):
                if is_true(model.eval(world_hunger_save[n1][n2 - n1 - 1])):
                    cycle_arrows[n1] = "-->"
                    cycle_arrows[n2] = "-->"

    print("   cycle, truck pos, truck storage,       A,       B,       C,       D")
    for n in range(num_eval):
        truck_p = model[truck_pos[n]].as_long()
        truck_storage = model[truck_store[n]].as_long()
        truck_cap = capacities[0]
        a = model[village_store[n][0]].as_long()
        a_cap = capacities[1] 
        b = model[village_store[n][1]].as_long()
        b_cap = capacities[2] 
        c = model[village_store[n][2]].as_long()
        c_cap = capacities[3]
        d = model[village_store[n][3]].as_long()
        d_cap = capacities[4]
        
        assert(a <= a_cap)
        assert(b <= b_cap)
        assert(c <= c_cap)
        assert(d <= d_cap)
        assert(truck_storage <= truck_cap)
        if n > 0:
            cost = model.eval(route_costs[truck_pos[n-1]][truck_pos[n]]).as_long()
            assert(cost != -1)

        print(f"{cycle_arrows[n]}{n:5},         {truck_p},       {truck_storage:03}/{truck_cap:03}, {a:03}/{a_cap:03}, {b:03}/{b_cap:03}, {c:03}/{c_cap:03}, {d:03}/{d_cap:03}")

s = Solver()

# load routes into Z3 Array
for y in range(num_stores + num_villages):
    for x in range(num_stores + num_villages):
        s.add(route_costs[y][x] == route_costs_list[y][x])

# set initial conditions
s.add(truck_pos[0] == 0)
s.add(truck_store[0] ==  capacities[0])

for v in range(num_villages):
    s.add(village_store[0][v] == 80)

# Run bounded model
for n in range(num_eval - 1):
    curr_loc = truck_pos[n]
    next_loc = truck_pos[n + 1]
    curr_truck_store = truck_store[n]
    next_truck_store = truck_store[n + 1]

    cost = route_costs[curr_loc][next_loc]

    # ensure we take a route that exists
    s.add(And(next_loc >= 0, next_loc < num_stores + num_villages, cost >= 0))

    unload = []

    # unload a negative amount to fill up capacity
    for i in range(num_stores):
        unload.append(If(next_loc == i, curr_truck_store - capacities[i], 0))

    for j in range(num_villages):
        store_curr = village_store[n][j]
        store_next = village_store[n + 1][j]

        # Ensure we don't go through 0 when traveling
        # and ensure we don't store more then possible

        s.add(store_next - cost >= 0)

        # Ensure we only unload at the current location
        unloaded = store_next - (store_curr - cost)
        s.add(If(
            next_loc == (num_stores + j),
            And(unloaded >= 0, unloaded <= curr_truck_store),
            unloaded == 0
        ))

        unload.append(unloaded)

        # set next store
        s.add(store_next <= capacities[num_stores + j])
        s.add(store_next == (store_curr - cost) + unloaded)

    # Remove capacity from truck
    s.add(next_truck_store == curr_truck_store - sum(unload))

# exercise 6b
# check if a storage state is encountered that is strictly
# better then a previous state.
# if that happens we have proven we can just always keep
# using that path and we have solved world hunger
if assignment_b:
    ors = []
    for n1 in range(num_eval):
        for n2 in range(n1 + 1, num_eval):
            ands = []

            ands.append(truck_pos[n1] == truck_pos[n2])
            ands.append(truck_store[n2] >= truck_store[n1])

            for j in range(num_villages):
                ands.append(village_store[n2][j] >= village_store[n1][j])

            world_hunger_save[n1][n2 - n1 - 1] = And(*ands)

            ors.append(world_hunger_save[n1][n2 - n1 - 1])

    s.add(Or(*ors))

res = s.check()
if res == unsat:
    print(f"unsat")
else:
    print(f"SAT")
    print_solution(s.model())




