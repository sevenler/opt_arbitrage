import time
import csv
import pandas as pd

import pymysql
from clickhouse_driver import Client


def data():
    f = "/Users/daniel/Desktop/opt_arbitrage/data/cfe/2021/wsSF1207fb/SFIC2112.csv"
    sql = '''insert into cfe (id, Code,Time,Price,Volume,Amount,OI,SP1,SV1,BP1,BV1,isBuy) values'''
    with open(f, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(spamreader, None)
        values = []
        for i, row in enumerate(spamreader):
            t = pd.to_datetime(row[0])
            values.append('''({}, '{}', '{}',{},{}, {},{},{},{},{},{},{})'''.format(
                i, 'IC2112', t, row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))
    return sql + ",".join(values)


def pickup_db(storage):
    if storage == "mysql":
        mysql = pymysql.connect(host='127.0.0.1', user='root', password='root', database='stock_arbitrage',
                                autocommit=True)
        db = mysql.cursor()
    elif storage == "clickhouse":
        client = Client('127.0.0.1', database='stock_arbitrage')
        db = client
    else:
        raise Exception("error storage")
    return db


if __name__ == "__main__":
    dt = data()
    t0 = time.perf_counter()
    pickup_db("mysql").execute(dt)
    t1 = time.perf_counter()
    pickup_db("clickhouse").execute(dt)
    t2 = time.perf_counter()
    print("mysql sink duration:%s" % (t1 - t0))
    print("clickhouse sink duration:%s" % (t2 - t1))
    # 26647 rows
    # mysql sink duration:0.2706547380000002
    # clickhouse sink duration:0.08111784799999988
