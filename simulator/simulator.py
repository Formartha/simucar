from flask import Flask
from endpoints import register_routes
import os

app = Flask(__name__)
register_routes(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5002)))
