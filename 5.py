
num_channels = 4
num_nodes = 4

main_nodes = [1, 2, 3]

channel_src = [1, 2, 3, 4]
channel_dest = [2, 3, 4, 1]

def path(channel, node_target):
    dest = channel_dest[channel]
    if dest == node_target:
        return [channel]

    paths = [path(i, node_target) for i in range(num_channels) if channel_src[i] == dest]

    shortest = list(sorted(paths, key = len))[0]
    shortest.insert(0, channel)

    return shortest

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

out_filename = "5.smv"
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

