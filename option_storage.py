import csv
import glob
import os
import xlrd
import pymysql
import time
import argparse

from xlrd import xldate_as_tuple
from datetime import datetime
from clickhouse_driver import Client

BATCH_SINK = 15000

class pickup_db(object):
    def __init__(self, storage):
        if storage == "mysql":
            self.client = pymysql.connect(host='127.0.0.1', user='root', password='root', database='stock_arbitrage',
                                          autocommit=True)
            self.cursor = self.client.cursor()
        elif storage == "clickhouse":
            self.client = Client('127.0.0.1', database='stock_arbitrage')
            self.cursor = self.client
        else:
            raise Exception("error storage")

    def __enter__(self):
        return self.cursor

    def __exit__(self, type, value, traceback):
        try:
            self.client.close()
        except Exception as e:
            pass


def read_xlsx(file_path, sheet_name):
    wb = xlrd.open_workbook(file_path)
    sh = wb.sheet_by_name(sheet_name)
    column_map = dict()
    for i, v in enumerate(sh.row_values(1)):
        column_map[i] = v
    rows = []
    for i in range(sh.nrows):
        if i == 0 or i == 1:
            continue
        row = sh.row_values(i)
        data = dict()
        for i1, v in enumerate(row):
            data[column_map[i1]] = v
        rows.append(data)
    return rows


def read_csv(file_path):
    rows = []
    with open(file_path) as f:
        f_csv = csv.DictReader(f)
        for row in f_csv:
            rows.append(row)
    print(rows[:5])
    return rows


def get_all_csv(dir_path):
    file_list = sorted(glob.glob(dir_path, recursive=True))
    return [file for file in file_list if file.endswith('.csv')]


def generate_id(storage, code, tm, pd_index):
    if storage == "mysql":
        # mysql 使用自增长 id
        # 自增长id 写入速度更快
        return 'NULL'
    elif storage == "clickhouse":
        # clickhouse id_format {code}_{day}_{pd_index}
        id = "'{code}_{day}_{pd_index}'".format(
            code=code,
            day=tm.split(" ")[0],
            pd_index=pd_index
        )
        return id


def read_futures(file_path):
    rows = read_xlsx(file_path, sheet_name='期货')
    for row in rows:
        for k, v in row.items():
            # 日期数字转为datetime
            if k == 'lasttrade_date' or k == 'ftdate':
                if isinstance(v, (float)):
                    row[k] = datetime(*xldate_as_tuple(v, 0)).strftime('%Y-%m-%d')
    return rows


def read_options(file_path):
    rows = read_xlsx(file_path, sheet_name='期权')
    for row in rows:
        for k, v in row.items():
            # 日期数字转为datetime
            if k in ['startdate', 'lasttradingdate', 'exe_startdate', 'exe_enddate']:
                if isinstance(v, (float)):
                    row[k] = datetime(*xldate_as_tuple(v, 0)).strftime('%Y-%m-%d')
    return rows


def storge_options(storage, file_path):
    table = 'option'

    options = read_options(file_path)
    with pickup_db(storage) as db:
        for i, option in enumerate(options):
            print(option)
            insert_sql = '''insert into `{}`
                        (Code, Name, tradecode, us_code, us_name, exe_price, startdate, lasttradingdate, 
                        exe_startdate, exe_enddate, exe_ratio)  values
                        ('{}','{}','{}','{}','{}',{},'{}','{}','{}','{}',{})
                        '''.format(table, option['Code'], option['Name'], option['tradecode'],
                                   int(option['us_code']), option['us_name'], option['exe_price'],
                                   option['startdate'],
                                   option['lasttradingdate'], option['exe_startdate'],
                                   option['exe_enddate'],
                                   option['exe_ratio'])
            print(insert_sql)
            db.execute(insert_sql)


def storge_futures(storage, file_path):
    table = 'future'
    futures = read_futures(file_path)

    with pickup_db(storage) as db:
        for i, future in enumerate(futures):
            insert_sql = '''insert into {} (Code, Name, lasttrade_date, ftdate, contractmultiplier) values
                                    ('{}','{}','{}','{}',{})
                                 '''.format(table, future['Code'], future['Name'], future['lasttrade_date'],
                                            future['ftdate'], future['contractmultiplier'])
            print(insert_sql)
            db.execute(insert_sql)


def storge_cfe(storage, dir_path):
    def sink(storage, csv_name):

        t0 = time.perf_counter()
        with pickup_db(storage) as db:
            file_name = os.path.basename(csv_name).split('.')[0]
            start_index = file_name.find('SF') + 2
            code = file_name[start_index:]
            with open(csv_name, newline='') as csvfile:
                # Time	Price	Volume	Amount	OI	SP1	SV1	BP1	BV1	isBuy
                spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(spamreader, None)
                sql = '''insert into cfe (id, Code,Time,Price,Volume,Amount,OI,SP1,SV1,BP1,BV1,isBuy) values'''
                values = []
                for row in spamreader:
                    # t = pd.to_datetime(row[0])
                    t = row[0]
                    i = 0
                    values.append('''({}, '{}','{}',{},{},{},{},{},{},{},{},{})'''
                                  .format(generate_id(storage, code, t, i),
                                          code, t, row[1], row[2],
                                          row[3], row[4], row[5], row[6],
                                          row[7],
                                          row[8], row[9]))
                    if len(values) >= BATCH_SINK:
                        esql = sql + ",".join(values)
                        values = []
                        db.execute(esql)
                esql = sql + ",".join(values)
                db.execute(esql)
        t1 = time.perf_counter()
        print(csv_name, t1 - t0)

    # jobs = [gevent.spawn(sink, storage, csv_name) for csv_name in get_all_csv(dir_path)]
    # gevent.joinall(jobs)
    for csv_name in get_all_csv(dir_path):
        sink(storage, csv_name)


