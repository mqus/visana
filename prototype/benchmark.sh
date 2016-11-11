pushd src
echo "create 1M samples in data/sample_1m.csv"
python3 make_sample.py > ../data/sample_1m.csv
echo "create 100K samples in data/sample_100k.csv"
cat ../data/sample_1m.csv | sed "100002,10000000d" >../data/sample_100k.csv
echo "create 10K samples in data/sample_10k.csv"
cat ../data/sample_1m.csv | sed "10002,10000000d" >../data/sample_10k.csv


popd