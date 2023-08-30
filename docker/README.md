# Simple Dockerfile for NS-3 Simulator

This repo contains a simple Dockerfile that can be used to build a Ubuntu 22.04 container with NS-3 Simulator.
Currently, NS-3 version 3.39 is downloaded.

## How to build

```Bash
$ docker build -t ns3 .
```

## How to run

```Bash
$ docker run --rm -it ns3
```
