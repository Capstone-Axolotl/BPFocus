import pymysql
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

# 데이터베이스 연결 설정 및 데이터 로드
connection = pymysql.connect(
    host='localhost',
    user='dbuser',
    password='dbpass',
    database='dbname'
)

query = "SELECT time, cpu_usg, mem_usg, disk_io, vfs_io, net_in, net_out FROM perform_info"
df = pd.read_sql(query, connection)
connection.close()

# 시간 데이터를 제외한 성능 메트릭 데이터
metric_data = df[['cpu_usg', 'disk_io', 'vfs_io', 'net_in', 'net_out']]
mem_usg_data = df[['mem_usg']]

# 각 열의 최대값 계산
max_values = metric_data.max()

# 가장 큰 값으로 정규화
normalized_metric_data = metric_data / max_values

# 정규화되지 않은 mem_usg 데이터를 합쳐서 최종 데이터 프레임 생성
final_data = pd.concat([normalized_metric_data, mem_usg_data], axis=1)

# Isolation Forest 모델 학습
model = IsolationForest(contamination=0.1)
model.fit(final_data)

# 모델 저장
joblib.dump(model, 'isolation_forest_model.joblib')

print("Model training completed and saved to isolation_forest_model.joblib")

