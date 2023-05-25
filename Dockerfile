FROM sflow/hping3:latest

ENTRYPOINT ["hping3", "192.168.116.137", "-p", "8080", "-S","--flood"]


