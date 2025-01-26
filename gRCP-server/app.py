import json
from flask import Flask, jsonify, request
from datetime import datetime
import logging
import grpc
from concurrent import futures
import time
import uuid

import service_pb2
import service_pb2_grpc

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




# In-memory storage for users
USERS = {}

class UserServiceServicer(service_pb2_grpc.UserServiceServicer):
    def CreateUser(self, request, context):
        user_id = str(uuid.uuid4())
        user = service_pb2.User(id=user_id, name=request.name, email=request.email)
        USERS[user_id] = user
        print(f"Created User: {user}")
        return service_pb2.CreateUserResponse(user=user)

    def GetUser(self, request, context):
        user = USERS.get(request.id)
        if user:
            return service_pb2.GetUserResponse(user=user)
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('User not found')
            return service_pb2.GetUserResponse()

    def ListUsers(self, request, context):
        return service_pb2.ListUsersResponse(users=list(USERS.values()))

    def DeleteUser(self, request, context):
        if request.id in USERS:
            del USERS[request.id]
            print(f"Deleted User ID: {request.id}")
            return service_pb2.DeleteUserResponse(success=True)
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('User not found')
            return service_pb2.DeleteUserResponse(success=False)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_UserServiceServicer_to_server(UserServiceServicer(), server)
    server.add_insecure_port(f"[::]:5015")
    server.start()
    print(f"gRPC server is running on port 5015...")
    try:
        while True:
            time.sleep(86400)  # Keep the server alive for 1 day
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()