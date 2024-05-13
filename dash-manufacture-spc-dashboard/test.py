data = {4294967294: {'rx_bytes': [0, 1, 2], 'tx_bytes': [0], 'duration': [2107.899]},
        1: {'rx_bytes': [16072, 17072, 20000], 'tx_bytes': [16072], 'duration': [1429.083, 2000, 3000]},
        2: {'rx_bytes': [16030, 17030, 20000], 'tx_bytes': [16030], 'duration': [1425.245, 2000, 3000]},
        3: {'rx_bytes': [15554, 16554, 20000], 'tx_bytes': [15554], 'duration': [1425.244, 2000, 3000]}
}

port = 1

duration = data[port]["duration"]
rx_bytes = data[port]["rx_bytes"]
if len(data[port]["duration"]) > 1:
    rate = [(yb - ya) / (xb - xa) if (xb - xa) != 0 else 0
            for (xa, xb), (ya, yb) in zip(zip(duration[:-1], duration[1:]),
                                          zip(rx_bytes[:-1], rx_bytes[1:]))]
else:
    rate = [0]

print(rate)