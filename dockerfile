FROM ubuntu:18.04
RUN apt-get update && apt-get install \
  -y --no-install-recommends python3 python3-virtualenv

ENV VIRTUAL_ENV=/opt/venv

# ----- lines above are same, lines below are different -----

RUN python3 -m virtualenv --python=/usr/bin/python3 $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"




COPY forum .
COPY requirements.txt requirements.txt
RUN python3 -m pip install --upgrade pip \
&& python3 -m pip install -r requirements.txt --no-cache-dir
CMD [ "python", "/main-program/loop_collect.py" ]

