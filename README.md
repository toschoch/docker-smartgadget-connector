Docker Sensirion SmartGadget BLE-Database Connector
===============================
author: Tobias Schoch

Overview
--------

Application to connect to nearby Sensirion SmartGadgets with BLE, periodically read their data and writbase (InfluxDB).


Change-Log
----------
##### 0.0.1
* initial version


Installation / Usage
--------------------
clone the repo:

```
git clone git@github.com:toschoch/docker-smartgadget-connector.git
```
build the docker image
```
docker --build-arg PIP_HOST=.. --build-arg PIP_INDEX=.. build . -t docker-smartgadget-connector
```

Example
-------

The container needs access to the bluetooth devices therefore the special
capabilites and the host net is required.

```
docker run --cap-add=SYS_ADMIN --cap-add=NET_ADMIN --net=host -it shocki/smartgadget-connector
```