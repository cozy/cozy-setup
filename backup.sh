#!/bin/bash
#Usage
#./backup.sh urltarget urlbackup
#
curl -X POST http://127.0.0.1:5984/_replicate -d {"source"="$1","target"="$2"}
