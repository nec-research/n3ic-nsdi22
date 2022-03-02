# Requirements (tested on Ubuntu 20.04.3 LTS)

```
sudo apt update
sudo apt install -y python3-pip python3-dev
pip install notebook numpy sklearn matplotlib pandas larq tensorflow==2.5
python3 -c "import tensorflow as tf;print(tf.reduce_sum(tf.random.normal([1000, 1000])))"
```

# UNSW-NB15 dataset

Download `UNSW-NB15` dataset from https://research.unsw.edu.au/projects/unsw-nb15-dataset.

Put `UNSW_NB15_testing-set.csv` and `UNSW_NB15_training-set.csv` from `UNSW_NB15 - CSV Files/a part of training and testing set` into `datasets/UNSW_NB15`.

# UNSW-IoT dataset

Download `UNSW-IoT` dataset from https://iotanalytics.unsw.edu.au/iottraces.html.

Put all the `tar.gz` files, as well as `List_Of_Devices.txt`, in `datasets/UNSW_IOT` and extract the pcap files using `tar -xf`.
Extract all the features into a single `dataset.csv` file using `argus`.

```
sudo apt install -y argus-client
cd datasets/UNSW_IOT
argus -r *.pcap -AZJmR -w argusfile
ra -r argusfile -u -n -c , -s +dur +sbytes +dbytes +sttl +dttl +sload +dload +spkts +dpkts +smeansz +dmeansz +sintpkt +dintpkt +tcprtt +synack +ackdat +smac +dmac > dataset.csv
```
