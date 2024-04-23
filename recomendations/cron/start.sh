#!/usr/bin/env bash

service cron start

echo "" > /usr/src/cron/logs/cron.log

tail -f /usr/src/cron/logs/cron.log