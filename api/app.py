from flask import Flask, jsonify, request
from sqlalchemy import create_engine, text
import json
import os
from time import strftime

ID=0
health_check_host = {}
def create_app(test_config = None):
    app = Flask(__name__)
    app.config.from_pyfile("config.py")    

    database = create_engine(app.config['DB_URL'])

    app.database = database 

    @app.route('/insert_user')
    def insert_user():
        df=request.json
        
        with database.connect() as conn:
            ID=conn.execute(text("""insert into user_info(name, email, gen_date, id) """), df)
            conn.commit()
        



    @app.route('/get_user')
    def get_user():
        with database.connect() as conn:
            result = conn.execute(text("""SELECT * FROM user_info; """)).fetchall()

        result=[list(row) for row in result]
        js=json.dumps(result)

        return jsonify(js)

    @app.route('/get_network')
    def get_network():
        with database.connect() as conn:
            result = conn.execute(text("""SELECT * FROM network_info; """)).fetchall()

        result=[list(row) for row in result]
        js=json.dumps(result)

        return jsonify(js)


    @app.route('/get_hw')
    def get_hw():
        with database.connect() as conn:
            result = conn.execute(text("""SELECT * FROM hw_info; """)).fetchall()
        
        result=[list(row) for row in result]
        js=json.dumps(result)
        
        return jsonify(js)

    @app.route('/insert_hw', methods=['POST'])
    def insert_hw():
        global ID

        df=request.json
      
        kernel = df['kernel_info']
        networks=df['network_info']
        disks=df['disk_info']
        with database.connect() as conn:
            ID=conn.execute(text("""insert into hw_info(os, kernel_version, kernel_host, kernel_release, kernel_arch, cpu_core, cpu_tot, cpu_id, cpu_model, mem_stor) values(:os, :kernel_version, :kernel_host, :kernel_release, :kernel_arch, :cpu_core, :cpu_tot, :cpu_id, :cpu_model, :mem_stor)"""), kernel).lastrowid
            conn.commit()
        
            for n in networks:
                n['id'] = ID
                conn.execute(text("""insert into network_info(name, addr, netmask, id) values(:name, :addr, :netmask, :id)"""), n)
                conn.commit()

            for p in disks:
                p['id'] = ID
                conn.execute(text("""insert into disk_info(device, mountpoint, fstype, total, used, free, id) values(:device, :mountpoint, :fstype, :total, :used, :free, :id)"""), p)
                conn.commit()

            health_df['on_time']=strftime('%Y-%m-%d %H:%M:%S')
            health_df['id']=ID
            conn.execute(text("""insert into health_check(on_time, id) values (:on_time, :id)"""), health_df)

        return jsonify(ID)

    @app.route('/get_disk')
    def get_disk():
        with database.connect() as conn:
            result = conn.execute(text("""SELECT * FROM disk_info; """)).fetchall()

        result=[list(row) for row in result]
        js=json.dumps(result)

        return jsonify(js)
    
    @app.route('/insert_perform', methods=["POST"])
    def insert_perform():
        df=request.json
        df['time'] = strftime('%Y-%m-%d %H:%M:%S')
        with database.connect() as conn:
            conn.execute(text("""insert into perform_info(time, cpu_usg, mem_usg, disk_io, network, id, vfs_io) values(:time, :cpu_usg, :mem_usg, :disk_io, :network, :id, :vfs_io)"""), df)
            conn.commit()

            health_update=strftime('%Y-%m-%d %H:%M:%S')
            health_id=df['id']

            conn.execute(text("""update health_check set last_update='{}' where id='{}'""").format(health_update, health_id))
            conn.commit()

            health_df=conn.execute(text("""select id from perform_info where time<date_sub(now(), interval 1 minute) group by id;""")).fetchall()

    
        return jsonify(df)

    @app.route('/get_perform')
    def get_perform():
        with database.connect() as conn:
            result = conn.execute(text("""SELECT * FROM perform_info; """)).fetchall()


        result=[list(row) for row in result]
        js=json.dumps(result)

        return jsonify(js)

        
    @app.route('/container_perform', methods=["POST", "GET"])
    def container_perform():
        if request.method=="POST":
            df=request.json

            with database.connect() as conn:
                conn.execute(text("""insert into container_perform_info(cpu, memory, disk_io, network_input, network_output, id, container_id) values (:cpu, :memory, :disk_io, :network_input, :network_output, :id, :container_id)"""), df)
                conn.commit()

            return jsonify(df)

        else:
            with database.connect() as conn:
                result = conn.execute(text("""select * from container_perform_info""")).fetchall()

                result=[list(row) for row in result]
                js=json.dumps(result)

            return jsonify(js)


    @app.route('/container', methods=["POST", "GET", "DELETE"])
    def container():
        if request.method=="POST":
            df=request.json

            with database.connect() as conn:
                conn.execute(text("""insert into container_info(name, container_id, status, image_tag, command, networks, ip, ports, created, id) values(:name, :container_id, :status, :image_tag, :command, :networks, :ip, :ports, :created, :id)"""), df)
                conn.commit()

            return jsonify(df)

        elif request.method=="DELETE":
            df=request.json['container_id']

            with database.connect() as conn:
                conn.execute(text("""delete from  container_info where container_id='{}'""".format(df)))
                conn.commit()

            return jsonify(df)
        
        else:
            with database.connect() as conn:
                result = conn.execute(text("""SELECT * FROM container_info; """)).fetchall()

            result=[list(row) for row in result]
            js=json.dumps(result)

            return jsonify(js)



            
        
    return app

if __name__=="__main__":
    app=create_app()
    app.run(host='0.0.0.0', port='5000', debug=True)

