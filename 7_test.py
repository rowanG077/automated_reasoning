# counter example monoid found by mace4 for c)

# identity element
i = 0

# binary operator
o = [
    [ 0, 1, 2, 3, 4, 5, 6, 7 ],
    [ 1, 0, 3, 2, 5, 4, 7, 6 ],
    [ 2, 4, 0, 6, 1, 7, 3, 5 ],
    [ 3, 5, 1, 7, 0, 6, 2, 4 ],
    [ 4, 2, 6, 0, 7, 1, 5, 3 ],
    [ 5, 3, 7, 1, 6, 0, 4, 2 ],
    [ 6, 7, 4, 5, 2, 3, 0, 1 ],
    [ 7, 6, 5, 4, 3, 2, 1, 0 ]
]

# set M
m = len(o[0])

for x in range(m):
    # identity property must hold
    val = o[x][i]
    if x != val:
        print(f"identity property does not hold o({x}, {i}) != {i}")

    val = o[i][x]
    if x != val:
        print(f"identity property does not hold o({i}, {x}) != {i}")

    # c) property must hold
    val = o[o[x][x]][o[x][x]]
    if i != val:
        print(f"property c) does not hold o(o({x}, {x}), o({x}, {x})) != {i}")

    for y in range(m):
        # associativity property must hold
        for z in range(m):
            val1 = o[x][o[y][z]]
            val2 = o[o[x][y]][z]
            if val1 != val2:
                print(f"associativity property does not hold o({x}, o({y}, {z})) != o(o({x}, {y}), {z})")

        # check if commutativity holds
        val1 = o[x][y]
        val2 = o[y][x]
        if val1 != val2:
            print(f"commutativity property does not hold o({x}, {y}) != o({y}, {x})")
