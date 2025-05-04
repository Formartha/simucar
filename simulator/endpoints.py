from flask import Blueprint, render_template, request, jsonify
import itertools
import uuid
from engine import start_simulation_batch, execution_status, submit_result_to_engine, execution_results

bp = Blueprint('main', __name__, template_folder='templates')


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/submit_permutations', methods=['POST'])
def submit_permutations():
    data = request.get_json()
    try:
        expected_delays = {
            'I2': float(data['expected_delay_I2']),
            'I3': float(data['expected_delay_I3'])
        }
        accel_list = [float(v) for v in data['accel_list']]
        tau_list = [float(v) for v in data['tau_list']]
        startup_delay_list = [float(v) for v in data['startup_delay_list']]

        permutations = list(itertools.product(accel_list, tau_list, startup_delay_list))

        batch_id = uuid.uuid4().hex
        for accel, tau, startup_delay in permutations:
            execution_id = uuid.uuid4().hex
            execution_status[execution_id] = 'running'
            start_simulation_batch([(accel, tau, startup_delay)])  # Each permutation runs immediately

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
        if not execution_id:
            return jsonify({'status': 'error', 'message': 'Missing execution_id'}), 400

        submit_result_to_engine(execution_id, result)
        return jsonify({'status': 'success', 'received': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@bp.route('/status/<execution_id>', methods=['GET'])
def status(execution_id):
    status = execution_status.get(execution_id)
    if status:
        return jsonify({'execution_id': execution_id, 'status': status})
    return jsonify({'status': 'error', 'message': 'Execution ID not found'}), 404


@bp.route('/execution-results/<execution_id>', methods=['GET'])
def get_execution_results(execution_id):
    status = execution_results.get(execution_id)
    if status:
        return jsonify({'execution_id': execution_id, 'status': status})
    return jsonify({'status': 'error', 'message': 'Execution ID not found'}), 404


def register_routes(app):
    app.register_blueprint(bp)