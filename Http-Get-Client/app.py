import time
import requests
import os
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
USER_IP_FILE = "/users_ip.txt"  # User's IP file in the root of the container
PORT_FILE = "/port.txt"  # Port number file in the root of the container
CONTAIERID_FILE ="/containerid.txt"
CHECK_INTERVAL = 5  # Interval between GET requests, in seconds

# Global Variables
users_ip = []
users_uid = []


def is_valid_ip(ip):
    """Simple IP address validation."""
    parts = ip.split(".")
    if len(parts) != 4:
        logger.debug(f"IP '{ip}' does not have 4 parts.")
        return False
    try:
        valid = all(0 <= int(part) <= 255 for part in parts)
        if not valid:
            logger.debug(f"IP '{ip}' has parts outside the valid range (0-255).")
        return valid
    except ValueError:
        logger.debug(f"IP '{ip}' contains non-integer parts.")
        return False


def get_container_id():
    """Read the container  id from the containerid file."""
    try:
        with open(CONTAIERID_FILE, "r") as f:
            containerID_content = f.read().strip()
            logger.debug(f"Containerid file content: '{containerID_content}'")
            logger.info(f"id  retrieved: {containerID_content}")
            return containerID_content

    except FileNotFoundError:
        logger.error(f"Error: {CONTAIERID_FILE} not found.")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while reading {CONTAIERID_FILE}: {e}")
        return None


def get_user_ips():
    """Read the user's IPs and UIDs from the file."""
    global users_ip, users_uid
    users_ip = []
    users_uid = []
    logger.debug("Attempting to read user IPs and UIDs from file.")

    try:
        with open(USER_IP_FILE, "r") as f:
            lines = f.read().splitlines()  # Handles different newline characters
            logger.debug(f"Total lines read from {USER_IP_FILE}: {len(lines)}")

            if not lines:
                logger.info("User IP file is empty.")
                return

            for line_number, line in enumerate(lines, start=1):
                original_line = line  # Keep the original line for logging
                line = line.strip()
                logger.debug(f"Processing line {line_number}: '{original_line}'")

                if not line:
                    logger.warning(f"Line {line_number} is empty. Skipping.")
                    continue  # Skip empty lines

                parts = line.split(",")
                logger.debug(f"Line {line_number} split into parts: {parts}")

                # if len(parts) != 2:
                #     logger.error(f"Malformed line {line_number} skipped: '{original_line}'")
                #     continue  # Skip malformed lines

                ip, uid = parts
                ip = ip.strip()
                uid = uid.strip()
                logger.debug(f"Line {line_number} parsed IP: '{ip}', UID: '{uid}'")

                # Validate IP
                if not is_valid_ip(ip):
                    logger.error(f"Invalid IP format on line {line_number}: '{ip}'. Skipping.")
                    continue
                #
                # # Validate UID
                # if not uid:
                #     logger.error(f"Empty UID on line {line_number}. Skipping.")
                #     continue

                users_ip.append(ip)
                users_uid.append(uid)
                logger.info(f"Line {line_number}: Added IP '{ip}' and UID '{uid}' to lists.")

        logger.debug(f"Total valid entries retrieved: {len(users_ip)}")
        logger.debug(f"User IPs: {users_ip}")
        logger.debug(f"User UIDs: {users_uid}")

    except FileNotFoundError:
        logger.error(f"Error: {USER_IP_FILE} not found.")
    except Exception as e:
        logger.error(f"Unexpected error while reading {USER_IP_FILE}: {e}")


def get_port():
    """Read the port number from the port file."""
    try:
        with open(PORT_FILE, "r") as f:
            port_content = f.read().strip()
            logger.debug(f"Port file content: '{port_content}'")
            if port_content.isdigit():
                port = int(port_content)
                logger.info(f"Port retrieved: {port}")
                return port
            else:
                logger.error(f"Invalid port number in {PORT_FILE}: '{port_content}'")
                return None
    except FileNotFoundError:
        logger.error(f"Error: {PORT_FILE} not found.")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while reading {PORT_FILE}: {e}")
        return None


def on_successful_request(ip, uid, container_id):
    """Action to perform when the request is successful."""
    logger.info(f"Request to {ip}:{container_id} sent successfully! Performing an action...")
    try:
        with open("/action_log.txt", "a") as log_file:
            log_entry = f"Action completed after successful request to {ip}:{container_id} with UID {uid}!\n"
            log_file.write(log_entry)
            logger.debug(f"Action logged in /action_log.txt: '{log_entry.strip()}'")

        # Send API request to the server informing it that the action was completed
        api_url = f"http://0.0.0.0:3000/api/ClientEvaluation/1/{container_id}/{ip}"

        logger.debug(f"Sending GET request to API URL: {api_url} ")
        response = requests.get(api_url)
        logger.info(f"Server informed: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Failed to log action or notify server: {e}")


def main():
    """Main loop to keep trying GET requests to all user IPs."""
    container_id = get_container_id()

    logger.info(f"Container ID: {container_id}")

    while True:
        get_user_ips()
        port = get_port()

        if not users_ip:
            logger.warning("No valid IPs found. Retrying...")
        elif port is None:
            logger.warning("Port number is invalid or not found. Retrying...")
        else:
            logger.debug(f"Starting to send GET requests to {len(users_ip)} IPs.")
            for ip, uid in zip(users_ip, users_uid):
                target_url = f"http://{ip}:{port}"
                logger.info(f"Sending GET request to {target_url}...")
                try:
                    response = requests.get(target_url, timeout=10)  # Added timeout for better handling
                    logger.debug(f"Received response: {response.status_code} - {response.text}")
                    if response.status_code == 200:
                        logger.info(f"Success: {response.text}")
                        on_successful_request(ip, uid, container_id)
                    else:
                        logger.error(f"Failed with status code: {response.status_code} for {ip}:{port}")
                except requests.exceptions.RequestException as e:
                    logger.error(f"Error sending request to {ip}:{port} - {e}")

        logger.debug(f"Sleeping for {CHECK_INTERVAL} seconds before next check.")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    logger.info("Container has started and will create an award application HTML file.")
    logger.info("Starting the Python application...")
    main()