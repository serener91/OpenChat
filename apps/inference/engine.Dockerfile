FROM ubuntu:latest
LABEL authors="Gukhwan Hyun"
LABEL build_date="2025-03"

WORKDIR /app

COPY ./model_setting.sh .

RUN apt update && apt install -y vim
RUN apt install -y python3.12 git
RUN apt-get -y install python3-pip
RUN pip install -U pip

RUN git clone https://github.com/vllm-project/vllm.git
RUN cd vllm && VLLM_USE_PRECOMPILED=1 pip install --editable .

RUN pip install git+https://github.com/huggingface/transformers.git