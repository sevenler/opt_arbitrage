#  data write
```
    # unrar all rar 
    cd /Users/daniel/Desktop/opt_arbitrage/data
    ls -d -1 $PWD/cfe/2021/*.rar | xargs -n 1 -I {} unrar x {} $PWD/cfe/2021/
    ls -d -1 $PWD/ashr_option/*.rar | xargs -n 1 -I {} unrar x {} $PWD/ashr_option/
    ls -d -1 $PWD/sh_sz_bin/202112/*.rar | xargs -n 1 -I {} unrar x {} $PWD/sh_sz_bin/202112/
    # unrar sh_sz_bin time duration: ~2.5Mins per file  2.5 * 30 = 75Mins total
    
    # init mysql and write into mysql
    mysql -uroot -proot stock_arbitrage < mysql.sql
    python option_storage.py --storage mysql --table meta|cfe|ashr_option|sh_sz_bin --path /Users/daniel/Desktop/opt_arbitrage/data
    
    # init clickhouse and write into clickhouse
    cat clickhouse.sql | clickhouse-client -mn
    python option_storage.py --storage clickhouse --table meta|cfe|ashr_option|sh_sz_bin --path /Users/daniel/Desktop/opt_arbitrage/data
    
    # script write duration
    #
    # cfe
    # 1day rar ~= 2M  ~=30W records
    # clickhouse: 1S(1D) * 30 = 30s
    #
    # ashr_option
    # 1day rar ~= 50M  ~=500W records 
    # total: 1.3 亿
    # clickhouse: 60S(1D) * 30 = 30Mins (实测：40Mins)
    #
    # 1day rar ~= 250M  ~=1500W records
    # total: 3.5 亿
    # clickhouse: 60S * 5(1D) * 30 = 150Mins(实测：3.5H)
    # 
    # 26647 records
    # mysql sink duration: 0.270s
    # clickhouse sink duration: 0.081s
    # ck / mysql = 0.270 / 0.081 = 3.33
    
    # 数据处理效率
    ## 读压缩包中的csv vs 读解压后的csv >=2s vs 0.1s 压缩包越大越慢
    ## pandas.read_csv + loop_rows vs csv.reader 0.5s vs 0.1s
    ## dataformat(Time) vs Time.split(' ')[0]  1s vs 0.01s
    ## 2W csv records => 0.2s 耗时主要来自文件 IO，还有压缩优化空间，例如 fread
    ## 更多提高 csv 文件的读取效率的方法：https://zhuanlan.zhihu.com/p/47872689
    
# clickhouse 磁盘占用
SELECT 
    partition AS `分区`,
    sum(rows) AS `总行数`,
    formatReadableSize(sum(data_uncompressed_bytes)) AS `原始大小`,
    formatReadableSize(sum(data_compressed_bytes)) AS `压缩大小`,
    round((sum(data_compressed_bytes) / sum(data_uncompressed_bytes)) * 100, 0) AS `压缩率`
FROM system.parts
WHERE (database IN ('stock_arbitrage')) AND (table IN ('cfe','ashr_option','sh_sz_bin')) 
GROUP BY partition
ORDER BY partition ASC

```

## 写入异常处理
```
CK 在 bin 数据写入到 2亿条左右的时候出现：
Memory limit (total) exceeded: would use 14.40 GiB (attempt to allocate chunk of 4200984 bytes), maximum: 14.40 GiB.
处理办法：https://github.com/ClickHouse/ClickHouse/issues/17631
```

#  数据校验
```
# 每个工作日的数据没有缺失，量级没有明显波动
select date(Time), count(*) from cfe group by date(Time) order by  date(Time);
select date(Time), count(*) from ashr_option group by date(Time) order by  date(Time);
select date(Time), count(*) from sh_sz_bin group by date(Time) order by  date(Time);

# 每天按照交易时间分布，量级没有明显波动
# 期权：9，10，11，13，14，15
# 期货：7，9，10，11，13，14，15
# 股票：9，10，11，12，13，14，15
select date(Time), hour(Time), count(*) from ashr_option group by date(Time), hour(Time) order by  date(Time), hour(Time);
select date(Time), hour(Time), count(*) from cfe group by date(Time), hour(Time) order by  date(Time), hour(Time);
select date(Time), hour(Time), count(*) from sh_sz_bin group by date(Time), hour(Time) order by  date(Time), hour(Time);

# 暂时忽略
# rar 原始数据中的行数 = 数据库中的行数
# 数据完全一致校验：MD5(csv) == MD5(db)
```