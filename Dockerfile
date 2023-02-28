FROM python:3

WORKDIR /app

ADD requirements.txt /app/requirements.txt
RUN apt-get update && apt-get install -y \
  python3-pip
RUN pip3 install -r requirements.txt

ADD *.py /app/

RUN mkdir -p /app/log
RUN mkdir -p /app/output

CMD ["/bin/sh"]