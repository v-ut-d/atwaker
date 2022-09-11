FROM python:3.10-bullseye as builder

WORKDIR /app

COPY requirements.lock /app
RUN pip3 install -r requirements.lock

FROM python:3.10-slim-bullseye as runner

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

COPY AtWaker.py /app

CMD ["python", "/app/AtWaker.py"]