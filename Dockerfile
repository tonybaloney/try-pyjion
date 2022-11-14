ARG DOTNET_VERSION=7.0.100
FROM python:3.10-slim-buster
ARG DOTNET_VERSION
RUN echo "Building Pyjion with .NET $DOTNET_VERSION"
COPY . /api
WORKDIR /api

ENV TZ=Europe/London
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get -y update && apt-get install -y software-properties-common build-essential && apt-get -y update && apt-get install -y wget unzip bzip2 && apt-get clean -y && rm -rf /var/lib/apt/lists/*
RUN wget https://dotnetcli.azureedge.net/dotnet/Sdk/${DOTNET_VERSION}/dotnet-sdk-${DOTNET_VERSION}-linux-x64.tar.gz
RUN mkdir -p dotnet && tar zxf dotnet-sdk-${DOTNET_VERSION}-linux-x64.tar.gz -C dotnet
ENV DOTNET_ROOT=/api/dotnet

COPY ./api/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./api /code/app
CMD ["python", "-m", "gunicorn", "--conf", "api/gunicorn_conf.py", "--bind", "0.0.0.0:80", "api.main:app"]
