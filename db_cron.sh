#!/bin/bash

cp -v /home/ubuntu/ncap/db.sqlite3 /home/ubuntu/ncap/db_backups/db_$(date +%m-%d-%y_%H:%M:%S).sqlite3
