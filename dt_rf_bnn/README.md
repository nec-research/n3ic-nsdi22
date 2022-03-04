# Requirements (tested on Ubuntu 20.04.3 LTS)

```
sudo apt update
sudo apt install -y python3-pip python3-dev
pip install notebook numpy sklearn matplotlib pandas larq tensorflow==2.5
python3 -c "import tensorflow as tf;print(tf.reduce_sum(tf.random.normal([1000, 1000])))"
```

## UNSW-NB15 dataset

Download `UNSW-NB15` dataset from https://research.unsw.edu.au/projects/unsw-nb15-dataset.

Put `UNSW_NB15_testing-set.csv` and `UNSW_NB15_training-set.csv` from `UNSW_NB15 - CSV Files/a part of training and testing set` into `datasets/UNSW_NB15`.

## UNSW-IoT dataset

Download `UNSW-IoT` dataset from https://iotanalytics.unsw.edu.au/iottraces.html into `datasets/UNSW_IOT` and extract the pcap files using `tar -xf`.
```
set -o xtrace
cd datasets/UNSW_IOT
wget https://iotanalytics.unsw.edu.au/iottestbed/pcap/filelist.txt -O filelist.txt
cat filelist.txt | egrep -v "(^#.*|^$)" | xargs -n 1 wget
ls *.tar.gz | xargs -n 1 tar -xf
rm *.tar.gz filelist.txt
```
Extract the features using `argus` and create a single `dataset.csv` file.
```
sudo apt install -y argus-client
for f in *.pcap; do argus -r $f -AZJmR -w $f.argus; done
for f in *.argus; do ra -r $f -u -n -c , -s +dur +sbytes +dbytes +sttl +dttl +sload +dload +spkts +dpkts +smeansz +dmeansz +sintpkt +dintpkt +tcprtt +synack +ackdat +smac +dmac > $f.csv; done
# Get header line from a single CSV file
ls *csv | head -n 1 | xargs -n 1 head -n 1 > dataset_hdr.csv
# Concatenate all the CSV files
awk FNR!=1 *.csv > dataset_data.csv
# Create a single dataset.csv file
cat dataset_hdr.csv dataset_data.csv > dataset.csv
rm *.argus* dataset_hdr.csv dataset_data.csv
```
Finally, download `List_Of_Devices.txt` into the same `datasets/UNSW_IOT` folder.
```
wget https://iotanalytics.unsw.edu.au/resources/List_Of_Devices.txt
```
You are now ready to run the two Jupyter notebooks `sec_dataset.ipynb` and `iot_dataset.ipynb`.
