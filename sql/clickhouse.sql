drop database stock_arbitrage;

create database stock_arbitrage;

CREATE TABLE stock_arbitrage.`future`
(
    `Code`               String NOT NULL COMMENT '代码',
    `Name`               String NULL COMMENT '名称',
    `lasttrade_date`     DateTime64(3) NOT NULL COMMENT '最后交易日',
    `ftdate`             DateTime64(3) NULL COMMENT '开始交易日',
    `contractmultiplier` Float64 NULL COMMENT '合约乘数',
) ENGINE = ReplacingMergeTree(lasttrade_date) ORDER BY Code COMMENT '期货';


CREATE TABLE stock_arbitrage.`option`
(
    `Code`            String NOT NULL COMMENT '代码',
    `Name`            String  DEFAULT NULL COMMENT '名称',
    `tradecode`       String  DEFAULT NULL COMMENT '期权交易代码',
    `us_code`         String  DEFAULT NULL COMMENT '标的代码',
    `us_name`         String  DEFAULT NULL COMMENT '标的简称',
    `exe_price`       Float64 DEFAULT NULL COMMENT '行权价格',
    `startdate`       String  DEFAULT NULL COMMENT '起始交易日期',
    `lasttradingdate` DateTime64(3) NOT NULL COMMENT '最后交易日期',
    `exe_startdate`   String  DEFAULT NULL COMMENT '起始行权日期',
    `exe_enddate`     String  DEFAULT NULL COMMENT '最后行权日期',
    `exe_ratio`       Float64 DEFAULT NULL COMMENT '合约乘数'
) ENGINE = ReplacingMergeTree(lasttradingdate) ORDER BY Code COMMENT '期权';


CREATE TABLE stock_arbitrage.`ashr_option`
(
    `id`     String  NOT NULL,
    `Code`   String NOT NULL COMMENT '代码',
    `Time`   DateTime64(3) NOT NULL,
    `Price`  Float64 DEFAULT NULL,
    `Volume` Int64   DEFAULT NULL,
    `Amount` Int64   DEFAULT NULL,
    `SP1`    Float64 DEFAULT NULL,
    `SP2`    Float64 DEFAULT NULL,
    `SP3`    Float64 DEFAULT NULL,
    `SP4`    Float64 DEFAULT NULL,
    `SP5`    Float64 DEFAULT NULL,
    `SV1`    Float64 DEFAULT NULL,
    `SV2`    Float64 DEFAULT NULL,
    `SV3`    Float64 DEFAULT NULL,
    `SV4`    Float64 DEFAULT NULL,
    `SV5`    Float64 DEFAULT NULL,
    `BP1`    Float64 DEFAULT NULL,
    `BP2`    Float64 DEFAULT NULL,
    `BP3`    Float64 DEFAULT NULL,
    `BP4`    Float64 DEFAULT NULL,
    `BP5`    Float64 DEFAULT NULL,
    `BV1`    Float64 DEFAULT NULL,
    `BV2`    Float64 DEFAULT NULL,
    `BV3`    Float64 DEFAULT NULL,
    `BV4`    Float64 DEFAULT NULL,
    `BV5`    Float64 DEFAULT NULL,
    `isBuy`  Int64   DEFAULT NULL,
    `OI`     Int64   DEFAULT NULL
) ENGINE = ReplacingMergeTree(Time) ORDER BY id COMMENT '沪深交易所期权的日内Tick数据';

Alter table stock_arbitrage.ashr_option ADD INDEX tag_idx (Code, toStartOfHour(Time)) TYPE minmax GRANULARITY 1024;

CREATE TABLE stock_arbitrage.`cfe`
(
    `id`     String NOT NULL,
    `Code`   String NOT NULL COMMENT '代码',
    `Time`   DateTime64(3) NOT NULL,
    `Price`  Float64 DEFAULT NULL,
    `Volume` Float64 DEFAULT NULL,
    `Amount` Int64   DEFAULT NULL,
    `OI`     Int64   DEFAULT NULL,
    `SP1`    Float64 DEFAULT NULL,
    `SV1`    Int64   DEFAULT NULL,
    `BP1`    Float64 DEFAULT NULL,
    `BV1`    Int64   DEFAULT NULL,
    `isBuy`  Int64   DEFAULT NULL
) ENGINE = ReplacingMergeTree(Time) ORDER BY id COMMENT '中金所股指期货和国债期货的日内Tick数据';

Alter table stock_arbitrage.cfe ADD INDEX tag_idx (Code, toStartOfHour(Time)) TYPE minmax GRANULARITY 1024;


CREATE TABLE stock_arbitrage.`sh_sz_bin`
(
    `id`     String  NOT NULL,
    `Code`   String NOT NULL COMMENT '代码',
    `Time`   DateTime64(3) NOT NULL,
    `Price`  Float64 DEFAULT NULL,
    `Volume` Int64   DEFAULT NULL,
    `Amount` Int64   DEFAULT NULL,
    `SP1`    Float64 DEFAULT NULL,
    `SP2`    Float64 DEFAULT NULL,
    `SP3`    Float64 DEFAULT NULL,
    `SP4`    Float64 DEFAULT NULL,
    `SP5`    Float64 DEFAULT NULL,
    `SV1`    Float64 DEFAULT NULL,
    `SV2`    Float64 DEFAULT NULL,
    `SV3`    Float64 DEFAULT NULL,
    `SV4`    Float64 DEFAULT NULL,
    `SV5`    Float64 DEFAULT NULL,
    `BP1`    Float64 DEFAULT NULL,
    `BP2`    Float64 DEFAULT NULL,
    `BP3`    Float64 DEFAULT NULL,
    `BP4`    Float64 DEFAULT NULL,
    `BP5`    Float64 DEFAULT NULL,
    `BV1`    Float64 DEFAULT NULL,
    `BV2`    Float64 DEFAULT NULL,
    `BV3`    Float64 DEFAULT NULL,
    `BV4`    Float64 DEFAULT NULL,
    `BV5`    Float64 DEFAULT NULL,
    `isBuy`  Int64   DEFAULT NULL
) ENGINE = ReplacingMergeTree(Time) ORDER BY id COMMENT '沪深交易所股票、基金的日内Tick数据';

Alter table stock_arbitrage.sh_sz_bin ADD INDEX tag_idx (Code, toStartOfHour(Time)) TYPE minmax GRANULARITY 1024;