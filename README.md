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
git clone <git-url>
```
build the docker image
```
docker build . -t docker-smartgadget-connector
```

Example
-------

run a container of the image
```
docker run -v ... -p ... docker-smartgadget-connector
```