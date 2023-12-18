# Justfile

# Get the kafka running
setup-kafka:
    sudo docker compose -f docker-compose.yml up zookeeper kafka
    docker exec -it kafka-broker bash -c "/opt/kafka/bin/kafka-topics.sh --create --topic in1-topic --partitions 1 --replication-factor 1 --bootstrap-server localhost:9092"
    docker exec -it kafka-broker bash -c "/opt/kafka/bin/kafka-topics.sh --create --topic in2-topic --partitions 1 --replication-factor 1 --bootstrap-server localhost:9092"
    docker exec -it kafka-broker bash -c "/opt/kafka/bin/kafka-topics.sh --create --topic in3-topic --partitions 1 --replication-factor 1 --bootstrap-server localhost:9092"

setup-kafka-topics:
    docker exec -it kafka-broker bash -c "/opt/kafka/bin/kafka-topics.sh --create --topic in1-topic --partitions 1 --replication-factor 1 --bootstrap-server localhost:9092"
    docker exec -it kafka-broker bash -c "/opt/kafka/bin/kafka-topics.sh --create --topic in2-topic --partitions 1 --replication-factor 1 --bootstrap-server localhost:9092"
    docker exec -it kafka-broker bash -c "/opt/kafka/bin/kafka-topics.sh --create --topic in3-topic --partitions 1 --replication-factor 1 --bootstrap-server localhost:9092"

delete-kafka-topics:
    docker exec -it kafka-broker bash -c "/opt/kafka/bin/kafka-topics.sh --delete --topic in1-topic --bootstrap-server localhost:9092"
    docker exec -it kafka-broker bash -c "/opt/kafka/bin/kafka-topics.sh --delete --topic in2-topic --bootstrap-server localhost:9092"
    docker exec -it kafka-broker bash -c "/opt/kafka/bin/kafka-topics.sh --delete --topic in3-topic --bootstrap-server localhost:9092"

setup-kafka-producer:
    docker build -t kafka-sumer-img -f kafkaDockerfile .
    docker run --name kafka-producer --network flinkplayground_projectnetwork -p 8001:8001 -v .:/data -d kafka-sumer-img bash
    # sudo docker compose -f docker-compose.yml up producer

start-producing NUMBER:
    docker exec -it kafka-consumer bash -c "python /data/kafkaProducer.py {{NUMBER}}"

setup-kafka-consumer:
    docker build -t kafka-sumer-img -f kafkaDockerfile .
    docker run --name kafka-consumer --network flinkplayground_projectnetwork -v .:/data -it kafka-sumer-img bash
    # sudo docker compose -f docker-compose.yml up -d consumer
    # docker exec -it kafka-consumer bash -c "python /app/kafkaConsumer.py"   

# Build the Flink job Docker image
build-docker-image:
    docker build -t projectflinkimage -f pyflinkJobDockerfile .

# Run Flink cluster in Docker i.e. start the jobmanager
run-jobmanager:
    docker run -d -t \
    --name jobmanager \
    --hostname jobmanager \
    -p 8081:8081 \
    --expose 6123 \
    --network flinkplayground_projectnetwork \
    -v .:/data \
    --env FLINK_PROPERTIES="jobmanager.rpc.port: 6123" \
    projectflinkimage \
    jobmanager

# Run flink taskmanager(s)
run-taskmanager HOSTNAME:
    docker run -d -t \
    --name {{HOSTNAME}} \
    --hostname {{HOSTNAME}} \
    --expose 6121 \
    --expose 6122 \
    --network flinkplayground_projectnetwork \
    -v .:/data \
    -v ./flink-conf.yaml:/opt/flink/conf/flink-conf.yaml \
    projectflinkimage \
    taskmanager
 
# Run Flink job in Docker
run-flink-job NUMBER:
    docker exec \
    jobmanager bash -c \
    "/opt/flink/bin/flink run --jarfile=/data/fatjar.jar --python /data/pyflinkKafkaJob.py {{NUMBER}}"

# Monitor Flink cluster
monitor-flink-cluster:
    echo "Access Flink dashboard at http://jobmanager:8081"

# Clean up Docker containers
clean-docker:
    docker stop flink-cluster your-job-container
    docker rm flink-cluster your-job-container

