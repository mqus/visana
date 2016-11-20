#!/usr/bin/env sh
if [ -z $1 ];then
	echo "Usage:
	prototype/profile.sh small 		runs only tests on files with 10k up to 1M lines
	prototype/profile.sh big 		runs all tests (will take up a significant amount of disk and memory space!!)"
	exit 1
fi

pushd src >/dev/null
if [ $1 == "big" ];then
	echo "	WARNING: This profiler will temporarily take up 5GB of Disk space in data/ .
	If you just want to run the small version (up to 50mb of Disk Space), run 'prototype/profile.sh small'."

	echo "create 100M samples in data/sample_100m.csv (may take ~10-15 minutes)"
	python3 make_sample.py > ../data/sample_100m.csv
	echo "create 10M samples in data/sample_10m.csv"
	cat ../data/sample_100m.csv | sed "2,90000002d" >../data/sample_10m.csv
fi
echo "create 1M samples in data/sample_1m.csv"
python3 make_sample.py 1000000 > ../data/sample_1m.csv
#cat ../data/sample_10m.csv | sed "2,9000002d" >../data/sample_1m.csv
echo "create 100K samples in data/sample_100k.csv"
cat ../data/sample_1m.csv | sed "2,900002d" >../data/sample_100k.csv
echo "create 10K samples in data/sample_10k.csv"
cat ../data/sample_100k.csv | sed "2,90002d" >../data/sample_10k.csv

if [ $1 == "big" ];then
	echo "Profile program with 100M Samples: Reading Input..."
	python3 profile.py ../data/sample_100m.csv
	echo "Profile program with 10M Samples: Reading Input..."
	python3 profile.py ../data/sample_10m.csv
fi
echo "Profile program with 1M Samples: Reading Input..."
python3 profile.py ../data/sample_1m.csv
echo "Profile program with 100k Samples: Reading Input..."
python3 profile.py ../data/sample_100k.csv
echo "Profile program with 10k Samples: Reading Input..."
python3 profile.py ../data/sample_10k.csv
echo "Done. Delete temporary files with 'rm data/sample*' by yourself, they are retained for inspection."
popd >/dev/null
