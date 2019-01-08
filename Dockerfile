FROM python:3 as builder

# Install dependencies
ARG PIP_INDEX
ARG PIP_HOST

COPY requirements.txt .
RUN mkdir /wheels
RUN pip wheel --index-url http://${PIP_HOST}/${PIP_INDEX} \
              --trusted-host ${PIP_HOST} \
              --wheel-dir /wheels \
              -r requirements.txt

FROM python:3-slim
MAINTAINER Tobias Schoch <tobias.schoch@vtxmail.ch>


# Install dependencies
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN apt-get update && apt-get install bluez -y && pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

# copy app
COPY app /app
WORKDIR /app

CMD ["python", "main.py"]