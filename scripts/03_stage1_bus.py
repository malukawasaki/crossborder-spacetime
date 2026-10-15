"""Stage 1 tables: Causeway bus crossings, onward split from Woodlands Checkpoint, corridor stops."""
from crossborder import config, io, stage1

print("Loading bus OD (checkpoint rows) and bus transport-node data ...")
bus_od = io.load("origin_destination_bus", origins=config.CHECKPOINT_STOPS)
bus_node = io.load("transport_node_bus")

io.write_table(stage1.crossings(bus_od), "stage1_causeway_crossings")
io.write_table(stage1.feeder_split(bus_od), "stage1_feeder_split_46109")
io.write_table(stage1.top_destinations(bus_od), "stage1_top_destinations_46109")
io.write_table(stage1.industrial_clusters(bus_od), "stage1_industrial_clusters")
io.write_table(stage1.corridor_stops(bus_node, bus_od), "stage1_corridor_stops")
