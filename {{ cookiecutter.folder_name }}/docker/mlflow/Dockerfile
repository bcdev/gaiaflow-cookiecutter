# 🚨 WARNING: Do not modify this Dockerfile without consulting the team! 🚨

FROM python:3.12-slim

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN mkdir -p /mlflow_artifacts
RUN chmod 777 -R /mlflow_artifacts