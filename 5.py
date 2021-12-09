from copy import deepcopy

num_channels = 27
num_nodes = 17

# Taken from https://www.win.tue.nl/~hzantema/defnetw.txt.
channel_src  =  [1, 2, 3, 4, 5, 6, 7, 8,  9, 10, 11, 12, 13, 14, 15, 16,  3, 17,  7, 17, 11, 17, 15, 17, 16, 4,  8]
channel_dest =  [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,  1, 17,  3, 17,  7, 17, 11, 17, 15,  2, 6, 10]

routes = [
    [ 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
    [ 2, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2 ],
    [ 17, 17, 0, 3, 3, 3, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17 ],
    [ 26, 26, 26, 0, 4, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26 ],
    [ 5, 5, 5, 5, 0, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5 ],
    [ 6, 6, 6, 6, 6, 0, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6 ],
    [ 19, 19, 19, 19, 19, 19, 0, 7, 7, 7, 19, 19, 19, 19, 19, 19, 19 ],
    [ 27, 27, 27, 27, 27, 27, 27, 0, 8, 27, 27, 27, 27, 27, 27, 27, 27 ],
    [ 9, 9, 9, 9, 9, 9, 9, 9, 0, 9, 9, 9, 9, 9, 9, 9, 9 ],
    [ 10, 10, 10, 10, 10, 10, 10, 10, 10, 0, 10, 10, 10, 10, 10, 10, 10 ],
    [ 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 0, 11, 11, 11, 21, 21, 21 ],
    [ 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 0, 12, 12, 12, 12, 12 ],
    [ 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 0, 13, 13, 13, 13 ],
    [ 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 0, 14, 14, 14 ],
    [ 15, 15, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 0, 15, 23 ],
    [ 16, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 0, 25 ],
    [ 24, 24, 18, 18, 18, 18, 20, 20, 20, 20, 22, 22, 22, 22, 24, 24, 0 ]
]

main_nodes_options = [
    [1, 5, 9, 13],
    [2, 4, 6],
    [1, 3, 5, 15],
    [1, 8, 10],
    [1, 2, 3, 4, 5],
    [11, 12, 15],
    [11, 12, 13, 15],
    [5, 12, 14],
    [5, 11, 14],
]

def path(src, dst):
    if src == dst:
        return []

    chan = routes[src - 1][dst - 1]
    p = [chan - 1]
    while channel_dest[chan - 1] != dst:
        chan = routes[channel_dest[chan - 1] - 1][dst - 1]
        p.append(chan - 1)

    return p

def case(cond, set_stmt, skip_chan_reset):
    tmp = []
    tmp.append("case")
    tmp.append(f"  {cond} : ")

    tmp2 = [set_stmt]
    for other_chan in range(num_channels):
        if other_chan in skip_chan_reset:
            continue
        tmp2.append(f"next(c_{other_chan}) = c_{other_chan}")

    tmp.append("    " + " &\n    ".join(tmp2) + ";")

    tmp.append("  TRUE : ")
    tmp2 = []
    for other_chan in range(num_channels):
        tmp2.append(f"next(c_{other_chan}) = c_{other_chan}")
    tmp.append("    " + " &\n    ".join(tmp2) + ";")

    tmp.append("esac")
    return "\n".join(tmp)

for i, main_nodes in enumerate(main_nodes_options):
    exercise = str(chr(ord('a') + i))
    print(f"Generating smv for {exercise}).")

    out_filename = f"5{exercise}.smv"
    with open(out_filename, 'w') as f:
        f.write("MODULE main\nVAR\n")
        for c in range(num_channels):
            f.write(f"c_{c}: 0..{num_nodes};\n")
        for c in range(num_channels):
            f.write(f"ASSIGN init(c_{c}) := 0;\n")

        f.write("TRANS\n")

        network_cases = []
        cases = []

        # Only routes between main nodes are relevant
        for n in main_nodes:
            for m in main_nodes:
                if n == m:
                    continue

                route = path(n, m)

                # Can always send on the first channel
                start_chan = route[0]
                cond = f"c_{start_chan} = 0"
                network_cases.append(f"({cond})")
                cases.append(case(
                    cond,
                    f"next(c_{start_chan}) = {m}",
                    [start_chan]
                ))

                # Can always receive on the final channel
                end_chan = route[-1]
                cond = f"c_{end_chan} = {m}"
                network_cases.append(f"({cond})")
                cases.append(case(
                    cond,
                    f"next(c_{end_chan}) = 0",
                    [end_chan]
                ))

                # Processing is only relevant between channels
                if len(route) == 1:
                    continue

                for r in range(len(route) - 1):
                    cur_chan = route[r]
                    next_chan = route[r + 1]

                    cond = f"c_{cur_chan} = {m} & c_{next_chan} = 0"
                    network_cases.append(f"({cond})")
                    cases.append(case(
                        cond,
                        f"next(c_{cur_chan}) = 0 & next(c_{next_chan}) = {m}",
                        [cur_chan, next_chan]
                    ))

        f.write(" | \n".join(cases))
        f.write("\n\nCTLSPEC !EF(!(\n  " + " |\n  ".join(network_cases) + "\n))\n")
