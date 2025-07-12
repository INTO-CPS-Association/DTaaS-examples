# Mass Spring Damper

The pipeline for this Digital Twin consists of a single stage , where an ubuntu 24 image is created , environment is provisioned using the lifecycle/create script , The digital twin is executed using lifecycle/execute script and the outputs that are created are saved as artifacts . The execution of lifecycle/clean has been commented out in this implementation as this is an example and we want to demonstrate the working of DT pipelines. Also the lifecycle/clean would delete the outputs, before we can save them in this one staged implementation. 

To make the DT work , you need to change the path at digital_twins/mass-spring-damper/cosim.json with your own path . ie , 
change file:///builds/user/dtaas_examples/models/MassSpringDamper1.fmu

to file://{CI_PROJECT_DIR}/models/MassSpringDamper1.fmu