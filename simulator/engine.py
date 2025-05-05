import subprocess
import uuid

# Store results per execution UUID
execution_results = {}


def launch_simulation_job(accel, tau, startup_delay, execution_id, l2_delay, l3_delay):
    container_name = f"sim_worker_{execution_id}_{uuid.uuid4()}"
    cmd = (
        f"docker run --rm "
        f"--name {container_name} "
        f"-e ACCEL={accel} "
        f"-e TAU={tau} "
        f"-e STARTUP_DELAY={startup_delay} "
        f"-e EXPECTED_L2_DELAY={l2_delay} "
        f"-e EXPECTED_L3_DELAY={l3_delay} "
        f"-e EXECUTION_ID={execution_id} "
        f"-e MASTER_HOST=http://host.docker.internal:5002 "
        f"sumo-worker:latest"
    )

    try:
        subprocess.Popen(cmd, shell=True)
    except Exception as e:
        execution_results[execution_id] = {"error": str(e)}


def start_simulation_batch(permutations, execution_id):
    for accel, tau, startup_delay, l2_delay, l3_delay in permutations:
        launch_simulation_job(accel, tau, startup_delay, execution_id, l2_delay, l3_delay)


def submit_result_to_engine(execution_id, permutation_id, result):
    if execution_id not in execution_results:
        execution_results[execution_id] = {}
    execution_results[execution_id][permutation_id] = result


def ensure_float(value):
    if not isinstance(value, float):
        try:
            value = float(value)
        except (ValueError, TypeError):
            print(f"Cannot convert {value} to float.")
            return None
    return value
