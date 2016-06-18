FROM ubuntu:xenial

RUN apt-get -y update && apt-get install -y python-pip
RUN apt-get install -y python-dev libxml2-dev libxslt1-dev zlib1g-dev
RUN apt-get install -y python-setuptools
RUN apt-get install -y python-openssl

RUN easy_install lxml

ADD requirements.txt /
RUN pip install -r requirements.txt

ADD MITscraper /MITscraper
ADD database_setup.py /
ADD main_database.db /
ADD project.py /
ADD static /static
ADD templates /templates
ADD client_secrets.json /
ADD grading.py /

CMD python database_setup.py
CMD python project.py
