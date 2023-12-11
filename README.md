# DSDFlinkProject
COMP 6231: Distributed System Design Group Project

### To run:
`git clone`\
`cd DSDFlinkProject`\
(Note: Please change the String videoInPath and videoOutPath in VideoProcessingJob.java before building the jar) \
`mvn clean package`

`flink run -c org.example.flink.VideoProcessingJob path/to/FlinkPlayground-1.0-SNAPSHOT-shaded.jar`
