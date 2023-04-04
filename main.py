import time
import json
import subprocess
import os
import logging
from datetime import datetime

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

# Creating an object
logger = logging.getLogger()
formatter = logging.Formatter('[%(asctime)16s] [%(filename)20s->%(funcName)25s():%(lineno)-5s]%(levelname)8s: %(message)s')
consolehandler = logging.StreamHandler()
consolehandler.setLevel(logging.INFO)
consolehandler.setFormatter(formatter)
logger.addHandler(consolehandler)
logger.setLevel(logging.INFO)


bucket = "main"
org = "yourorg"
token = "token"
url="https://influx.example.com/"

DB_RETRY_INVERVAL = int(os.environ.get('DB_RETRY_INVERVAL', 60)) # Time before retrying a failed data upload.
DB_DATABASE = "main"

# Speedtest Settings
TEST_INTERVAL = int(os.environ.get('TEST_INTERVAL', 1800))  # Time between tests (in seconds).
TEST_FAIL_INTERVAL = int(os.environ.get('TEST_FAIL_INTERVAL', 60))  # Time before retrying a failed Speedtest (in seconds).

client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)

write_api = client.write_api(write_options=SYNCHRONOUS)

def format_for_influx(cliout):
    data = json.loads(cliout)[0]
    # There is additional data in the output.

    p = influxdb_client.Point("speedtest").tag("server", "nalnet").field("speedtest_download", float(data['download']))
    p.tag("server", "nalnet").field("speedtest_upload", float(data['upload']))
    p.tag("server", "nalnet").field("ping", float(data['ping']))
    p.tag("server", "nalnet").field("jitter", float(data['jitter']))
    p.time(data['timestamp'])
    return p

def main():
    while (1):  # Run a Speedtest and send the results to influxDB indefinitely.
        speedtest = subprocess.run(
            ["./librespeed-cli-linux-amd64","--local-json","servers.json","--server","1","--json"], capture_output=True)

        if speedtest.returncode == 0:  # Speedtest was successful.
            data = format_for_influx(speedtest.stdout)
            try:
                write_api.write(bucket=bucket, org=org, record=data)
                logger.info("Data written to DB successfully")
                time.sleep(TEST_INTERVAL)
            except Exception as ex:
                logger.exception(ex)
                logger.error("Data write to DB failed")
                time.sleep(TEST_FAIL_INTERVAL)
        else:  # Speedtest failed.
            logger.error( "Speedtest failed")
            logger.error(speedtest.stderr)
            logger.info(speedtest.stdout)
            time.sleep(TEST_FAIL_INTERVAL)


if __name__ == '__main__':
    logger.info('Speedtest CLI Data Logger to InfluxDB started')
    main()
