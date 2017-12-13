FROM ryankurte/docker-ns3:latest

RUN apt-get update && \
    apt-get install -y \
    nano \
    qt5-default \
    python-pygraphviz \
    python-kiwi \
    python-pygoocanvas \
    python-pygccxml \
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

WORKDIR /usr/ns3/ns-3.26

VOLUME ["/usr/ns3/ns-3.26/work"]
