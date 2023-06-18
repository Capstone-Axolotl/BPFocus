#!/bin/sh
for i in $(seq 1 10)
do
    container="nmap_victim${i}_1"
    hping3 --scan 1-1000 -S -d 5000 $container
done
sleep inf
