from flask import Flask

# Flask 애플리케이션 생성
app = Flask(__name__)

# 루트 URL에 대한 핸들러 함수 정의
@app.route("/")
def hello():
    cnt = 0
    for i in range(0x10000):
        cnt += i
        print(i)

    return "Hello, Flask!"

# 서버 실행
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)

