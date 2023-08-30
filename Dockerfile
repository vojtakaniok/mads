FROM ubuntu:22.04
LABEL version = "0.1"
LABEL description = "Docker image of ns3 running on Ubuntu 22.04"
LABEL author = "jan@rozhon.eu"

ARG NS3_VERSION="3.39"

# install dependencies based on https://www.nsnam.org/wiki/Installation
RUN apt update && \
  DEBIAN_FRONTEND=noninteractive TZ=Europe/Prague apt install -y gcc \
  g++ \
  python3 \
  python3-dev \
  python3-pip \
  cmake \
  ninja-build \
  git \
  ccache \
  gir1.2-goocanvas-2.0 \
  python3-gi \
  python3-gi-cairo \
  python3-pygraphviz \
  gir1.2-gtk-3.0 \
  ipython3 \
  python3-setuptools \
  pkg-config \
  sqlite \
  sqlite3 \
  libsqlite3-dev \
  qtbase5-dev \
  qtchooser \
  qt5-qmake \
  qtbase5-dev-tools \
  mercurial \
  unzip \
  gdb \
  valgrind \
  clang-format \
  doxygen \
  graphviz \
  imagemagick \
  texlive \
  texlive-extra-utils \
  texlive-latex-extra \
  texlive-font-utils \
  dvipng \
  latexmk \
  python3-sphinx \
  dia \
  gsl-bin \
  libgsl-dev \
  libgslcblas0 \
  tcpdump \
  libxml2 \
  libxml2-dev \
  libgtk-3-dev \
  vtun \
  lxc \
  uml-utilities \
  libboost-all-dev \
  mc \
  wget

# create user student and set password
RUN groupadd -r student && \
	useradd -m -d /home/student -g student student

RUN echo "student:student" | chpasswd

#RUN mkdir -p /usr/ns3
WORKDIR /usr

RUN wget https://www.nsnam.org/releases/ns-allinone-$NS3_VERSION.tar.bz2 && tar -jxvf ns-allinone-$NS3_VERSION.tar.bz2

RUN chown -fR student:student ns-allinone-$NS3_VERSION/

RUN cd ns-allinone-$NS3_VERSION/ns-$NS3_VERSION && \
	./ns3 configure --build-profile=debug --disable-werror --enable-examples --enable-tests 

RUN ln -s /usr/ns-allinone-$NS3_VERSION/ns-$NS3_VERSION /usr/ns3

# final cleanup
RUN apt clean && \
	rm -rf /var/lib/apt/lists/* && \
	rm ns-allinone-$NS3_VERSION.tar.bz2
