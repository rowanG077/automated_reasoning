from copy import deepcopy

num_channels = 27
num_nodes = 17

channel_src =   [1, 2, 3,  3, 4, 4, 5, 6, 7,  7, 8,  8,  9, 10, 11, 11, 12, 13, 14, 15, 15, 16, 16, 17, 17, 17, 17]
channel_dest =  [2, 3, 4, 17, 5, 6, 6, 7, 8, 17, 9, 10, 10, 11, 12, 17, 13, 14, 15, 16, 17,  1,  2,  3,  7, 11, 15]

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

def path(channel, node_target, visited_channels = []):
    if channel in visited_channels:
        return None
    dest = channel_dest[channel]
    if dest == node_target:
        return [channel]

    visited_channels = deepcopy(visited_channels)
    visited_channels.append(channel)

    paths = [path(i, node_target, visited_channels) for i in range(num_channels) if channel_src[i] == dest]

    paths = list(sorted([p for p in paths if p != None], key = len))
    if len(paths) > 0:
        shortest_path = deepcopy(paths[0])
        shortest_path.insert(0, channel)
        return shortest_path
    else:
        return None

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

for c in path(19, 13, []):
    s = channel_src[c]
    d = channel_dest[c]
    print(f"Going from {s} -> {d} over channel: {c}")

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
        for chan in range(num_channels):
            src = channel_src[chan]
            dst = channel_dest[chan]

            # # Node can send.
            if src in main_nodes:
                for send_dst in main_nodes:
                    if src != send_dst:
                        cond = f"c_{chan} = 0"
                        network_cases.append(f"({cond})")
                        cases.append(case(
                            cond,
                            f"next(c_{chan}) = {send_dst}",
                            [chan]
                        ))

            for m, p in [(m, path(chan, m)) for m in main_nodes]:
                if src == m:
                    continue
                # Current channel connects to destination (receive)
                if len(p) == 1:
                    cond = f"c_{chan} = {m}"
                    network_cases.append(f"({cond})")
                    cases.append(case(
                        cond,
                        f"next(c_{chan}) = 0",
                        [chan]
                    ))
                # current channel doesn't connect to destination (process)
                else:
                    next_chan = p[1]
                    cond = f"c_{next_chan} = 0 & c_{chan} = {m}"
                    network_cases.append(f"({cond})")
                    cases.append(case(
                        cond,
                        f"next(c_{next_chan}) = c_{chan} & next(c_{chan}) = 0",
                        [chan, next_chan]
                    ))

        f.write(" | \n".join(cases))
        f.write("\n\nCTLSPEC !EF(!(\n  " + " |\n  ".join(network_cases) + "\n))\n")

