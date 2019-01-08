import logging
from influxdb import InfluxDBClient

log = logging.getLogger(__name__)


def upload_missing_data_to_db(client : InfluxDBClient, data, interval, topic, tags, database='telegraf'):

    t0 = data[-1][1]

    qry = 'SELECT "value" FROM "{}"."autogen"."{}" WHERE time > {}ms'.format(database, topic, t0 - interval // 2)
    log.debug("search db for existing data: {}".format(qry))
    rs = client.query(qry, epoch='ms')

    db_iter = rs.get_points()

    seq_p = 2000
    seq_tp = seq_p
    tnow = data[0][1]

    to_send = []
    for seq, tn, vn in reversed(data):
        not_in_db = True

        while seq_p >= seq:

            if seq_p == seq and abs(seq_tp - seq_p) < 0.01:
                not_in_db = False
                break

            try:
                p = next(db_iter)
            except StopIteration:
                break

            tp = p['time'] - interval
            seq_tp = (tnow - tp) / interval
            seq_p = int(round(seq_tp))

        if not_in_db:
            payload = {
                "measurement": topic,
                "time": tn,
                "fields": {
                    "value": vn
                }
            }
            to_send.append(payload)

    log.info("found {} datapoints not yet in db. Upload to '{}'...".format(len(to_send), topic))
    client.write_points(to_send, tags=tags, database=database, time_precision='ms')
