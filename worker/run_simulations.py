import os
import json
import traci
import requests
import sys
from collections import defaultdict

# ENV VARS
accel = os.getenv("ACCEL")
tau = os.getenv("TAU")
startup_delay = os.getenv("STARTUP_DELAY")
execution_id = os.getenv("EXECUTION_ID")
master_host = os.getenv("MASTER_HOST")

# Required check
if not all([execution_id, master_host]):
    print("Missing required environment variables.")
    sys.exit(1)

DIR_PATH = os.path.dirname(os.path.abspath(__file__))

SPEED_THRESHOLD = 0.3  # m/s
INTERSECTIONS_OF_INTEREST = ("I2", "I3")
SIMULATION_DURATION = 2000
SUMO_BINARY = "sumo"
CONFIG_PATH = os.path.join(DIR_PATH, "resources", "hw_model.sumocfg")
SCENARIO_PATH = os.path.join(DIR_PATH, "resources", "scenario.json")


def add_vehicles(vehicles_batch, start_index):
    index = start_index
    for route_id, _, vehicle_type in vehicles_batch:
        vehicle_id = f"{route_id}_{index}"
        traci.vehicle.add(vehicle_id, route_id, vehicle_type)
        index += 1
    return index

def run_simulation():
    with open(SCENARIO_PATH, 'r') as file:
        vehicle_schedule = json.load(file)

    traci.start([
        SUMO_BINARY,
        "-c", CONFIG_PATH,
        "--start",
        "--quit-on-end"
    ])

    delays = defaultdict(int)
    stopped_vehicles = defaultdict(set)
    index = 0

    try:
        for step in range(SIMULATION_DURATION):
            if str(step) in vehicle_schedule:
                index = add_vehicles(vehicle_schedule[str(step)], index)

            traci.simulationStep()

            for veh_id in traci.vehicle.getIDList():
                speed = traci.vehicle.getSpeed(veh_id)
                edge = traci.vehicle.getRoadID(veh_id)

                if speed < SPEED_THRESHOLD:
                    intersection = next((i for i in INTERSECTIONS_OF_INTEREST if i in edge), None)
                    if intersection:
                        delays[intersection] += 1
                        stopped_vehicles[intersection].add(veh_id)
    finally:
        traci.close()

    avg_delays = {
        k: (delays[k] / len(stopped_vehicles[k]) if stopped_vehicles[k] else 0)
        for k in INTERSECTIONS_OF_INTEREST
    }

    return avg_delays


def post_result(result):
    payload = {
        "execution_id": execution_id,
        "accel": accel,
        "tau": tau,
        "startupDelay": startup_delay,
        "intersection_avg_delays": result
    }
    try:
        res = requests.post(f"{master_host}/results", json=payload)
        res.raise_for_status()
    except Exception:
        pass


if __name__ == "__main__":
    result = run_simulation()
    post_result(result)