from flask import Flask, jsonify, request
from sqlalchemy import create_engine, text
import json
import os
from time import strftime

ID=0
CPU_MAX=5000000
DISK_MAX=10000
NET_MAX=100000
VFS_MAX=10000

def create_app(test_config = None):
    app = Flask(__name__)
    app.config.from_pyfile("config.py")    

    database = create_engine(app.config['DB_URL'])

    app.database = database 

    @app.route('/insert_user', methods=["POST"])
    def insert_user():
        df=request.json
        
        with database.connect() as conn:
            ID=conn.execute(text("""insert into user_info(name, email, gen_date, id) """), df)
            conn.commit()
        

    @app.route('/get_user', methods=["GET", "POST"])
    def get_user():
        if request.method=="POST":
            df=request.json['id']
            
            with database.connect() as conn:
                result=conn.execute(text("""select * from user_info where id='{}'""".format(df)))

        else:
            with database.connect() as conn:
                result = conn.execute(text("""SELECT * FROM user_info; """)).fetchall()

        
        result=[list(row) for row in result]
        js=json.dumps(result, default=str)

        return jsonify(js)

    @app.route('/get_network')
    def get_network():
        with database.connect() as conn:
            result = conn.execute(text("""SELECT * FROM network_info; """)).fetchall()

        result=[list(row) for row in result]
        js=json.dumps(result)

        return jsonify(js)

    @app.route('/update_health', methods=["POST"])
    def update_health():
        df=request.json['id']

        with database.connect() as conn:
            conn.execute(text("""update health_check set status='running' where id='{}'""".format(df)))
            conn.commit()

        return jsonify(df)

       
    @app.route('/get_components')
    def get_components():
        file_data={}

        with database.connect() as conn:
            ID = conn.execute(text("""select id from health_check where status='running'"""))
            ID='24'
            for i in ID:
                result1=conn.execute(text("""select name, email, id from user_info where id='{}'""".format(i[0])))
                result2=conn.execute(text("""select container_id, name from container_info where id='{}'""".format(i[0])))
                data={}
                file_data["nodes"]=[]
                file_data["links"]=[]
                for row in result1:
                    data["email"]=row.email
                    data["name"]=row.name
                    data["id"]=row.id
                
                file_data["nodes"].append(data)
                 
                for row in result2:
                    data={}
                    
                    data["id"]=row.container_id
                    data["name"]=row.name
            
                    file_data["nodes"].append(data)

                    data={}
                    
                    data['source']=i[0]
                    data['target']=row.container_id

                    file_data["links"].append(data)
            


        with open('/home/gyu/axolotl_front/src/components/Network/components_data.json', 'w', encoding='utf-8') as make_file:
            json.dump(file_data, make_file, ensure_ascii=False, indent='\t')
        return jsonify(file_data)


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
            health_df={} 
            health_df['status']="running"
            health_df['id']=ID
            conn.execute(text("""insert into health_check(status, id) values (:status, :id)"""), health_df)
            conn.commit()
            
            df['name']['id']=ID
            conn.execute(text("""insert into user_info(name, id) values(:name, :id)"""), df['name'] )
            conn.commit()

        return jsonify(ID)

    @app.route('/get_disk')
    def get_disk():
        with database.connect() as conn:
            result = conn.execute(text("""SELECT * FROM disk_info; """)).fetchall()

        result=[list(row) for row in result]
        js=json.dumps(result)

        return jsonify(js)
   
    @app.route('/anomaly', methods=["GET", "POST"])
    def anomaly():
        global CPU_MAX
        global DISK_MAX
        global NET_MAX
        global VFS_MAX
        
        if request.method=="POST":
            df=request.json
            CPU_MAX=df['cpu']
            DISK_MAX=df['disk']
            NET_MAX=df['network']
            


    @app.route('/insert_perform', methods=["POST"])
    def insert_perform():
        df=request.json
        df['time'] = strftime('%Y-%m-%d %H:%M:%S')
        df['cpu_usg']=round(df['cpu_usg']/CPU_MAX*100, 2)
        if(df['cpu_usg'])>100 : df['cpu_usg']=100
        df['disk_io']=df['disk_io']/DISK_MAX*100
        df['network']=df['network']/NET_MAX*100
        df['vfs_io']=df['vfs_io']/VFS_MAX*100

        with database.connect() as conn:
            conn.execute(text("""insert into perform_info(time, cpu_usg, mem_usg, disk_io, network, id, vfs_io) values(:time, :cpu_usg, :mem_usg, :disk_io, :network, :id, :vfs_io)"""), df)
            conn.commit()

            health_time=df['time']
            health_id=df['id']

            conn.execute(text("""update health_check set last_update='{}' where id='{}'""".format(health_time, health_id)))
            conn.commit()

            health_df=conn.execute(text("""select id from health_check where status='running' and last_update<date_sub(now(), interval 1 minute) group by id;""")).fetchall()

            result=[list(row) for row in health_df]
            for i in result:
                conn.execute(text("""update health_check set status='disabled' where id={}""".format(int(i[0]))))
                conn.commit()


        return jsonify(result)

    @app.route('/get_perform', methods=["GET", "POST"])
    def get_perform():
        if request.method=="GET":
            with database.connect() as conn:
                result = conn.execute(text("""SELECT * FROM perform_info; """)).fetchall()
        
            result=[list(row) for row in result]
            js=json.dumps(result, default=str)
            return jsonify(js)
            
        else:
            df=request.json['id']
             
            try: 
                int(df)

                with database.connect() as conn:
                    result = conn.execute(text("""select * from perform_info where id='{}' order by time desc limit 10""".format(df)))
                
                file_data={df:[]}
                
                for i in result:
                    data={}
                    data["date"]=str(i.time)
                    data["cpu"]=i.cpu_usg
                    data["memory"]=i.mem_usg
                    data["disk_io"]=i.disk_io
                    data["network"]=i.network
                    data["vfs_io"]=i.vfs_io
                    
                    file_data[df].append(data)

            except ValueError:
                with database.connect() as conn:
                    result = conn.execute(text("""select * from container_perform_info where id='{}' order by time desc limit 10""".format(df)))

                    file_data={df:[]}

                    for i in result:
                        data={}
                        data["date"]=str(i.time)
                        data["cpu"]=i.cpu
                        data["memory"]=i.memory
                        data["disk_io"]=i.disk_io
                        data["network"]=i.network_input+i.network_output
                        data["vfs_io"]=NULL

                        file_data[df].append(data)
                
            with open('perform.json', 'w', encoding='utf-8') as make_file:
                json.dump(file_data, make_file, ensure_ascii=False, indent='\t')
                return jsonify(file_data)



       
    @app.route('/insert_container_perform', methods=["POST"])
    def insert_container_perform():
        df=request.json

        df['cpu']=df['cpu']/CPU_MAX*100
        df['disk_io']=df['disk_io']/DISK_MAX*100
        df['network_input']=df['network_input']/NET_MAX*100
        df['network_output']=df['network_output']/NET_MAX*100
        df['time'] = strftime('%Y-%m-%d %H:%M:%S')

        with database.connect() as conn:
            conn.execute(text("""insert into container_perform_info(cpu, memory, disk_io, network_input, network_output, id, container_id, time) values (:cpu, :memory, :disk_io, :network_input, :network_output, :id, :container_id, :time)"""), df)
            conn.commit()

        return jsonify(df)

    @app.route('/container_perform')
    def container_perform():
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

