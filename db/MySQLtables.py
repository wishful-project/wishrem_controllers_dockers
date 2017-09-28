#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function

import mysql.connector
from mysql.connector import errorcode
import json

'''
Creates the REM database
'''

DB_NAME = 'remdb'

TABLES = {}

TABLES['global_location'] = (
    "CREATE TABLE `global_location` ("
    "  `id` bigint NOT NULL AUTO_INCREMENT,"
    "  `name_identifier` varchar(32),"
    "  `x_coord` float NOT NULL,"
    "  `y_coord` float NOT NULL,"
    "  `z_coord` float NOT NULL,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")

TABLES['devices'] = (
    "CREATE TABLE `devices` ("
    "  `uuid` varchar(64),"
    "  `mac_address` varchar(17) NOT NULL,"
    "  `chan_capab` TEXT,"
    "  `x_coord` float,"
    "  `y_coord` float,"
    "  `z_coord` float,"
    "  `global_loc_id` bigint,"
    "  `floor` int(2),"
    "  `loc_type` int(1),"
    "  `mode` varchar(3),"
    "  `power` float,"
    "  `ssid` varchar(32),"
    "  `status` int(2),"
    "  `active_channel` int(2),"
    "  `active_channel_sup` int(2),"
    "  `ap_mac_address` varchar(17),"
    "  PRIMARY KEY (`mac_address`)"
    ") ENGINE=InnoDB")

TABLES['rssi_meas'] = (
    "CREATE TABLE `rssi_meas` ("
    "  `id` bigint NOT NULL AUTO_INCREMENT,"
    "  `tx_mac_address` varchar(17) NOT NULL,"
    "  `rx_mac_address` varchar(17) NOT NULL,"
    "  `value` float NOT NULL,"
    "  `timestamp` datetime NOT NULL,"
    "  `signal_type` varchar(20) NOT NULL,"
    "  `bw_mode` int(2) NOT NULL,"
    "  `active_channel` int(2) NOT NULL,"
    "  `active_channel_sup` int(2) NOT NULL,"
    "  PRIMARY KEY (`id`),"
    "  FOREIGN KEY (`rx_mac_address`) REFERENCES devices(`mac_address`)"
    ") ENGINE=InnoDB")

TABLES['duty_cycle'] = (
    "CREATE TABLE `duty_cycle` ("
    "  `id` bigint NOT NULL AUTO_INCREMENT,"
    "  `rx_mac_address` varchar(17) NOT NULL,"
    "  `value` float NOT NULL,"
    "  `timestamp` datetime NOT NULL,"
    "  `channel` int(2) NOT NULL,"
    "  PRIMARY KEY (`id`),"
    "  FOREIGN KEY (`rx_mac_address`) REFERENCES devices(`mac_address`)"
    ") ENGINE=InnoDB")

TABLES['estimated_locations'] = (
    "CREATE TABLE `estimated_locations` ("
    "  `id` bigint NOT NULL AUTO_INCREMENT,"
    "  `tx_mac_address` varchar(17) NOT NULL,"
    "  `x_coord` float NOT NULL,"
    "  `y_coord` float NOT NULL,"
    "  `global_loc_id` bigint NOT NULL,"
    "  `floor` int(2) NOT NULL,"
    "  `timestamp` datetime NOT NULL,"
    "  `channel` int(2) NOT NULL,"
    "  `tx_power` float(4,2) NOT NULL,"
    "  PRIMARY KEY (`id`),"
    "  FOREIGN KEY (`global_loc_id`) REFERENCES global_location(`id`)"
    ") ENGINE=InnoDB")

TABLES['propagation_model'] = (
    "CREATE TABLE `propagation_model` ("
    "  `id` bigint NOT NULL AUTO_INCREMENT,"
    "  `L0` float NOT NULL,"
    "  `alpha` float NOT NULL,"
    "  `sigma` float NOT NULL,"
    "  `d0` float NOT NULL,"
    "  `timestamp` datetime NOT NULL,"
    "  `channel` int(2) NOT NULL,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")

TABLES['ap_statistics'] = (
    "CREATE TABLE `ap_statistics` ("
    "  `id` bigint NOT NULL AUTO_INCREMENT,"
    "  `ap_mac_address` varchar(17) NOT NULL,"
    "  `total_tx_retries` float NOT NULL,"
    "  `total_tx_failed` float NOT NULL,"
    "  `total_tx_throughput` float NOT NULL,"
    "  `total_rx_throughput` float NOT NULL,"
    "  `total_tx_activity` float NOT NULL,"
    "  `total_rx_activity` float NOT NULL,"
    "  `timestamp` datetime NOT NULL,"
    "  PRIMARY KEY (`id`),"
    "  FOREIGN KEY (`ap_mac_address`) REFERENCES devices(`mac_address`)"
    ") ENGINE=InnoDB")

TABLES['link_statistics'] = (
    "CREATE TABLE `link_statistics` ("
    "  `id` bigint NOT NULL AUTO_INCREMENT,"
    "  `tx_mac_address` varchar(17) NOT NULL,"
    "  `rx_mac_address` varchar(17) NOT NULL,"
    "  `rssi` float NOT NULL,"
    "  `tx_retries` float NOT NULL,"
    "  `tx_failed` float NOT NULL,"
    "  `tx_rate` float NOT NULL,"
    "  `rx_rate` float NOT NULL,"
    "  `tx_throughput` float NOT NULL,"
    "  `rx_throughput` float NOT NULL,"
    "  `tx_activity` float NOT NULL,"
    "  `rx_activity` float NOT NULL,"
    "  `timestamp` datetime NOT NULL,"
    "  PRIMARY KEY (`id`),"
    "  FOREIGN KEY (`tx_mac_address`) REFERENCES devices(`mac_address`)"
    ") ENGINE=InnoDB")

#cnx = mysql.connector.connect(user='root',password='rem', port='3306', host='localhost')
cnx = mysql.connector.connect(user='root',password='rem', unix_socket='/var/run/mysqld/mysqld.sock')
cursor = cnx.cursor()

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

try:
    cnx.database = DB_NAME  
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)

for name, ddl in TABLES.items():
    try:
        print("Creating table {}: ".format(name), end='')
        cursor.execute(ddl)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

for name, ddl in TABLES.items():
    try:
        print("Creating table {}: ".format(name), end='')
        cursor.execute(ddl)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

cursor.close()
cnx.close()
