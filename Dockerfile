FROM python:3.10-slim

RUN apt-get update 

COPY . .

RUN pip install poetry 

ENTRYPOINT ["bin/bash"]