# Base SUMO worker Dockerfile
# Build: docker build -t sumo-worker:latest .

FROM ubuntu:jammy

ENV SUMO_HOME=/usr/share/sumo

# Install SUMO from the stable PPA
RUN apt-get update \
 && apt-get install -y software-properties-common \
 && add-apt-repository ppa:sumo/stable \
 && apt-get update \
 && apt-get install -y sumo sumo-doc sumo-tools python3 python3-pip git curl nano \
 && apt-get clean

# Create a non-root user
RUN useradd -ms /bin/bash sumo
USER sumo
WORKDIR /home/sumo

# Copy simulation code into the container
COPY --chown=sumo:sumo run_simulations.py ./
COPY --chown=sumo:sumo requirements.txt ./
COPY --chown=sumo:sumo resources ./resources

# Install Python dependencies from requirements.txt
RUN pip3 install --user -r requirements.txt

# Set PATH for pip user installs
ENV PATH="/home/sumo/.local/bin:$PATH"

ENTRYPOINT ["python3", "run_simulations.py"]