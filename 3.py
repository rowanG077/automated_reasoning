from z3 import *

num_participants = 10
num_houses = num_participants // 2
num_rounds = 5
num_served_house_per_round = 2

s = Solver()

part_serves_round = [
    [Bool(f"part_{j}_serves_round_{i}") for j in range(num_participants)]
    for i in range(num_rounds)
]

part_dines = [
    [
        [Bool(f"part_{j}_dines_round_{i}_at_house_{k}") for k in range(num_houses)]
        for j in range(num_participants)
    ]
    for i in range(num_rounds)
]

def sum_true(l):
    return sum([If(x, 1, 0) for x in l])

# Ensure that each round people serve
for i in range(num_rounds):
    # ensure the right number of people serve
    s.add(sum_true(part_serves_round[i]) == num_served_house_per_round * 2)

    # ensure couples are matched
    for j in range(0, num_participants, 2):
        s.add(part_serves_round[i][j] == part_serves_round[i][j + 1])

# Ensure the couple that serves a round also dines in its own house
for i in range(num_rounds):
    for j in range(num_participants):
        s.add(Implies(part_serves_round[i][j], part_dines[i][j][j // 2]))

# Ensure every person serves twice
for i in range(num_participants):
    serves_in_round = []
    for j in range(num_rounds):
        serves_in_round.append(part_serves_round[j][i])
    s.add(sum_true(serves_in_round) == 2)

# Ensure participants only eat in houses where food is served
for i in range(0, num_rounds):
    for j in range(num_houses):
        parts_in_houses = []
        for k in range(num_participants):
            parts_in_houses.append(part_dines[i][k][j])

        num_parts_in_houses = sum_true(parts_in_houses)
        s.add(Or(
            num_parts_in_houses == 0,
            num_parts_in_houses == num_participants // 2,
            ))

# Ensure every person has food every round exactly one time
for i in range(num_rounds):
    for j in range(num_participants):
        s.add(sum_true(part_dines[i][j]) == 1)

# Ensure pair of participants meet at most four times
for k1 in range(num_participants):
    for k2 in range(k1 + 1, num_participants):
        meets = []
        for i in range(num_rounds):
            for j in range(num_houses):
                meet = And(part_dines[i][k1][j], part_dines[i][k2][j])
                meets.append(meet)

                # C) Couples never meet outside their own house
                if k1 % 2 == 0 and k2 - k1 == 1:
                    s.add(Implies(
                            meet,
                            part_serves_round[i][k1]))

        num_meets = sum_true(meets)
        s.add(num_meets <= 4)

        # A) Every two people must meet at least once
        #s.add(num_meets >= 1)

        # B) Every two peopple meet at most 3 times
        s.add(num_meets <= 3)


# D) For every house the six guests (3 each time a house serves) are distinct
# This the same as saying: each participant can only eat once in a house it
# doesn't serve in.
for j in range(num_participants):
    for k in range(num_houses):
        part_dines_in_house = []
        for i in range(num_rounds):
            part_dines_in_house.append(part_dines[i][j][k])

        if j // 2 != k:
            s.add(sum_true(part_dines_in_house) <= 1)

def visualise_solution(model):
    print("ROUNDS DISTRIBUTION")
    for i in range(0, num_rounds):
        print(f"round {i}")
        serves = []
        for j in range(num_participants):
           serve = is_true(model[part_serves_round[i][j]])
           if serve:
               serves.append(j)

        print(f"serves: {serves}")

        for j in range(num_houses):
            dines = []
            for k in range(num_participants):
                serve = is_true(model[part_serves_round[i][k]])
                dine = is_true(model[part_dines[i][k][j]])
                if dine:
                    dines.append(k)

            print(f"house {j}: {dines}")

    print("---")
    print("MEET MATRIX")

    meets = [
                [0 for i in range(num_participants)]
            for j in range(num_participants)]
    for k1 in range(num_participants):
        for k2 in range(k1 + 1, num_participants):
            for i in range(num_rounds):
                for j in range(num_houses):
                    a1 = is_true(model[part_dines[i][k1][j]])
                    a2 = is_true(model[part_dines[i][k2][j]])
                    if a1 and a2:
                        meets[k1][k2] += 1

    for i in range(len(meets)):
        print(meets[i])


res = s.check()
if res == unsat:
    print("unsat")
    sys.exit(1)

model = s.model()
visualise_solution(model)
