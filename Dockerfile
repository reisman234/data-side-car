FROM python:3.9-alpine

RUN apk update

WORKDIR /opt/data-side-car/
ADD requirements.txt /opt/data-side-car/
RUN pip3 install -r requirements.txt

ADD main.py /opt/data-side-car/
ADD progress.py /opt/data-side-car/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9999"]