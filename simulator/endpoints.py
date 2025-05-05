from flask import Blueprint, render_template, request, jsonify
import itertools
import uuid

from engine import start_simulation_batch, submit_result_to_engine, execution_results, ensure_float

bp = Blueprint('main', __name__, template_folder='templates')


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/submit_permutations', methods=['POST'])
def submit_permutations():
    data = request.get_json()
    try:
        l2_delay = float(data['expected_delay_I2'])
        l3_delay = float(data['expected_delay_I3'])
        accel_list = [float(v) for v in data['accel_list']]
        tau_list = [float(v) for v in data['tau_list']]
        startup_delay_list = [float(v) for v in data['startup_delay_list']]
        batch_id = uuid.uuid4().hex

        # Build full permutation list
        permutations = [
            (accel, tau, startup_delay, l2_delay, l3_delay)
            for accel, tau, startup_delay in itertools.product(accel_list, tau_list, startup_delay_list)
        ]

        # Launch all in one batch under shared ID
        start_simulation_batch(permutations, batch_id)

        return jsonify({
            'status': 'started',
            'execution_batch_id': batch_id,
            'total_permutations': len(permutations)
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@bp.route('/results', methods=['POST'])
def results():
    try:
        result = request.get_json()
        execution_id = result.get('execution_id')
        permutation_id = result.get("permutation_id")
        if not execution_id:
            return jsonify({'status': 'error', 'message': 'Missing execution_id'}), 400

        submit_result_to_engine(execution_id, permutation_id, result)
        return jsonify({'status': 'success', 'received': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@bp.route('/execution-results/<execution_id>', methods=['GET'])
def get_execution_results(execution_id):
    status = execution_results.get(execution_id)
    if status:
        return jsonify({'execution_id': execution_id, 'status': status})
    return jsonify({'status': 'error', 'message': 'Execution ID not found'}), 404


@bp.route("/execution-results/<execution_id>/winner", methods=["GET"])
def get_best_permutation(execution_id):
    execution_data = execution_results.get(execution_id)
    if not execution_data:
        return jsonify({"error": "Execution ID not found"}), 404

    best_score = float('inf')
    best_permutation = None
    best_result = None

    for permutation_id, result in execution_data.items():
        sim = result.get("intersection_avg_delays", {})
        i2_sim = sim.get("I2")
        i3_sim = sim.get("I3")
        i2_exp = ensure_float(result.get("expected_l2_delay"))
        i3_exp = ensure_float(result.get("expected_l3_delay"))

        if None in (i2_sim, i3_sim, i2_exp, i3_exp):
            continue

        error = (i2_sim - i2_exp) ** 2 + (i3_sim - i3_exp) ** 2
        if error < best_score:
            best_score = error
            best_permutation = permutation_id
            best_result = result

    if best_permutation is None:
        return jsonify({"error": "No valid permutations found for winner calculation."}), 400

    return jsonify({
        "best_permutation": best_permutation,
        "total_error": round(best_score, 3),
        "result": best_result
    })


def register_routes(app):
    app.register_blueprint(bp)
