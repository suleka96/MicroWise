FROM openjdk:8-jdk-alpine
ADD  ./sort-0.0.1-SNAPSHOT.jar /usr/src/microwise/
WORKDIR /usr/src/microwise
EXPOSE 8080
CMD java $JAVA_OPTIONS -jar sort-0.0.1-SNAPSHOT.jar