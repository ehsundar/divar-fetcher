FROM python:3.10.5-bullseye

WORKDIR /root/divar-fetcher

ADD requirements.txt .
RUN pip install -r requirements.txt
RUN pip install python-telegram-bot --pre

ADD . .

CMD ["python", "main.py"]
