FROM ubuntu:xenial

RUN apt-get -y update && apt-get install -y python-pip
RUN apt-get install -y python-dev libxml2-dev libxslt1-dev zlib1g-dev
RUN apt-get install -y python-setuptools

RUN easy_install lxml

ADD requirements.txt /
RUN pip install -r requirements.txt

ADD database_setup.py /
ADD MITscraper /
RUN python database_setup.py

ADD project.py /
ADD static /
ADD templates /
CMD python project.py
