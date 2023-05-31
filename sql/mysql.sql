drop database stock_arbitrage;
create database stock_arbitrage;
use stock_arbitrage;

CREATE TABLE stock_arbitrage.`future` (
  `Code` varchar(64) NOT NULL COMMENT '代码',
  `Name` varchar(64) DEFAULT NULL COMMENT '名称',
  `lasttrade_date` varchar(32) DEFAULT NULL COMMENT '最后交易日',
  `ftdate` varchar(32) DEFAULT NULL COMMENT '开始交易日',
  `contractmultiplier` float  DEFAULT NULL COMMENT '合约乘数',
  PRIMARY KEY (`Code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='期货';

CREATE TABLE stock_arbitrage.`option` (
  `Code` varchar(64) NOT NULL COMMENT '代码',
  `Name` varchar(64) DEFAULT NULL COMMENT '名称',
  `tradecode` varchar(32) DEFAULT NULL COMMENT '期权交易代码',
  `us_code` varchar(32) DEFAULT NULL COMMENT '标的代码',
  `us_name` varchar(32) DEFAULT NULL COMMENT '标的简称',
  `exe_price` float  DEFAULT NULL COMMENT '行权价格',
  `startdate` varchar(32)  DEFAULT NULL COMMENT '起始交易日期',
  `lasttradingdate` varchar(32)  DEFAULT NULL COMMENT '最后交易日期',
  `exe_startdate` varchar(32)  DEFAULT NULL COMMENT '起始行权日期',
  `exe_enddate` varchar(32)  DEFAULT NULL COMMENT '最后行权日期',
  `exe_ratio` float  DEFAULT NULL COMMENT '合约乘数',
  PRIMARY KEY (`Code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='期权';


CREATE TABLE stock_arbitrage.`ashr_option` (
  `id` bigint(20) NOT NULL auto_increment PRIMARY KEY,
  `Code` varchar(64) NOT NULL COMMENT '代码',
  `Time` DATETIME(6) DEFAULT NULL,
  `Price` float DEFAULT NULL,
  `Volume` BIGINT DEFAULT NULL,
  `Amount` BIGINT DEFAULT NULL,
  `SP1` float  DEFAULT NULL,
  `SP2` float  DEFAULT NULL,
  `SP3` float  DEFAULT NULL,
  `SP4` float  DEFAULT NULL,
  `SP5` float  DEFAULT NULL,
  `SV1` float  DEFAULT NULL,
  `SV2` float  DEFAULT NULL,
  `SV3` float  DEFAULT NULL,
  `SV4` float  DEFAULT NULL,
  `SV5` float  DEFAULT NULL,
  `BP1` float  DEFAULT NULL,
  `BP2` float  DEFAULT NULL,
  `BP3` float  DEFAULT NULL,
  `BP4` float  DEFAULT NULL,
  `BP5` float  DEFAULT NULL,
  `BV1` float DEFAULT NULL,
  `BV2` float DEFAULT NULL,
  `BV3` float DEFAULT NULL,
  `BV4` float DEFAULT NULL,
  `BV5` float DEFAULT NULL,
  `isBuy` INT  DEFAULT NULL,
  `OI` INT  DEFAULT NULL,
   KEY `key_code` (`Code`, `Time`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='沪深交易所期权的日内Tick数据';

CREATE TABLE `cfe` (
  `id` bigint(20) NOT NULL auto_increment PRIMARY KEY,
  `Code` varchar(64) NOT NULL COMMENT '代码',
  `Time` DATETIME(6) DEFAULT NULL,
  `Price` float DEFAULT NULL,
  `Volume` float DEFAULT NULL,
  `Amount` INT DEFAULT NULL,
  `OI` INT  DEFAULT NULL,
  `SP1` float  DEFAULT NULL,
  `SV1` INT  DEFAULT NULL,
  `BP1` float  DEFAULT NULL,
  `BV1` INT DEFAULT NULL,
  `isBuy` INT  DEFAULT NULL,
  KEY `key_code` (`Code`, `Time`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='中金所股指期货和国债期货的日内Tick数据';


CREATE TABLE `sh_sz_bin` (
  `id` bigint(20) NOT NULL auto_increment PRIMARY KEY,
  `Code` varchar(64) NOT NULL COMMENT '代码',
  `Time` DATETIME(6) DEFAULT NULL,
  `Price` float DEFAULT NULL,
  `Volume` BIGINT DEFAULT NULL,
  `Amount` BIGINT DEFAULT NULL,
  `SP1` float  DEFAULT NULL,
  `SP2` float  DEFAULT NULL,
  `SP3` float  DEFAULT NULL,
  `SP4` float  DEFAULT NULL,
  `SP5` float  DEFAULT NULL,
  `SV1` float  DEFAULT NULL,
  `SV2` float  DEFAULT NULL,
  `SV3` float  DEFAULT NULL,
  `SV4` float  DEFAULT NULL,
  `SV5` float  DEFAULT NULL,
  `BP1` float  DEFAULT NULL,
  `BP2` float  DEFAULT NULL,
  `BP3` float  DEFAULT NULL,
  `BP4` float  DEFAULT NULL,
  `BP5` float  DEFAULT NULL,
  `BV1` float DEFAULT NULL,
  `BV2` float DEFAULT NULL,
  `BV3` float DEFAULT NULL,
  `BV4` float DEFAULT NULL,
  `BV5` float DEFAULT NULL,
  `isBuy` INT  DEFAULT NULL,
  KEY `key_code` (`Code`, `Time`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='沪深交易所股票、基金的日内Tick数据';