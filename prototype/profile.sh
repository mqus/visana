pushd src
echo "WARNING: This profiler will temporarily take up 5GB of Disk space in data/"
echo "create 100M samples in data/sample_100m.csv (may take ~10-15 minutes)"
python3 make_sample.py > ../data/sample_100m.csv
echo "create 10M samples in data/sample_10m.csv"
cat ../data/sample_100m.csv | sed "2,90000002d" >../data/sample_10m.csv
echo "create 1M samples in data/sample_1m.csv"
cat ../data/sample_10m.csv | sed "2,9000002d" >../data/sample_1m.csv
echo "create 100K samples in data/sample_100k.csv"
cat ../data/sample_1m.csv | sed "2,900002d" >../data/sample_100k.csv
echo "create 10K samples in data/sample_10k.csv"
cat ../data/sample_100k.csv | sed "2,90002d" >../data/sample_10k.csv

echo "Profile program with 100M Samples: Reading Input..."
python3 profile.py ../data/sample_100m.csv
echo "Profile program with 10M Samples: Reading Input..."
python3 profile.py ../data/sample_10m.csv
echo "Profile program with 1M Samples: Reading Input..."
python3 profile.py ../data/sample_1m.csv
echo "Profile program with 100k Samples: Reading Input..."
python3 profile.py ../data/sample_100k.csv
echo "Profile program with 10k Samples: Reading Input..."
python3 profile.py ../data/sample_10k.csv
echo "Done. Delete temporary files with 'rm data/sample*' by yourself, they are retained for inspection."
popd