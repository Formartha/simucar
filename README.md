how to run worker example:
---------
docker run --rm \
  -e ACCEL=2.5 \
  -e TAU=1.2 \
  -e STARTUP_DELAY=0.5 \
  -e EXECUTION_ID=test123 \
  -e MASTER_HOST=http://host.docker.internal:5000 \
  sumo-worker:latest