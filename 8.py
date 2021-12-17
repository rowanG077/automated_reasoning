from z3 import *
import cairo

problem = [
    [0, 0, 0, 4, 0, 0, 0],
    [0, 3, 0, 0, 2, 5, 0],
    [0, 0, 0, 3, 1, 0, 0],
    [0, 0, 0, 5, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0],
    [2, 0, 0, 0, 4, 0, 0], 
]

w = len(problem[0])
h = len(problem)

for y in range(h):
    assert(len(problem[y]) == w)

# the grid variables
grid = [[Int(f"cell_{x}_{y}") for x in range(w)] for y in range(h)]

# connections variables.
v_connections = [[Bool(f"vconn_{x}_{y}") for x in range(w)] for y in range(h - 1)]
h_connections = [[Bool(f"hconn_{x}_{y}") for x in range(w - 1)] for y in range(h)]

def get_maybe(ls, iy, ix):
    try:
        return ls[iy][ix] if ix >= 0 and iy >= 0 else None
    except IndexError:
        return None

def get_connections(iy, ix):
    left = get_maybe(h_connections, y, x-1)
    right = get_maybe(h_connections, y, x)
    up = get_maybe(v_connections, y-1, x)
    down = get_maybe(v_connections, y, x)

    return [left, right, up, down]

def sum_true(l):
    return sum([If(x, 1, 0) for x in l])

def draw_solution(model):
    res_x = 600
    res_y = 600
    with cairo.SVGSurface("8.svg", res_x + 1, res_y + 1) as surface:
        context = cairo.Context(surface)
        context.scale(res_x / w, res_y / h)
        context.set_line_width(0.03)

        for i in range(w + 1):
            context.move_to(i, 0)
            context.line_to(i, w)
            context.stroke()

        for j in range(h + 1):
            context.move_to(0, j)
            context.line_to(h, j)
            context.stroke()

        context.set_font_size(0.65)
        context.set_line_width(0.1)
        for y in range(h):
            for x in range(w):
                n = model[grid[y][x]].as_long()
                context.set_source_rgba(0, 0, 1, 1)
                context.move_to(x + 0.075, y + 0.75)
                context.show_text(f"{n}")

s = Solver()

# Since we don't allow any splitting or overlap that means there are two cases
# 1. Grid number is given from the problem statement. That means it has one connection
# 2. Grid number is unknown. Then it must have two connections.
for y in range(h):
    for x in range(w):
        c = grid[y][x]

        connections = get_connections(y, x)
        existing_connections = filter(lambda x: x != None, connections)

        if problem[y][x] != 0:
            s.add(grid[y][x] == problem[y][x])
            s.add(sum_true(existing_connections) == 1)
        else:
            # set connected cells to same number
            for conn, dir in zip(connections, [(-1, 0), (1, 0), (0, -1), (0, 1)]):
                if conn == None:
                    continue
                c2 = grid[y + dir[1]][x + dir[0]]
                s.add(Implies(conn, c == c2))

            s.add(sum_true(existing_connections) == 2)

res = s.check()
if res == unsat:
    print("unsat")
    sys.exit(1)

model = s.model()
draw_solution(model)
