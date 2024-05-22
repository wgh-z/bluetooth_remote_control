import bluetooth
import cv2
from threading import Thread
import numpy as np
import pickle
import time
# import functools


# def screen_reader(camera=0, width=1920, height=1080, fps=30):
#     cap = cv2.VideoCapture(camera)
#     # 设置摄像头参数
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
#     cap.set(cv2.CAP_PROP_FPS, fps)
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
#         yield frame

# def transfer_image(host, port, camera=0):
#     sock = bluetooth.BluetoothSocket()
#     sock.connect((host, port))
#     print(f"已连接{host}:{port}")


#     reader = screen_reader(camera)
#     for frame in reader:
#         print(frame.shape)
#         cv2.imshow('frame', frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#         im_bytes = cv2.imencode('.jpg', frame)[1].tobytes()
#         sock.send(im_bytes)
#     sock.close()


l_point, r_point = None, None
camera = 0
width = 1280
height = 720
fps = 60
prior_event = None
prior_flag = None

cool_down_count = 20
cool_down = cool_down_count
# cv2.EVENT_LBUTTONDBLCLK

def send_controls(sock, event, x, y, width=1920, height=1080):
    message = (event, x/width, y/height)
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

def on_mouse(event, x, y, flags, param):
    global l_point, r_point, sock, width, height, prior_event, cool_down, cool_down_count

    # event falgs
    #   0    0   :移动
    #   1    1   :左键按下
    #   4    0   :左键释放
    #   7    1   :左键双击
    #   2    2   :右键按下
    #   5    0   :右键释放
    #   8    2   :右键双击
    #   10   7864320   :滚轮上滚
    #   10   -7864320   :滚轮下滚
    #   9    7864320   :滚轮上滚

    print('event:', event, x, y, flags, param)
    if event == 1 or event == 7:  # 左键按下
        # print('左键按下')
        send_controls(sock, 1, x, y, width, height)
    elif event == 4:
        # print('左键释放')
        send_controls(sock, 3, x, y, width, height)
    elif event == 2 or event == 8:  # 右键按下
        # print('右键按下')
        send_controls(sock, 2, x, y, width, height)
    elif event == 5:
        # print('右键释放')
        send_controls(sock, 4, x, y, width, height)
    elif event == 0:  # 移动
        # print('移动')
        if cool_down:
            cool_down -= 1
        else:
            send_controls(sock, 0, x, y, width, height)
            cool_down = cool_down_count
        # time.sleep(0.1)


def main(host, port, camera=0, width=1280, height=720, fps=60):
    global l_point, r_point, sock

    sock = bluetooth.BluetoothSocket()
    sock.connect((host, port))
    print(f"已连接{host}:{port}")

    cv2.namedWindow('frame')
    cv2.setMouseCallback('frame', on_mouse)

    cam = cv2.VideoCapture(camera)
    # 设置摄像头参数
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cam.set(cv2.CAP_PROP_FPS, fps)
    # ret = True
    # frame = cv2.imread('test.jpg')
    # frame = cv2.resize(frame, (width, height))
    while True:
        ret, frame = cam.read()
        if not ret:
            break
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            send_controls(sock, -1, 0, 0)
            break
    # cam.release()


if __name__ == '__main__':
    host = '00:A6:23:12:0F:DC'  # 远程蓝牙地址
    # host = '00:A6:23:12:0F:2C'
    port = 1

    # t = Thread(target=transfer_image, args=(host, port, 0))
    # t.start()
    # t.join()
    # print('Done.')
    main(host, port, camera, width, height, fps)
