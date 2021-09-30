from z3 import *

chip_size = (30, 30)

pow_min_offset = (16, 16)

pow_sizes = [
    (4, 3),
    (4, 3),
]

com_sizes = [
    (4, 5),
    (4, 6),
    (5, 20),
    (6, 9),
    (6, 10),
    (6, 11),
    (7, 8),
    (7, 12),
    (10, 10),
    (10, 20),
]

pow_positions = [(Int(f"pow{i}_pos_x"), Int(f"pow{i}_pos_y")) for i in range(len(pow_sizes)]
pow_rotated = [Boolean(f"pow{i}_rot") for i in range(len(pow_sizes))]

com_positions = [(Int(f"com{i}_pos_x"), Int(f"com{i}_pos_y")) for i in range(len(pow_sizes)]
com_rotated = [Boolean(f"com{i}_rot") for i in range(len(pow_sizes))]

s = Solver()

# ensure components are placed in the chip
for i in range(len(pow_sizes)):
    sx, sy = pow_sizes[i]
    x, y = pow_positions[i]
    r = pow_rotated[i]

    pos = And(r ==  False, And(x + sx <= chip_size[0], y + sy <= chip_size[1]))
    pos_rotated = And(r == True, And(x + sy <= chip_size[0], y + sx <= chip_size[1]))
    s.add(Or(pos, pos_rotated)

for i in range(len(pow_sizes)):
    sx, sy = com_sizes[i]
    x, y = com_positions[i]
    r = com_rotated[i]

    pos = And(r ==  False, And(x + sx <= chip_size[0], y + sy <= chip_size[1]))
    pos_rotated = And(r == True, And(x + sy <= chip_size[0], y + sx <= chip_size[1]))
    s.add(Or(pos, pos_rotated)

def abs(x):
    return if(x >= 0, x, -x)

def divru(a, b):
    return (a - 1) // b + 1;


# create the unique pairs of power components and
# add constraints so they don't overlap
for i in range(len(pow_sizes)):
    for j in range(p1 + 1, len(pow_sizes)):
        sx, sy = pow_sizes[i]

        p1x, p1y = pow_positions[i]
        p2x, p2y = pow_positions[j]
        r1 = pow_rotated[i]
        r2 = pow_rotated[j]
        
        # If both rotation of the components are the same
        # we can simply check if the positions differ by
        # then the minimum offset in either x or y
        dx = abs(p1x - p2x)
        dy = abs(p1y - p2y)
        same_rotation = Implies(r1 == r2, Or(dx >= pow_min_offset[0], dy >= pow_min_offset[1]))
        # If the rotations are different we need to
        # actually compare center points...

        # if width is greater then height and we rotate a component
        # it means the x-coordinate of the center point will shift
        # by 
        dlenx = (pow_sizes[0] - pow_sizes[1]) // 2
        dleny = (pow_sizes[1] - pow_sizes[0]) // 2
        dx = abs(p1x - p2x) - dlenx
        dy = abs(p1y - p2y) + dleny

        different_rotation = Implies(r1 != r2, Or(dx >= pow_min_offset[0], dy >= pow_min_offset[1]))
                





        # situation 1, p1x < p2x and p2 is rotated
        # 1111            222
        # this means the center of p2 shifts by (width - height) / 2 to the left
        # which means we need to account for an additional divru((width - height) / 2)
        # between the x cooords of the component

        # situation 2, p1x < p2x and p1 is rotated
        # 111             2222
        # this means the center of p1 shifts by (width - height) / 2 to the left
        # which means we need to account for an less divru((width - height) / 2)
        # between the x cooords of the component
