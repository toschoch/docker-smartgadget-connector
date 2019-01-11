Docker Sensirion SmartGadget BLE-Database Connector
===============================
author: Tobias Schoch

[![Build Status](https://drone.github.dietzi.mywire.org/api/badges/toschoch/docker-smartgadget-connector/status.svg)](https://drone.github.dietzi.mywire.org/toschoch/docker-smartgadget-connector)

Overview
--------

Application to connect to nearby Sensirion SmartGadgets with BLE, periodically read their data and writes it to a database (InfluxDB).


Change-Log
----------
##### 1.0.0
* fix battery data annotation & documentation
* added battery value push and made influxdb connection configurable
* removed global dictionary for tasks
* added glib2.0 to raspbian image
* fixed drone docker plugin version
* drone docker plugin update
* switched to raspian/stretch for updated python3 version
* added build args
* added Dockerfiles into build description
* fixed rpi version of dockerfile
* added a docker file for raspberry
* working dockerfile

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
Configuration
-------

* `INFLUXDB` adress of influxdb to store data e.g. data.company.com
* `INFLUXDB_PORT` port to use for communcation, default 8086
* `SCAN_INTERVAL` interval to scan for devices in minutes, default 5 
* `DOWNLOAD_INTERVAL` interval to download data from devices in hours, default 4

Example
-------

The container needs access to the bluetooth devices therefore the special
capabilites and the host net is required.

```
docker run --cap-add=SYS_ADMIN --cap-add=NET_ADMIN --net=host -it shocki/smartgadget-connector
```