#!/bin/bash
if [ -n "$DEBUG" ];
then
    set -x
    set -v
else
    exec &> /dev/null
fi

LOCAL_DIR='/usr/local/bin'
OBJECT_DIR='/home/megaflex/objetos'
TERM=linux

cd $OBJECT_DIR &&
runcbl POS0000 $1
cd $LOCAL_DIR
exit $RETVAL
