#!/bin/bash
NS3_VERSION="3.39"
INSTALL_DIR="/home/student"
NS3_LINK_DIR="/home/student/_ns3"

sudo apt update && \
  sudo apt install -y gcc \
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
  python3-venv \
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
  curl \
  sudo \
  xpra \
  iproute2 \
  wget \


wget https://www.nsnam.org/releases/ns-allinone-$NS3_VERSION.tar.bz2 && tar -jxvf ns-allinone-$NS3_VERSION.tar.bz2

# RUN chown -fR student:student ns-allinone-$NS3_VERSION/

cd $INSTALL_DIR/ns-allinone-$NS3_VERSION || exit
./build.py --enable-examples --enable-tests

ln -s $INSTALL_DIR/ns-allinone-$NS3_VERSION/ns-$NS3_VERSION $NS3_LINK_DIR

cd $INSTALL_DIR || exit
export VIRTUAL_ENV=$INSTALL_DIR/venv-ns3
python3 -m venv $VIRTUAL_ENV
# echo "export PATH=""$VIRTUAL_ENV/bin:$PATH:$INSTALL_DIR/ns-allinone-$NS3_VERSION/ns-$NS3_VERSION" >> /home/student/.profile
source $VIRTUAL_ENV/bin/activate
pip install ns3 loguru jupyterlab

rm ns-allinone-$NS3_VERSION.tar.bz2


