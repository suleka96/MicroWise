#!/bin/bash
  echo Starting Testing Script...

  containerName=microWiseContainer
  containerTag=suleka96/microwise
  containerTagLatest=suleka96/microwise:latest

  echo Buiding Microservice Docker Image....
  docker build . -t ${containerTag}
  sleep 10

  #run microservice
  echo Running Microservice Container...
  docker run -d  --rm --name ${containerName} --memory=$1 --cpus=$2 -p 8080:8080 -e JAVA_OPTIONS="$(cat $(pwd)/$3)" ${containerTagLatest}
  sleep 15

  #run test
  echo Running JMeter Container...
  export volume_path=$(pwd)/jmeter_resource && export jmeter_path=/jmeter && docker run --rm --name jmeterContainer --memory=$4 --cpus=$5 -p 8081:8081 --link ${containerName} -e JAVA_OPTS="$(cat $(pwd)/$9)" --volume ${volume_path}:${jmeter_path} egaillardon/jmeter -JConcurrentUsers=$6 -JTestTime=$8 -JHostName=${containerName} --nongui -t microwise.jmx -l jmeter_results.jtl -q user.properties
  sleep 10

  #jtl split
  echo Splitting JTL File...
  java -jar $(pwd)/jtl-splitter-0.4.6-SNAPSHOT.jar -f $(pwd)/jmeter_resource/jmeter_results.jtl -s -t $7;

  echo Stopping Microservice Container...
  docker stop ${containerName}
  sleep 10

  #deleteing log files
  rm -f $(pwd)/jmeter_resource/jmeter_results.jtl
  rm -f $(pwd)/jmeter_resource/*.log

  echo Ending Testing Script...
