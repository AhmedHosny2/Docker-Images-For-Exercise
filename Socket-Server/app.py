import socket

def main():
    host = '10.1.0.114'  # Replace with your server's IP if different
    port = 5007

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            print(f"Connected to server at {host}:{port}")

            while True:
                data = s.recv(1024)
                if not data:
                    break
                print("Received:", data.decode().strip())
                if "Bye bye" in data.decode():
                    break

        except ConnectionRefusedError:
            print(f"Could not connect to server at {host}:{port}")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()