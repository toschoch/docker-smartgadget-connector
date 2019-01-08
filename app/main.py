import datetime
import logging

from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.schedulers.background import BlockingScheduler
from influxdb import InfluxDBClient

from smartgadget.device import SmartGadget
from smartgadget.scanner import SmartGadgetScanner

from helper import upload_missing_data_to_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')

if __name__ == '__main__':

    scheduler = BlockingScheduler(
        executors={
            'default': ThreadPoolExecutor(5),
            'process': ProcessPoolExecutor(max_workers=1)})

    class AppendSmartGadget(SmartGadgetScanner):

        def __init__(self, gadgets={}, jobs={}):
            SmartGadgetScanner.__init__(self, gadgets)
            self.jobs = jobs

        def on_appearance(self, dev: SmartGadget):
            logging.info("appearance {}".format(dev))

            if dev.addr not in self.jobs:
                logging.info("add download for {}".format(dev))
                job = scheduler.add_job(AppendSmartGadget.download,
                                        'interval',
                                        args=(dev,),
                                        hours=4,
                                        jitter=300,
                                        coalesce=True,
                                        start_date=datetime.datetime.now() + datetime.timedelta(seconds=1),
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
            db = InfluxDBClient('nas', 4286, 'telegraf')

            batt = dev.Battery.read()
            logging.info("{}, Battery: {:02d}%".format(dev, batt))
            data = dev.download_temperature_and_relative_humidity()

            # db.write_points([{
            #     "measurement": "smartgadgets/{}/{}".format(dev.addr, 'battery'),
            #     "time": time.time(),
            #     "fields": {
            #         "value": batt
            #     }
            # }], )

            topic = "smartgadgets/{}/{}".format(dev.addr, 'temperature')

            tags = {
                'manufacturer': 'Sensirion',
                'quantity': 'temperature',
                'device': 'smartgadget',
                'address': dev.addr,
                'unit': dev.Temperature.unit,
                'description': dev.Temperature.description
            }

            upload_missing_data_to_db(db, data[dev.Temperature], dev.Logging.interval, topic, tags)

            topic = "smartgadgets/{}/{}".format(dev.addr, 'humidity')

            tags = {
                'manufacturer': 'Sensirion',
                'quantity': 'humidity',
                'device': 'smartgadget',
                'address': dev.addr,
                'unit': dev.RelativeHumidity.unit,
                'description': dev.RelativeHumidity.description
            }

            upload_missing_data_to_db(db, data[dev.RelativeHumidity], dev.Logging.interval, topic, tags)

            dev.disconnect()


    scanner = AppendSmartGadget()

    scheduler.add_job(scanner.scan, 'interval', minutes=5, args=(10,),
                      start_date=datetime.datetime.now()+datetime.timedelta(seconds=1))

    scheduler.start()

    # db = InfluxDBClient('nas', 4286, 'telegraf')
    #
    # scanner = SmartGadgetScanner()
    # scanner.scan(3)
    #
    # print(scanner.gadgets)
    # #
    # g = SmartGadget('e2:07:bc:53:40:61')
    # g.connect()
    #
    # data = g.download_temperature_and_relative_humidity()
    #
    # topic = "smartgadgets/{}/{}".format(g.addr, 'temperature')
    #
    # tags = {
    #     'manufacturer': 'Sensirion',
    #     'quantity': 'temperature',
    #     'device': 'smartgadget',
    #     'address': g.addr,
    #     'unit': g.Temperature.unit,
    #     'description': g.Temperature.description
    # }
    #
    # upload_missing_data_to_db(db, data[g.Temperature], g.Logging.interval, topic, tags)
    #
    # topic = "smartgadgets/{}/{}".format(g.addr, 'humidity')
    #
    # tags = {
    #     'manufacturer': 'Sensirion',
    #     'quantity': 'humidity',
    #     'device': 'smartgadget',
    #     'address': g.addr,
    #     'unit': g.RelativeHumidity.unit,
    #     'description': g.RelativeHumidity.description
    # }
    #
    # upload_missing_data_to_db(db, data[g.RelativeHumidity], g.Logging.interval, topic, tags)
    #
    # g.disconnect()
