"""Hourly rhythms at the Causeway by direction, and onward trips to industrial stops by hour."""
from crossborder import config, io, rhythms

print("Loading bus OD (checkpoint rows) and bus transport-node data ...")
bus_od = io.load("origin_destination_bus", origins=config.CHECKPOINT_STOPS)
bus_node = io.load("transport_node_bus")

io.write_table(rhythms.checkpoint_hourly(bus_od, bus_node), "rhythms_checkpoint_hourly")
io.write_table(rhythms.industrial_hourly(bus_od), "rhythms_industrial_hourly")
