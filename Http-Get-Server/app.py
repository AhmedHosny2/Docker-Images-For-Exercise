from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def get_current_time():
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    serverType ="python"
    return jsonify({"current_time": current_time,
                    "serverType": serverType})

if __name__ == '__main__':
    # Bind to 0.0.0.0 to make the server externally visible
    app.run(host='0.0.0.0', port=5005)