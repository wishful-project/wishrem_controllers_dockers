FROM ubuntu:16.04

RUN apt-get update && apt-get install -y apt-transport-https

RUN apt-get install -y python3

RUN apt-get install -y python3-numpy

RUN apt-get install -y python3-scipy

RUN apt-get install -y python3-pip

RUN apt-get install -y wget

RUN apt-get install -y git

WORKDIR /app

COPY . /app/

RUN pip3 install git+https://github.com/uniflex/uniflex@master

RUN pip3 install git+https://github.com/wishful-project/pyre@master

RUN pip3 install git+https://github.com/uniflex/app_discovery_pyre@master

RUN pip3 install git+https://github.com/wishful-project/wishrem_rem_events@master

CMD ["uniflex-agent", "--config", "/app/config_rrm.yaml"]
