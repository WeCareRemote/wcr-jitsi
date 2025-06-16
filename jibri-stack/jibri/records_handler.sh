#!/bin/bash
log=/home/jibri/records_handler.log
date >> $log 2>&1
curl -X POST --header "Authorization:Bearer $RECORDS_HANDLER_TOKEN" api:80/api/records-handler/ >> $log 2>&1