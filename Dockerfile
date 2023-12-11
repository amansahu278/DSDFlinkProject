FROM apache/flink:scala_2.12-java17

CMD ["/opt/flink/bin/jobmanager.sh", "start-foreground"]

