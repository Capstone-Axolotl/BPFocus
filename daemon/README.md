# Daemon
`axolotl daemon` is a performance measurement daemon that enables macroscopic monitoring. It leverages BCC Python (BPF) and Docker SDK to collect performance information from endpoints and send it to centralized aggregation server(`api`).

## Install
```bash
# 1. 기본 환경 세팅
sudo apt update && sudo apt-get update
sudo apt install terminator vim git gcc build-essential docker

# 2. python을 python3로 사용하도록 변경, python2 백업
sudo mv /usr/bin/python /usr/bin/python.backup
sudo ln -s /usr/bin/python3 /usr/bin/python

# 3. BCC 소스 코드로 빌드
sudo apt install -y bison build-essential cmake flex git libedit-dev libllvm12 llvm-12-dev libclang-12-dev python zlib1g-dev libelf-dev libfl-dev python3-setuptools
sudo apt-get -y install luajit luajit-5.1-dev
git clone https://github.com/iovisor/bcc.git
mkdir bcc/build; cd bcc/build
cmake .. -DENABLE_LLVM_SHARED=1
make -j4
sudo make install
cmake -DPYTHON_CMD=python3 .. # build python3 binding
pushd src/python/
make
sudo make install
popd

# 4. bcc tools 환경 변수 등록
echo "export PATH=\$PATH:/usr/share/bcc/tools/" >> ~/.bashrc

# 5. 레포지토리 다운로드
git clone https://github.com/Capstone-Axolotl/Axolotl.git
cd Axolotl/daemon
pip3 install -r requirements.txt
```

## Start (with root)
```bash
./daemon.py
```
