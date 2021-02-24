FROM python:3.8

# install motuclient
# TODO: cleanup cache?
RUN python -m pip install motuclient==1.8.6

# drop this later, but we might need a bash for debugging
# TODO: cleanup cache?
RUN apt update && apt install -y bash

COPY motupydownload.py .
ENTRYPOINT python motupydownload.py