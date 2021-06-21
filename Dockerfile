FROM locustio/locust

RUN python -m pip install numpy
RUN python -m pip install pandas