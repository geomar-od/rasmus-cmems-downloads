FROM python:3.8

# install motuclient
# TODO: cleanup cache?
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# drop this later, but we might need a bash for debugging
# TODO: cleanup cache?
RUN apt update && apt install -y bash

RUN mkdir -p /opt/motupydownload/
COPY motupydownload.py /opt/motupydownload/.
ENTRYPOINT ["python", "/opt/motupydownload/motupydownload.py"]