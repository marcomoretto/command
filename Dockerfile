FROM python:3.6.8-jessie

EXPOSE 80

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN apt-get update
RUN apt-get -y install openjdk-7-jdk
ENV JDK_HOME='/usr/lib/jvm/java-7-openjdk-amd64/'
ENV JAVA_HOME='/usr/lib/jvm/java-7-openjdk-amd64/'
RUN pip3 install --upgrade pip
RUN pip3 install Cython==0.28.1
RUN pip3 install -r requirements.txt

COPY . /app
