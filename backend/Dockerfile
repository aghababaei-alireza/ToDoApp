FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /backend

COPY requirements.txt /backend/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /backend

EXPOSE 8000