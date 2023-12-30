FROM python:3.10-slim

RUN apt-get update 

COPY . .

RUN pip install poetry 

EXPOSE 8501

ENTRYPOINT ["bin/bash"]