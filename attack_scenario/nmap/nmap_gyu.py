#!/usr/bin/env python3
import subprocess

def run_nmap_scan(targets, ports):
    try:
        # nmap 실행 명령어
        command = ['nmap', '-p', ports, *targets, '--data-length', '65434', '--badsum']
        print(command)
        
        # 외부 명령어 실행
        output = subprocess.check_output(command)
        
        # 결과 출력
        print(output.decode())
    
    except subprocess.CalledProcessError as e:
        print(f"오류 발생: {e}")
        
# 테스트
target_ips = ["127.0.0.1", "192.168.198.128"]  # 대상 IP 주소 리스트
port_range = "1-65535"  # 스캔할 포트 범위
run_nmap_scan(target_ips, port_range)
