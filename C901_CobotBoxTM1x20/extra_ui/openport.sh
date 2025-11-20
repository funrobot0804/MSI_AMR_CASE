sysctl -w net.ipv4.ip_forward=1
iptables -t nat -A PREROUTING -p tcp --dport 502 -j DNAT --to-destination 192.168.88.7:502
iptables -t nat -A PREROUTING -p tcp --dport 3849 -j DNAT --to-destination 192.168.88.7:3849
iptables -t nat -A PREROUTING -p tcp --dport 4585 -j DNAT --to-destination 192.168.88.7:4585
iptables -t nat -A PREROUTING -p tcp --dport 5001 -j DNAT --to-destination 192.168.88.7:5001
iptables -t nat -A PREROUTING -p tcp --dport 5050 -j DNAT --to-destination 192.168.88.7:5050
iptables -t nat -A PREROUTING -p tcp --dport 5194:5199 -j DNAT --to-destination 192.168.88.7:5194-5199
iptables -t nat -A PREROUTING -p tcp --dport 5201 -j DNAT --to-destination 192.168.88.7:5201
iptables -t nat -A PREROUTING -p tcp --dport 5430 -j DNAT --to-destination 192.168.88.7:5430
iptables -t nat -A PREROUTING -p tcp --dport 5432 -j DNAT --to-destination 192.168.88.7:5432
iptables -t nat -A PREROUTING -p tcp --dport 5700 -j DNAT --to-destination 192.168.88.7:5700
iptables -t nat -A PREROUTING -p tcp --dport 5890:5891 -j DNAT --to-destination 192.168.88.7:5890-5891
iptables -t nat -A PREROUTING -p tcp --dport 6187:6188 -j DNAT --to-destination 192.168.88.7:6187-6188
iptables -t nat -A PREROUTING -p tcp --dport 8816 -j DNAT --to-destination 192.168.88.7:9863
iptables -t nat -A PREROUTING -p tcp --dport 12290 -j DNAT --to-destination 192.168.88.7:12290
iptables -t nat -A PREROUTING -p tcp --dport 14585 -j DNAT --to-destination 192.168.88.7:14585
iptables -t nat -A PREROUTING -p tcp --dport 15566 -j DNAT --to-destination 192.168.88.7:15566
iptables -t nat -A PREROUTING -p tcp --dport 16188 -j DNAT --to-destination 192.168.88.7:16188
iptables -t nat -A PREROUTING -p tcp --dport 50051 -j DNAT --to-destination 192.168.88.7:50051
iptables -t nat -A PREROUTING -p tcp --dport 445 -j DNAT --to-destination 192.168.88.7:445
iptables -t nat -A PREROUTING -p tcp --dport 139 -j DNAT --to-destination 192.168.88.7:139
iptables -t nat -A PREROUTING -p tcp --dport 222 -j DNAT --to-destination 192.168.88.7:222
iptables -t nat -A PREROUTING -p tcp --dport 20 -j DNAT --to-destination 192.168.88.7:20
iptables -t nat -A PREROUTING -p tcp --dport 21 -j DNAT --to-destination 192.168.88.7:21
iptables -t nat -A PREROUTING -p tcp --dport 2222 -j DNAT --to-destination 192.168.88.7:2222
iptables -t nat -A PREROUTING -p udp --dport 44818 -j DNAT --to-destination 192.168.88.7:44818
iptables -t nat -A PREROUTING -p tcp --dport 34964 -j DNAT --to-destination 192.168.88.7:34964
iptables -t nat -A PREROUTING -p udp --dport 49152 -j DNAT --to-destination 192.168.88.7:49152
iptables -t nat -A PREROUTING -p udp --dport 5600 -j DNAT --to-destination 192.168.88.7:5600
iptables -t nat -A PREROUTING -p udp --dport 7000 -j DNAT --to-destination 192.168.88.7:7000
iptables -t nat -A PREROUTING -p udp --dport 7001 -j DNAT --to-destination 192.168.88.7:7001
iptables -t nat -A PREROUTING -p udp --dport 137 -j DNAT --to-destination 192.168.88.7:137
iptables -t nat -A PREROUTING -p udp --dport 138 -j DNAT --to-destination 192.168.88.7:138
iptables -t nat -A PREROUTING -p udp --dport 19880 -j DNAT --to-destination 192.168.88.7:19880
iptables -t nat -A PREROUTING -p udp --dport 51335 -j DNAT --to-destination 192.168.88.7:51335
iptables -t nat -A POSTROUTING -j MASQUERADE 
iptables -t nat -A POSTROUTING -o wlan0 -s 192.168.88.0/24 -j MASQUERADE
iptables -t nat -A PREROUTING -i wlan0 -p tcp --dport 3074 -j DNAT --to-destination 192.168.88.254
iptables -t nat -A PREROUTING -i wlan0 -p udp -m multiport --dports 88,3074 -j DNAT --to-destination 192.168.88.254
iptables -A FORWARD -i wlan0 -d 192.168.88.254 -p tcp --dport 3074 -j ACCEPT