def storge_sh_sz_bin(storage, dir_path):
    def sink(storage, csv_name):

        t0 = time.perf_counter()
        with pickup_db(storage) as db:
            code = os.path.basename(csv_name).split('.')[0]

            with open(csv_name, newline='') as csvfile:
                # Time,Price,Volume,Amount,SP1, SP2,SP3,SP4,SP5,SV1,
                # SV2,SV3,SV4,SV5,BP1,  BP2,BP3,BP4,BP5,BV1,  BV2,BV3,BV4,BV5,isBuy
                spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(spamreader, None)
                sql = '''insert into sh_sz_bin (id, Code,Time,Price,Volume,Amount,
                SP1,SP2,SP3,SP4,SP5,SV1,SV2,SV3,
                SV4,SV5,BP1,BP2,BP3,BP4,BP5,BV1,BV2,BV3,BV4,BV5,isBuy) values'''
                values = []
                for i, row in enumerate(spamreader):
                    t = row[0]
                    value = '''({}, '{}','{}',{},{},{},{},{},{},{},{},{},{},
                    {},{},{},{},{},{},{},{},{},{},{},{},{},{})'''.format(
                        generate_id(storage, code, t, i), code,
                        row[0], row[1], row[2], row[3], row[4],
                        row[5], row[6], row[7], row[8], row[9],
                        row[10], row[11], row[12], row[13], row[14],
                        row[15], row[16], row[17], row[18], row[19],
                        row[20], row[21], row[22], row[23], row[24])
                    values.append(value)
                    if len(values) >= BATCH_SINK:
                        esql = sql + ",".join(values)
                        values = []
                        db.execute(esql)
                esql = sql + ",".join(values)
                db.execute(esql)
        t1 = time.perf_counter()
        print(csv_name, t1 - t0)

    # jobs = [gevent.spawn(sink, storage, csv_name) for csv_name in get_all_csv(dir_path)]
    # gevent.joinall(jobs)
    for csv_name in get_all_csv(dir_path):
        sink(storage, csv_name)


def storge_ashr_option(storage, dir_path):
    def sink(storage, csv_name):
        t0 = time.perf_counter()
        with pickup_db(storage) as db:
            code = os.path.basename(csv_name).split('.')[0]
            with open(csv_name, newline='') as csvfile:
                # Time,Price,Volume,Amount,SP1, SP2,SP3,SP4,SP5,SV1, SV2,SV3,SV4,SV5,BP1, BP2,BP3,BP4,BP5,BV1, BV2,BV3,BV4,BV5,isBuy, OI
                spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(spamreader, None)
                sql = '''insert into ashr_option (id, Code,Time,Price,Volume,Amount,SP1,SP2,SP3,SP4,SP5,SV1,SV2,SV3,
                                                            SV4,SV5,BP1,BP2,BP3,BP4,BP5,BV1,BV2,BV3,BV4,BV5,isBuy,OI) values '''
                values = []
                for i, row in enumerate(spamreader):
                    t = row[0]
                    value = '''({}, '{}','{}',{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{})
                                                    '''.format(generate_id(storage, code, t, i), code, row[0],
                                                               row[1], row[2], row[3], row[4], row[5],
                                                               row[6], row[7], row[8], row[9], row[10],
                                                               row[11], row[12], row[13], row[14], row[15],
                                                               row[16], row[17], row[18], row[19], row[20],
                                                               row[21], row[22], row[23], row[24], row[25])

                    values.append(value)
                    if len(values) >= BATCH_SINK:
                        esql = sql + ",".join(values)
                        values = []
                        db.execute(esql)
                esql = sql + ",".join(values)
                db.execute(esql)
        t1 = time.perf_counter()
        print(csv_name, t1 - t0)

    # jobs = [gevent.spawn(sink, storage, csv_name) for csv_name in get_all_csv(dir_path)]
    # gevent.joinall(jobs)
    for csv_name in get_all_csv(dir_path):
        sink(storage, csv_name)


def td_format(seconds):
    periods = [
        ('year', 60 * 60 * 24 * 365),
        ('month', 60 * 60 * 24 * 30),
        ('day', 60 * 60 * 24),
        ('hour', 60 * 60),
        ('minute', 60),
        ('second', 1)
    ]
    strings = []
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            has_s = 's' if period_value > 1 else ''
            strings.append("%s %s%s" % (period_value, period_name, has_s))
    return ", ".join(strings)


if __name__ == "__main__":
    start = time.perf_counter()
    parser = argparse.ArgumentParser()

    # mysql
    parser.add_argument('-s', '--storage')
    # meta | cfe | ashr_option | sh_sz_bin
    parser.add_argument('-t', '--table')
    # /Users/daniel/Desktop/opt_arbitrage/data
    parser.add_argument('-p', '--path')

    args = parser.parse_args()
    print(args.storage, args.table, args.path)

    try:
        path = args.path
        if args.table == "meta":
            storge_futures(args.storage, path + '/meta.xlsx')
            storge_options(args.storage, path + '/meta.xlsx')

        if args.table == "cfe":
            storge_cfe(args.storage, path + '/cfe/**')

        if args.table == "ashr_option":
            storge_ashr_option(args.storage, path + '/ashr_option/**')

        if args.table == "sh_sz_bin":
            storge_sh_sz_bin(args.storage, path + '/sh_sz_bin/**')

        end = time.perf_counter()
        elapsed_time = end - start
        print("Elapsed time: ", td_format(elapsed_time))
    except Exception as e:
        raise e
