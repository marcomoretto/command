FROM python:3

EXPOSE 8888

RUN mkdir /app
RUN mkdir -p /root/.jupyter/custom
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN apt-get update
RUN apt-get -y install openjdk-7-jdk
ENV JDK_HOME='/usr/lib/jvm/java-7-openjdk-amd64/'
ENV JAVA_HOME='/usr/lib/jvm/java-7-openjdk-amd64/'
RUN pip3 install --upgrade pip
RUN pip3 install Cython==0.28.1
RUN pip3 install -r requirements.txt
RUN pip3 install jupyter

COPY jupyter/jupyter_notebook_config.py /root/.jupyter/
COPY jupyter/custom.js /root/.jupyter/custom/

COPY . /app

WORKDIR /app/notebook

CMD jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root
