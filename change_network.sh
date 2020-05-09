#!/bin/bash
DATETIME=$(date +%Y-%m-%d-%H-%M)
echo "$DATETIME"
sudo cp /etc/dhcpcd.conf config/dhcpd_$DATETIME.conf
sudo cat config/dhcpcd-static.txt config/dhcpcd-dynamic.txt > /etc/dhcpcd.conf
sudo ifconfig eth0 down
sudo ifconfig eth0 up