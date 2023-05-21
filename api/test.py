from sqlalchemy import create_engine, text
import json

USER = 'axolotl'
PASS = 'password'
HOST = 'localhost'
PORT = 3306
DB = 'axolotl_DB'

connect_string='mysql+pymysql://{user}:{pw}@{host}:{port}/{db}?charset=utf8mb4'.format(user=USER, pw=PASS, host=HOST, port=PORT, db=DB)


database = create_engine(connect_string)

with database.connect() as conn:
    result = conn.execute(text("SELECT * FROM hw_info "))

res=result.all()
#res=json.dumps(res)
print(res)
print(type(res))

test_data=[('1', '2'), ('3', '4')]
print(test_data)
print(type(test_data))

