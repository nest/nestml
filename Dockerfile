FROM alpine:3.4

RUN apk update
RUN apk --update add openjdk8
RUN apk --update add git
RUN apk --update add wget
RUN apk --update add python-dev
RUN apk --update add clang # for clang-format
RUN apk --update add g++   # is required by sympy
RUN apk --update add sudo

# Set environment
#ENV JAVA_HOME /usr/bin/java
#ENV PATH ${PATH}:${JAVA_HOME}/bin

# Install mpmath, required by sympy
WORKDIR /tmp
RUN wget https://bootstrap.pypa.io/get-
.py
RUN python get-pip.py
RUN pip install mpmath
RUN pip install sympy

WORKDIR /tmp
ENV MAVEN_VERSION 3.3.9
RUN mkdir -p /usr/share/maven
RUN wget http://mirror.softaculous.com/apache/maven/maven-3/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz
RUN tar -xzf apache-maven-$MAVEN_VERSION-bin.tar.gz -C /usr/share/maven
RUN ln -s /usr/share/maven//apache-maven-$MAVEN_VERSION/bin/mvn /usr/bin/mvn
ENV MAVEN_HOME /usr/share/maven

# Define working directory.
WORKDIR /data
RUN git clone https://github.com/nest/nestml.git
WORKDIR /data/nestml
RUN mvn install

