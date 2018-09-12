# vim:set et ts=2 sw=2 syntax=dockerfile:

FROM       docker.demigame.com/base/python:3.4v6
MAINTAINER djluo <dj.luo@baoyugame.com>

#COPY ./requirements.txt /dist/
RUN python3 -m venv /venv \
    && /venv/bin/pip install -i https://mirrors.aliyun.com/pypi/simple/ --upgrade pip==10.0.1

COPY ./dist/ftp_v5-1.2.0v1-py3-none-any.whl /dist/
RUN /venv/bin/pip install /dist/ftp_v5-1.2.0v1-py3-none-any.whl

COPY ./python.py /
CMD ["/python.py"]
