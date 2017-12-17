FROM ryankurte/docker-ns3:latest

RUN apt-get update && \
    apt-get install -y \
    nano \
    qt5-default \
    python-pygraphviz \
    python-kiwi \
    python-pygoocanvas \
    libgoocanvas-dev \
    ipython \
    openmpi-bin \
    openmpi-common \
    openmpi-doc \
    libopenmpi-dev \
    uncrustify \
    doxygen \
    graphviz \
    imagemagick \
    texlive \
    texlive-extra-utils \
    texlive-latex-extra \
    texlive-font-utils \
    texlive-lang-portuguese \
    dvipng \
    python-sphinx \
    dia

RUN apt-get -y install wget
RUN cd /tmp && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \
    apt-get install -y gccxml python-pygccxml python-gnome2 python-rsvg

RUN pip install matplotlib

ADD manet_routing_compare.py /usr/ns3/ns-3.26/

WORKDIR /usr/ns3/ns-3.26

VOLUME ["/usr/ns3/ns-3.26/work"]

CMD ["./waf", "--pyrun", "manet_routing_compare.py"]
