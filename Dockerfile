FROM python:latest

WORKDIR /install
RUN wget https://www.dabeaz.com/ply/ply-3.11.tar.gz --no-check-certificate
RUN tar -xvf ply-3.11.tar.gz
WORKDIR /install/ply-3.11
RUN python setup.py install
RUN pip install mako

WORKDIR /code
COPY Source/Generator/ ./
COPY Docker/entrypoint.sh entrypoint.sh
RUN ls .

WORKDIR /run
ENTRYPOINT ["/code/entrypoint.sh"]
CMD ["10","200"]
