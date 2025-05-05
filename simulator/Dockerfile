FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install and add docker.io ability
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y docker.io

# Copy the rest of the simulator code
COPY . .

# Expose port (optional, depending on your app)
EXPOSE 5002

# Run the simulator (adjust this if the entry file is named differently)
CMD ["python", "simulator.py"]