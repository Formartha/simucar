import subprocess
import uuid

# Store results per execution UUID
execution_results = {}

# Track job completion status
execution_status = {}


def launch_simulation_job(accel, tau, startup_delay, execution_id):
    container_name = f"sim_worker_{execution_id}"
    cmd = [
        "docker", "run", "--rm",
        "--name", container_name,
        "-e", f"ACCEL={accel}",
        "-e", f"TAU={tau}",
        "-e", f"STARTUP_DELAY={startup_delay}",
        "-e", f"EXECUTION_ID={execution_id}",
        "simulation-worker-image"
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        execution_status[execution_id] = 'completed'
    except subprocess.CalledProcessError as e:
        execution_status[execution_id] = 'failed'
        execution_results[execution_id] = {"error": e.stderr}


def start_simulation_batch(permutations):
    batch_id = uuid.uuid4().hex
    for accel, tau, startup_delay in permutations:
        execution_id = uuid.uuid4().hex
        execution_status[execution_id] = 'running'
        launch_simulation_job(accel, tau, startup_delay, execution_id)
    return batch_id


def get_execution_status():
    return execution_status


def submit_result_to_engine(execution_id, result):
    execution_results[execution_id] = result
    execution_status[execution_id] = 'completed'


def get_all_results():
    return execution_results
