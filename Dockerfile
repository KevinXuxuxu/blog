FROM ubuntu:20.04

RUN apt-get update \
    && apt-get install software-properties-common -y \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install python3.8 python3-distutils wget -y

RUN wget https://bootstrap.pypa.io/get-pip.py \
    && python3 get-pip.py

COPY requirements.txt /root/

RUN pip install -r /root/requirements.txt
