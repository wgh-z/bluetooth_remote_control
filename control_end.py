import bluetooth
import cv2
from threading import Thread
import numpy as np
import pickle
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


def send_controls(sock, event, x, y, width=1920, height=1080):
    message = (event, x/width, y/height)
    print('message=', message)
    try:
        # message_bytes = np.array(message).tobytes()
        message_bytes = pickle.dumps(message)
        sock.send(message_bytes)
    except Exception as e:
        print(e)

def on_mouse(event, x, y, flags, param):
    global l_point, r_point, sock, width, height
    print('event:', event, x, y, flags, param)
    # if event == cv2.EVENT_LBUTTONDOWN:  # 左键点击
    #     print('event:', event, x, y, flags, param)
    #     send_controls(sock, event, x, y, width, height)

    # elif event == cv2.EVENT_RBUTTONDOWN:  # 右键点击
    #     print('event:', event, x, y, flags, param)
    #     send_controls(sock, event, x, y, width, height)

    # elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):               #按住左键拖曳
    #     cv2.rectangle(img2, point1, (x,y), (255,0,0), 5)
    #     cv2.imshow('image', img2)
    # elif event == cv2.EVENT_LBUTTONUP:         #左键释放
    #     point2 = (x,y)
    #     cv2.rectangle(img2, point1, point2, (0,0,255), 5) 
    #     cv2.imshow('image', img2)
    #     min_x = min(point1[0],point2[0])     
    #     min_y = min(point1[1],point2[1])
    #     width = abs(point1[0] - point2[0])
    #     height = abs(point1[1] -point2[1])
    #     cut_img = img[min_y:min_y+height, min_x:min_x+width]

    # elif event == cv2.EVENT_MBUTTONDOWN:  # 中键点击
    #     m_point = (x,y)
    #     print('m=', m_point)
    # elif event == cv2.EVENT_LBUTTONDBLCLK:  # 左键双击
    #     ld_point = (x,y)
    #     print('ld=', ld_point)
    # elif event == cv2.EVENT_RBUTTONDBLCLK:  # 右键双击
    #     rd_point = (x,y)
    #     print('rd=', rd_point)

def main(host, port, camera=0, width=1280, height=720, fps=60):
    global l_point, r_point, sock

    sock = bluetooth.BluetoothSocket()
    sock.connect((host, port))
    print(f"已连接{host}:{port}")

    cv2.namedWindow('frame')
    cv2.setMouseCallback('frame', on_mouse)

    # cam = cv2.VideoCapture(camera)
    # # 设置摄像头参数
    # cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    # cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    # cam.set(cv2.CAP_PROP_FPS, fps)
    ret = True
    frame = cv2.imread('boar.jpg')
    frame = cv2.resize(frame, (width, height))
    while True:
        # ret, frame = cam.read()
        if not ret:
            break
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            send_controls(sock, -1, 0, 0)
            break
    # cam.release()


if __name__ == '__main__':
    host = '00:A6:23:12:0F:2C'  # 远程蓝牙地址
    # host = '00:A6:23:12:0F:DC'
    port = 4

    # t = Thread(target=transfer_image, args=(host, port, 0))
    # t.start()
    # t.join()
    # print('Done.')
    main(host, port, camera, width, height, fps)
