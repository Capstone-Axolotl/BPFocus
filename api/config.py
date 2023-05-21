db = {
    'user':'axolotl',
    'password':'P@ssw0rd',
    'host': 'localhost',
    'port': 3306,
    'database': 'axolotl_DB'
}
DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8mb4"

