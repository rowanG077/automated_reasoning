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

capacities = [
    250,
    110,
    160,
    110,
    160,
]

num_eval = 10

route_costs = Array('routes', IntSort(), ArraySort(IntSort(), IntSort()))

truck_pos = [Int(f"truck_pos_{i}") for i in range(num_eval)]
truck_store = [Int(f"truck_store_{i}") for i in range(num_eval)]

village_store = [[Int(f"vilage_store_{chr(ord('A') + v)}_{i}") for v in range(num_villages)] for i in range(num_eval)]

def print_solution(model):
    print("cycle, truck pos, truck storage,       A,       B,       C,       D")
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
        
        print(f"{n:5},         {truck_p},       {truck_storage:03}/{truck_cap:03}, {a:03}/{a_cap:03}, {b:03}/{b_cap:03}, {c:03}/{c_cap:03}, {d:03}/{d_cap:03}")

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
        s.add(store_curr - cost >= 0)

        # Ensure we only unload at the current location
        unloaded = store_next - (store_curr - cost)
        s.add(If(
            next_loc == (num_stores + j),
            And(*[unloaded >= 0, unloaded <= curr_truck_store, unloaded <= (capacities[j] - (store_curr + cost))]),
            unloaded == 0
        ))

        unload.append(unloaded)

        # set next store
        s.add(store_next == (store_curr - cost) + unloaded)

    # Remove capacity from truck
    s.add(next_truck_store == curr_truck_store - sum(unload))

res = s.check()
if res == unsat:
    print(f"unsat")
else:
    model = s.model()
    print(f"SAT model:")
    print_solution(model)




