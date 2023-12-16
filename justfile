# Justfile

# Get the kafka running
setup-kafka:
    sudo docker compose -f docker-compose.yml up zookeeper kafka
    docker exec -it kafka-broker bash -c "/opt/kafka/bin/kafka-topics.sh --create --topic in-topic --partitions 1 --replication-factor 1 --bootstrap-server localhost:9092"
    docker exec -it kafka-broker bash -c "/opt/kafka/bin/kafka-topics.sh --create --topic out-topic --partitions 1 --replication-factor 1 --bootstrap-server localhost:9092" 

setup-kafka-producer:
    docker build -t kafka-sumer-img -f kafkaDockerfile .
    docker run --name kafka-producer --network flinkplayground_projectnetwork -p 8001:8001 -v .:/data -it kafka-sumer-img bash
    # sudo docker compose -f docker-compose.yml up producer
    # docker exec -it kafka-consumer bash -c "python /app/kafkaProducer.py"

setup-kafka-consumer:
    docker build -t kafka-sumer-img -f kafkaDockerfile .
    docker run --name kafka-consumer --network flinkplayground_projectnetwork -v .:/data -it kafka-sumer-img bash
    # sudo docker compose -f docker-compose.yml up -d consumer
    # docker exec -it kafka-consumer bash -c "python /app/kafkaConsumer.py"   

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

clean-topic:
    docker exec -it kafka-broker bash -c "/opt/kafka/bin/kafka-topics.sh --delete --topic in-topic --bootstrap-server localhost:9092"
    docker exec -it kafka-broker bash -c "/opt/kafka/bin/kafka-topics.sh --create --topic in-topic --partitions 1 --replication-factor 1 --bootstrap-server localhost:9092"