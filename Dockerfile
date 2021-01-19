FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install --no-install-recommends -y python3.8 python3-pip python3.8-dev

RUN python3 -m pip install motuclient==1.8

RUN apt update && apt install -y bash

CMD ./MotuClCallPhysModel.sh
CMD ./MotuClCallWaveModel.sh
CMD python3 NetCDF2CSVPhysModel.py
CMD python3 NetCDF2CSVPhysModel.py
