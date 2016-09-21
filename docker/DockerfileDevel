# Pull base image.
FROM ubuntu:16.04

ENV DEBIAN_FRONTEND noninteractive

# Install developer tools, alse add-re
RUN apt-get update
# install basics
RUN apt-get install -y software-properties-common
RUN apt-get install -y git
RUN apt-get install -y wget
RUN apt-get install -y gcc
RUN apt-get install -y python
RUN apt-get install -y python-dev
RUN apt-get install -y clang-format

# install oracle java
RUN add-apt-repository -y ppa:webupd8team/java
RUN apt-get update
RUN echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | debconf-set-selections
RUN apt-get install -y oracle-java8-installer

WORKDIR /tmp
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python get-pip.py
RUN pip install numpy
RUN pip install mpmath
RUN git clone https://github.com/sympy/sympy.git
WORKDIR /tmp/sympy
RUN python setup.py install
WORKDIR /tmp

ENV MAVEN_VERSION 3.3.9
RUN mkdir -p /usr/share/maven
RUN wget http://mirror.softaculous.com/apache/maven/maven-3/$MAVEN_VERSION/binaries/apache-maven-$MAVEN_VERSION-bin.tar.gz
RUN tar -xzf apache-maven-$MAVEN_VERSION-bin.tar.gz -C /usr/share/maven --strip-components=1
RUN ln -s /usr/share/maven/bin/mvn /usr/bin/mvn

# Define commonly used JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/java-8-oracle
ENV MAVEN_HOME /usr/share/maven

# Define working directory.
WORKDIR /data
RUN git clone https://github.com/nest/nestml.git

WORKDIR /data/nestml
RUN mvn install
ENV NESTML 'java -jar /data/nestml/target/nestml.jar'

# create a non-root user named tester, 
# give them the password "tester" put them in the sudo group
RUN useradd -d /home/tester -m -s /bin/bash tester && echo "tester:tester" | chpasswd && adduser tester sudo

# start working in the "tester" home directory
WORKDIR /home/tester

# Make the files owned by tester
RUN chown -R tester:tester /home/tester

# Switch to your new user in the docker image
USER tester


# Define default command.
ENTRYPOINT ["java", "-jar", "/data/nestml/target/nestml.jar", "/nestml", "--target", "/nestml/result"]
