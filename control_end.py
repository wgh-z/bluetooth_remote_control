import bluetooth
import yaml
import cv2
import pickle
from flask import Flask, Response, jsonify, request, render_template
from flask_cors import CORS
from threading import Thread
from queue import Queue

q = Queue(20)

#开始主程序
app = Flask(__name__)

CORS(app, supports_credentials=True)

def read_frame(cfg):
    camera = cfg['camera']
    width = cfg['width']
    height = cfg['height']
    fps = cfg['fps']

    cam = cv2.VideoCapture(camera)
    # 设置摄像头参数
    cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J', 'P', 'G'))
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cam.set(cv2.CAP_PROP_FPS, fps)
    while True:
        ret, frame = cam.read()
        if not ret:
            break
        q.put(frame)


def gen(cfg):
    """视频流生成"""
    while True:
        frame = q.get()
        # frame = cv2.resize(frame, (width, height))
        data = cv2.imencode('.jpg', frame)[1]
        frame = data.tobytes()
        yield (b'--frame\r\n'
                          b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    global cfg
    return Response(gen(cfg), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/dblclick', methods=['POST'])
def dblclick():
    global sock, cfg
    width = cfg['width']
    height = cfg['height']

    data = request.json
    x_rate = float(data['x'])
    y_rate = float(data['y'])
    print('dbclick===', x_rate, y_rate)
    send_controls(sock, 7, x_rate, y_rate, width, height)
    return jsonify({
      'code': 0
    })

@app.route('/click', methods=['POST'])
def click():
    global sock, cfg
    width = cfg['width']
    height = cfg['height']

    data = request.json
    x_rate = float(data['x'])
    y_rate = float(data['y'])
    print('click===', x_rate, y_rate)
    send_controls(sock, 3, x_rate, y_rate, width, height)
    return jsonify({
      'code': 0
    })

@app.route('/input', methods=['POST'])
def input():
    global sock

    data = request.json
    key = data['key']
    send_controls(sock, event=key, keyboard=True)  # left, right, up, down, +, -
    return jsonify({
      'code': 0
    })

def send_controls(sock, event, x_rate=None, y_rate=None,
                  width=1920, height=1080, keyboard=False):
    if keyboard:
        message = (event, )
    else:
        message = (event, x_rate, y_rate, width, height)
    # print('message=', message)
    try:
        # message_bytes = np.array(message).tobytes()
        message_bytes = pickle.dumps(message)
        message_length = len(message_bytes)
        # print(message_length)
        sock.send(message_length.to_bytes(4, 'big'))
        sock.send(message_bytes)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    # 读取蓝牙地址
    with open('control_end.yaml', 'r', encoding='utf-8') as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)

    # host = '00:A6:23:12:0F:DC'  # 远程蓝牙地址
    # 00:A6:23:12:0F:2C

    bluetooth_ip = cfg['bluetooth_ip']
    bluetooth_port = cfg['bluetooth_port']
    camera = cfg['camera']
    flask_ip = cfg['flask_ip']
    flask_port = cfg['flask_port']

    sock = bluetooth.BluetoothSocket()
    sock.connect((bluetooth_ip, bluetooth_port))
    print(f"蓝牙已连接{bluetooth_ip}:{bluetooth_port}")

    # app.run(host=flask_ip, port=flask_port, debug=True, threaded=True, processes=True)
    flask_thread = Thread(target=app.run,
                          kwargs={
                              'host': flask_ip,
                              'port':flask_port,
                              'debug': True,
                              'use_reloader': False,
                              'threaded': True,
                            #   'processes':True
                              }
                        )
    flask_thread.start()

    read_thread = Thread(target=read_frame, args=(cfg,))
    read_thread.start()
