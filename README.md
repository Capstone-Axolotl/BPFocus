# BPFocus: System Inspection Tools with BPF

## What?

- Assume multiple endpoints connected to a server, collect machine meta information from individual endpoints such as OS version, kernel version, CPU architecture and account information, and performance information such as CPU, memory, and network
- Visualization of abnormal signs of the endpoint through BPF when a task is performed on the machine
- Print endpoint performance information in real-time as a heat map using saturation

## How?
- **Aggregator Server**

need to build a mariadb environment and install some dependencies before running.

```bash
cd api
python3 app.py

# in another terminal
cd frontend-dashboard
npm install
sudo npm install -g create-react-app
npm start
```

- **Client**

need to install some dependencies before running. (see `daemon` directory)

```bash
cd daemon
sudo ./daemon.py
```

## Demo
[![DEMO](https://img.youtube.com/vi/3iDmKLZfwyA/0.jpg)](https://youtu.be/3iDmKLZfwyA)
