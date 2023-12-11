# Justfile

# Build the Flink job Docker image
build-docker-image:
    docker build -t your-flink-job .

# Run Flink cluster in Docker
run-flink-cluster:
    docker run -d --name flink-cluster -p 8081:8081 apache/flink:1.14.3-scala_2.12-java11 standalone-jobmanager
    docker exec -it flink-cluster bash -c "/opt/flink/bin/taskmanager.sh start"

# Run Flink job in Docker
run-flink-job:
    docker run -d --name your-job-container your-flink-job

# Monitor Flink cluster
monitor-flink-cluster:
    echo "Access Flink dashboard at http://localhost:8081"

# Clean up Docker containers
clean-docker:
    docker stop flink-cluster your-job-container
    docker rm flink-cluster your-job-container

# Complete workflow
run-workflow: build-docker-image run-flink-cluster run-flink-job monitor-flink-cluster

# Clean up everything
clean: clean-docker

