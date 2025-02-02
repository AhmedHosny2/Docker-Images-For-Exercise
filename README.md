# Docker Images for Student Exercises

This repository is a simple demo of container images designed for student exercises. It provides basic examples for both server and client setups, and shows admins how to create their own exercises.

---

## Included Examples

- **Server Example:**  
  A minimal containerized server to demonstrate how a service can run inside a Docker container.

- **Client Example:**  
  A simple containerized client that can interact with a server.

---

## How to Run the Examples

### Running the Server Example

1. Navigate to the server example directory:
   ```bash
   cd Server-Example

	2.	Build the Docker image:

docker build -t my-server-example .


	3.	Run the container:

docker run -it --rm my-server-example



Running the Client Example
	1.	Navigate to the client example directory:

cd Client-Example


	2.	Build the Docker image:

docker build -t my-client-example .


	3.	Run the container:

docker run -it --rm my-client-example

Creating Your Own Exercise

Admins can create their own server or client exercises by following these simple steps:
	1.	Set Up a New Directory:
Create a new folder for your exercise (e.g., My-Exercise).
	2.	Write Your Application Code:
Develop your server or client code as needed.
	3.	Create a Dockerfile:
Write a Dockerfile to containerize your application. For example:

FROM python:3.9-slim
WORKDIR /app
COPY . .
CMD ["python", "your_script.py"]


	4.	Build and Run Your Image:
Use the same build and run commands as shown above:

docker build -t my-custom-exercise .
docker run -it --rm my-custom-exercise


