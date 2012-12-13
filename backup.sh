#!/bin/bash
#Usage
#./backup.sh urltarget 
#

if [ $# = 1 ]
    then
	backupAnswer=$(curl -X POST -H "Content-Type: application/json" -d '{"source":"cozy","target":"'$1'","verify_ssl_certificates":false}' http://127.0.0.1:5984/_replicate) 
	if [[ "$backupAnswer" == *"\"ok\":true"* ]]
	    then
		#Backup Ok
		exit 0
	    else 
		#Backup FAILED
		exit 1
	fi
	
    else
	echo "Usage: $0 targetUrl"
	exit 1
fi
