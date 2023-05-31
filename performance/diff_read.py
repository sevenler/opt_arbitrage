import time
import csv
import pandas as pd

if __name__ == "__main__":
    f = "/Users/daniel/Desktop/opt_arbitrage/data/cfe/2021/wsSF1213fb/SFIH2201.csv"
    # columns
    # Time	Price	Volume	Amount	OI	SP1	SV1	BP1	BV1	isBuy

    t0 = time.perf_counter()
    df = pd.read_csv(f, header=0)
    t1 = time.perf_counter()
    rows = df.to_dict('records')
    t2 = time.perf_counter()
    values = []
    for i, row in enumerate(rows):
        values.append(
            [row['Time'], row['Price'], row['Volume'], row['Amount'], row['OI'], row['SP1'], row['SV1'], row['BP1'],
             row['BV1'], row['isBuy']])
    t3 = time.perf_counter()
    print("read file by pandas duration:%s %s %s total:%s" % (t1 - t0, t2 - t1, t3 - t2, t3 - t1))

    t0 = time.perf_counter()
    with open(f, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        t1 = time.perf_counter()
        values = []
        for row in spamreader:
            values.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]])
    t2 = time.perf_counter()
    print("read file by csv reader duration:%s %s total:%s" % (t1 - t0, t2 - t1, t2 - t0))

    # 26647 rows
    # read file by pandas duration:0.03642178400000007 0.271032697 0.02117243099999999 total:0.292205128
    # read file by csv reader duration:0.00022000299999991313 0.05662911699999995 total:0.056849119999999864
