USER = 'axolotl'
PASS = 'password'
HOST = 'localhost'
PORT = 3306
DB = 'axolotl_DB'

DB_URL='mysql+pymysql://{user}:{pw}@{host}:{port}/{db}?charset=utf8mb4'.format(user=USER, pw=PASS, host=HOST, port=PORT, db=DB)

#test
