import json
from flask import Flask, jsonify, request
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all levels of log messages
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Output to console
        # Uncomment the next line to also log to a file
        # logging.FileHandler("/var/log/application.log"),
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
VARIABLES_FILE = "/variables.txt"  # Ensure the file path is correct

def load_variables():
    """Read the variables from the file."""
    try:
        with open(VARIABLES_FILE, "r") as f:
            # Read the raw content
            raw_content = f.read().strip()

            # Preprocess the content to make it valid JSON
            if not raw_content.startswith("{") or not raw_content.endswith("}"):
                raise ValueError("Invalid JSON format in the file.")

            # Convert to valid JSON format: Add double quotes around keys and values
            json_content = raw_content.replace("{", '{"').replace("}", '"}').replace(":", '":"').replace(",", '","')

            # Deserialize the JSON string into a Python dictionary
            file_content = json.loads(json_content)
            logger.debug(f"Variables file content: {file_content}")
            return file_content
    except FileNotFoundError:
        logger.error(f"Error: {VARIABLES_FILE} not found.")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while reading {VARIABLES_FILE}: {e}")
        return None

@app.route('/get-secret-key', methods=['GET'])
def get_auth_key():
    variables = load_variables()
    if not variables:
        return jsonify({
            "Exercise State": "Sorry! No key found."
        }), 404

    secret_key = variables.get("secret").strip()
    if not secret_key:
        return jsonify({
            "Exercise State": "Sorry! No key found."
        }), 404

    return jsonify({
        "secret_key": secret_key,
        "Header Name": "Secretkey",
        "Exercise State": "Congratulations! You did your first step, now try to use this key to complete the exercise."
    })

@app.route('/unlock-treasure', methods=['POST'])  # Fixed the route path
def auth_key():
    variables = load_variables()
    if not variables:
        return jsonify({
            "Exercise State": "Sorry! Something went wrong. Please try again later."
        }), 500
    # log all req header
    secret_key = request.headers.get('Secretkey')
    # print both
    logger.info(f"Secret key from headers: {secret_key}")
    logger.info(f"Secret key from variables: {variables.get('secret')}")
    # Compare the secret key from headers with the one from the variables file

    if secret_key == variables.get("secret"):
        return jsonify({
            "status": "success",
            "message": "You found the treasure!",
            "reward": "Golden Key of Knowledge"
        })
    else:
        return jsonify({
            "Exercise State": "Sorry! Wrong Key."
        }), 401

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, SECRET_KEY"
    return response

if __name__ == '__main__':
    vals =load_variables()
    logger.info(f"Variables loaded: {vals}")
    app.run(host='0.0.0.0', port=5010)