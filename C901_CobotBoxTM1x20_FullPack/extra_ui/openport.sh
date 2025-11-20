sysctl -w net.ipv4.ip_forward=1
iptables -t nat -A PREROUTING -p tcp --dport 502 -j DNAT --to-destination 192.168.88.7:502
iptables -t nat -A PREROUTING -p udp --dport 502 -j DNAT --to-destination 192.168.88.7:502
iptables -t nat -A PREROUTING -p tcp --dport 9000:9029 -j DNAT --to-destination 192.168.88.7:9000-9029
iptables -t nat -A PREROUTING -p udp --dport 9000:9029 -j DNAT --to-destination 192.168.88.7:9000-9029
iptables -t nat -A POSTROUTING -j MASQUERADE 
iptables -t nat -A POSTROUTING -o wlan0 -s 192.168.88.0/24 -j MASQUERADE
iptables -t nat -A PREROUTING -i wlan0 -p tcp --dport 3074 -j DNAT --to-destination 192.168.88.254
iptables -t nat -A PREROUTING -i wlan0 -p udp -m multiport --dports 88,3074 -j DNAT --to-destination 192.168.88.254
iptables -A FORWARD -i wlan0 -d 192.168.88.254 -p tcp --dport 3074 -j ACCEPT