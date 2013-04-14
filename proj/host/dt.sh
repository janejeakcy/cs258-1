#!/bin/bash
# Xiaohan Li
#printf "%s\n" $1
#echo $1
for(( i = 1; i < 5 ; i++))
do
    wget 10.0.0.10:8080/cs258/test.dat
    #echo "test..."
    sleep 8
done
