#!/bin/bash
# Xiaohan Li
#printf "%s\n" $1
#echo $1
for(( i = 1; i <= 1 ; i++))
do
    printf "start test.....\n"
    cd ~/proj/wrk-master
    ./wrk -t1 -c3 -d10 http://10.0.0.65:8080/cs258/test1.dat >> result.txt
    printf "waiting 2  seconds...\n"
    sleep 2
done
printf "done"
