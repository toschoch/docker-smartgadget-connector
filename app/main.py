import datetime
import logging
import os
import time

from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.schedulers.background import BlockingScheduler
from influxdb import InfluxDBClient

from smartgadget.device import SmartGadget
from smartgadget.scanner import SmartGadgetScanner

from helper import upload_missing_data_to_db


INFLUXDB = os.environ['INFLUXDB']
INFLUXDB_PORT = os.environ.get('INFLUXDB_PORT', 8086)
INFLUXDB_NAME = os.environ.get('INFLUXDB_NAME', 'smartgadgets')

SCAN_INTERVAL = int(os.environ.get('SCAN_INTERVAL', 5))  # minutes
SCAN_DURATION = 10  # seconds
DOWNLOAD_INTERVAL = int(os.environ.get('DOWNLOAD_INTERVAL', 4))  # hours

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')

if __name__ == '__main__':

    scheduler = BlockingScheduler(
        executors={
            'default': ThreadPoolExecutor(5),
            'process': ProcessPoolExecutor(max_workers=1)})

    class AppendSmartGadget(SmartGadgetScanner):

        def __init__(self):
            SmartGadgetScanner.__init__(self)
            self.jobs = {}

        def on_appearance(self, dev: SmartGadget):
            logging.info("appearance {}".format(dev))

            if dev.addr not in self.jobs:
                logging.info("add download for {}".format(dev))
                job = scheduler.add_job(AppendSmartGadget.download,
                                        'interval',
                                        args=(dev,),
                                        hours=DOWNLOAD_INTERVAL,
                                        jitter=300,
                                        coalesce=True,
                                        start_date=datetime.datetime.now() + datetime.timedelta(seconds=5),
                                        executor='process',
                                        misfire_grace_time=120)
                self.jobs[dev.addr] = job

            else:
                logging.info("resume download for {}".format(dev))
                self.jobs[dev.addr].resume()

        def on_disappearance(self, dev: SmartGadget):
            logging.info("pause download for {}".format(dev))
            self.jobs[dev.addr].pause()

        @staticmethod
        def download(dev: SmartGadget):
            dev.connect()

            logging.info("connect to db...")
            db = InfluxDBClient(INFLUXDB, INFLUXDB_PORT, INFLUXDB_NAME)

            batt = dev.Battery.read()
            logging.info("{}, Battery: {:02d}%".format(dev, batt))
            data = dev.download_temperature_and_relative_humidity()

            tags = {
                'manufacturer': 'Sensirion',
                'device': 'smartgadget',
                'address': dev.addr,
            }

            _tags = tags.copy()
            _tags.update({
                'quantity': 'battery',
                'unit': dev.Battery.unit,
                'description': dev.Battery.description
            })

            db.write_points([{
                "measurement": "battery_levels",
                "time": int(time.time()*1000),
                "fields": {
                    "value": batt
                }
            }], tags=_tags, time_precision='ms', database=INFLUXDB_NAME)

            _tags = tags.copy()
            _tags.update({
                'quantity': 'temperature',
                'unit': dev.Temperature.unit,
                'description': dev.Temperature.description
            })

            upload_missing_data_to_db(db,
                                      data[dev.Temperature],
                                      dev.Logging.interval,
                                      "temperatures", _tags, INFLUXDB_NAME)


            _tags = tags.copy()
            _tags.update({
                'quantity': 'humidity',
                'unit': dev.RelativeHumidity.unit,
                'description': dev.RelativeHumidity.description
            })

            upload_missing_data_to_db(db,
                                      data[dev.RelativeHumidity],
                                      dev.Logging.interval,
                                      "humidities", _tags, INFLUXDB_NAME)

            dev.disconnect()

    # assure existence of database
    db = InfluxDBClient(INFLUXDB, INFLUXDB_PORT, INFLUXDB_NAME)
    db.create_database(INFLUXDB_NAME)


    scanner = AppendSmartGadget()

    scheduler.add_job(scanner.scan, 'interval', minutes=SCAN_INTERVAL, args=(SCAN_DURATION,),
                      start_date=datetime.datetime.now()+datetime.timedelta(seconds=1))

    scheduler.start()
