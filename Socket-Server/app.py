import json
import socket
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
# Configuration
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




def main():
    variables = load_variables()
    HOST = "0.0.0.0"
    PORT = int(variables.get("port"))

    logger.debug(f" retrieved Host: {HOST}, Port: {PORT}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reuse address
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Server is running on {HOST}:{PORT}")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connection established with {client_address}")

            with client_socket:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    print(f"Received from {client_address}: {data.decode()}")
                    client_socket.sendall(data)  # Echo data back to client
                    if "Bye bye" in data.decode():
                        print(f"Closing connection with {client_address}")
                        break
if __name__ == "__main__":
    main()