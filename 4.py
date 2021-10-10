from z3 import *

num_loops = 10

a_l = [Int(f"a_{i}") for i in range(num_loops + 1)]
b_l = [Int(f"b_{i}") for i in range(num_loops + 1)]
checks = [Bool(f"check_{i}") for i in range(num_loops)]

def run(model, n):
    a = 1
    b = 1
    for i in range(1, num_loops + 1):
        j = i - 1
        if is_true(model[checks[j]]):
            a = a + 2 * b
            b = b + i
        else:
            b = a + b
            a = a + i
    
    if b == 700 + n:
        print(f"crash: b is {b}")
    else:
        print(f"no crash: b is {b}")


for n in range(1, 11):
    s = Solver()

    # initial conditions
    s.add(a_l[0] == 1)
    s.add(b_l[0] == 1)

    for i in range(1, num_loops + 1):
        j = i - 1

        a_l[i] = If(checks[j], a_l[j] + 2 * b_l[j], a_l[j] + i)
        b_l[i] = If(checks[j], b_l[j] + i, a_l[j] + b_l[j])

    s.add(b_l[-1] == 700 + n)

    res = s.check()
    if res == unsat:
        print(f"unsat for n == {n}")
        run(model, n)
    else:
        model = s.model()
        print(model)
        run(model, n)
