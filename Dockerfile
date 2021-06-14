FROM python:3.8

ARG src="/Stock API Handler"

COPY . ${src}

WORKDIR ${src}

ADD main.py .

ADD venv/Lib/site-packages/commons commons/

RUN pip install aiokafka

RUN pip install requests

RUN pip install pymongo

CMD ["python", "./main.py"]