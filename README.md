How to run?
----------
1. Install docker-compose and docker
2. run: ``` docker-compose up --build simulator``` on the root of the project (ensure docker-compose.yaml is there)
3. access the ui via http://127.0.0.1:5002

Debugging simulator:
---------
```
  docker build -t sumo-simulator:latest ./simulator && docker run --rm \
  --name sumo_simulator \
  -p 5002:5002 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --network simnet \
  sumo-simulator:latest
 ```

Debugging worker:
--------
```
  docker build -t sumo-worker:latest . && docker run --rm \
  -e ACCEL=4.5 \
  -e TAU=2.2 \
  -e STARTUP_DELAY=10 \
  -e EXPECTED_L3_DELAY=50 \
  -e EXPECTED_L2_DELAY=5 \
  -e EXECUTION_ID=test123 \
  -e MASTER_HOST=http://host.docker.internal:5002 \
  sumo-worker:latest
```