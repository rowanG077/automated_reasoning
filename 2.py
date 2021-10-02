from z3 import *
import cairo
import math

chip_size = (30, 30)

pow_min_offset = (17, 17)

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

pow_positions = [(Int(f"pow{i}_pos_x"), Int(f"pow{i}_pos_y")) for i in range(len(pow_sizes))]
pow_rotated = [Bool(f"pow{i}_rot") for i in range(len(pow_sizes))]

com_positions = [(Int(f"com{i}_pos_x"), Int(f"com{i}_pos_y")) for i in range(len(com_sizes))]
com_rotated = [Bool(f"com{i}_rot") for i in range(len(com_sizes))]

all_sizes = pow_sizes + com_sizes
all_positions = pow_positions + com_positions
all_rotated = pow_rotated + com_rotated

s = Solver()

def z3_abs(x):
    return If(x >= 0, x, -x)

def draw_solution(model):
    with cairo.SVGSurface("2.svg", 1000, 1000) as surface:
        context = cairo.Context(surface)
        context.scale(chip_size[0] / 3, chip_size[1] / 3)
        context.set_line_width(0.03)

        for i in range(chip_size[0] + 1):
            context.move_to(i, 0)
            context.line_to(i, chip_size[0])
            context.stroke()

        for j in range(chip_size[1] + 1):
            context.move_to(0, j)
            context.line_to(chip_size[1], j)
            context.stroke()

        # draw normal components
        context.set_font_size(2)
        
        context.set_line_width(0.1)
        for i in range(len(com_sizes)):
            sx, sy = com_sizes[i]
            r = is_true(model[com_rotated[i]])
            x = model[com_positions[i][0]].as_long()
            y = model[com_positions[i][1]].as_long()
            w = sy if r else sx 
            h = sx if r else sy

            context.rectangle(x, y, w, h)
            context.set_source_rgba(0, 0, 1, 1)
            context.stroke_preserve()
            context.set_source_rgba(0, 0, 1, 0.5)
            context.fill()

            context.set_source_rgba(1, 1, 1, 1)
            context.move_to(x + 0.05, y + 2.0)
            context.show_text(f"C{i}")

        # draw power components
        context.set_line_width(0.1)
        for i in range(len(pow_sizes)):
            sx, sy = pow_sizes[i]
            r = is_true(model[pow_rotated[i]])
            x = model[pow_positions[i][0]].as_long()
            y = model[pow_positions[i][1]].as_long()
            w = sy if r else sx 
            h = sx if r else sy

            context.rectangle(x, y, w, h)
            context.set_source_rgba(1, 0, 0, 1)
            context.stroke_preserve()
            context.set_source_rgba(1, 0, 0, 0.5)
            context.fill()

            context.set_source_rgba(1, 1, 1, 1)
            context.move_to(x, y + 2.0)
            context.show_text(f"P{i}")

# ensure all components are placed in the chip
for i in range(len(all_sizes)):
    sx, sy = all_sizes[i]
    x, y = all_positions[i]
    r = all_rotated[i]

    pos = And(r ==  False, And(x + sx <= chip_size[0], y + sy <= chip_size[1]))
    pos_rotated = And(r == True, And(x + sy <= chip_size[0], y + sx <= chip_size[1]))
    
    s.add(x >= 0)
    s.add(y >= 0)
    s.add(Or(pos, pos_rotated))

# Create unique pairs of all components and ensure they don't overlap
for i in range(len(all_sizes)):
    for j in range(i + 1, len(all_sizes)):
        s1x, s1y = all_sizes[i]
        s2x, s2y = all_sizes[j]
        p1x1, p1y1 = all_positions[i]
        p2x1, p2y1 = all_positions[j]
        r1 = all_rotated[i]
        r2 = all_rotated[j]

        p1x2 = If(r1, p1x1 + s1y, p1x1 + s1x)
        p1y2 = If(r1, p1y1 + s1x, p1y1 + s1y)
        p2x2 = If(r2, p2x1 + s2y, p2x1 + s2x)
        p2y2 = If(r2, p2y1 + s2x, p2y1 + s2y)

        not_x_overlap = Or(p1x2 <= p2x1, p2x2 <= p1x1)
        not_y_overlap = Or(p1y2 <= p2y1, p2y2 <= p1y1)
        s.add(Or(not_x_overlap, not_y_overlap))

# create the unique pairs of power components and ensure
# their centers are far enough away from eachother
for i in range(len(pow_sizes)):
    for j in range(i + 1, len(pow_sizes)):
        sx, sy = pow_sizes[i]

        p1x, p1y = pow_positions[i]
        p2x, p2y = pow_positions[j]
        r1 = pow_rotated[i]
        r2 = pow_rotated[j]

        # to check whether a power component is placed close enough we
        # create a virtual grid twice as large as the original
        # where the components are also twice as large
        # This way the center points of the power components
        # always align with a grid point and we stay 
        # in the nice and comfy domain of integers
        cp1x = If(r1, 2 * p1x + sy, 2 * p1x + sx)
        cp1y = If(r1, 2 * p1y + sx, 2 * p1y + sy)
        cp2x = If(r2, 2 * p2x + sy, 2 * p2x + sx)
        cp2y = If(r2, 2 * p2y + sx, 2 * p2y + sy)

        dx = z3_abs(cp1x - cp2x) >= 2 * pow_min_offset[0]
        dy = z3_abs(cp1y - cp2y) >= 2 * pow_min_offset[1]
        s.add(Or(dx, dy))

# Ensure every normal component has at least a single edge
# in common with a power componnent
for i in range(len(com_sizes)):
    pow_edges = []
    for j in range(len(pow_sizes)):
        s1x, s1y = com_sizes[i]
        s2x, s2y = pow_sizes[j]
        p1x1, p1y1 = com_positions[i]
        p2x1, p2y1 = pow_positions[j]
        r1 = com_rotated[i]
        r2 = pow_rotated[j]

        p1x2 = If(r1, p1x1 + s1y, p1x1 + s1x)
        p1y2 = If(r1, p1y1 + s1x, p1y1 + s1y)
        p2x2 = If(r2, p2x1 + s2y, p2x1 + s2x)
        p2y2 = If(r2, p2y1 + s2x, p2y1 + s2y)

        x_overlap = And(p1x2 > p2x1, p2x2 > p1x1)
        x_edge_match = Or(And(x_overlap, p1y2 == p2y1), And(x_overlap, p2y2 == p1y1))

        y_overlap = And(p1y2 > p2y1, p2y2 > p1y1)
        y_edge_match = Or(And(y_overlap,  p1x2 == p2x1), And(y_overlap, p2x2 == p1x1))
        connected = Or(x_edge_match, y_edge_match) 

        pow_edges.append(connected)
    
    constraint = Or(pow_edges[0], pow_edges[1])
    for j in range(2, len(pow_sizes)):
        constraint = Or(constraint, pow_edges[j])

    s.add(constraint)

res = s.check()
if res == unsat:
    print("unsat")
    sys.exit(1)

model = s.model()
print(model)
draw_solution(model)