from flask import Flask, jsonify, request
from sqlalchemy import create_engine, text
import json

def create_app(test_config = None):
    app = Flask(__name__)
    
    #DB config
    USER = 'axolotl'
    PASS = 'password'
    HOST = 'localhost'
    PORT = 3306
    DB = 'axolotl_DB'

    connect_string='mysql+pymysql://{user}:{pw}@{host}:{port}/{db}?charset=utf8mb4'.format(user=USER, pw=PASS, host=HOST, port=PORT, db=DB)


    database = create_engine(connect_string) 
    app.database = database 

    @app.route('/hw_info')
    def get_hw():
        with database.connect() as conn:
            result = conn.execute(text("""SELECT * FROM hw_info; """)).fetchall()
        
        result=[list(row) for row in result]
        js=json.dumps(result)
        
        return jsonify(js)
        
    return app

if __name__=="__main__":
    app=create_app()
    app.run(host='0.0.0.0', port='5000', debug=True)

