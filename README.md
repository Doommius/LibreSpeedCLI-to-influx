# LibreSpeedCLI to influx

Speedtest for LibreSpeed with InfluxDB as the data store.

It is currently setup to run a test towards my ISP (https://speedtest.nal-medienet.dk/)

To use this code you'll need to download or build the librespeed/speedtest-cli

```shell script
git clone https://github.com/librespeed/speedtest-cli.git
cd speedtest-cli
./build.sh
cd ..
mv speedtest-cli/out/ librespeed-cli-* .
```

Run the script via

```shell script
python main.py
```

based on https://github.com/aidengilmartin/speedtest-to-influxdb
