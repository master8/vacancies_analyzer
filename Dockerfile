FROM python:3.7

EXPOSE 5000

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app

ENV PYTHONPATH /app
ENV FLASK_APP app.py
CMD python -u -m flask run --host=0.0.0.0 --port=5000