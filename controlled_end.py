import bluetooth
import pyautogui
import pickle


width, height = pyautogui.size()  # 屏幕宽高

def mouse_execution(message, width=1920, height=1080):
    print("接收到的消息：", message)
    try:
        event, x_rate, y_rate = message
        x, y = x_rate * width, y_rate * height

        if event == 3:  # 左键单击
            # print(f"左键单击{x},{y}")
            pyautogui.click(x, y)
        elif event == 7:  # 左键双击
            # print(f"左键双击{x},{y}")
            pyautogui.doubleClick(x, y)

    except TypeError as e:
        key = message
        pyautogui.press(key)


def main(my_addr):
    server_sock = bluetooth.BluetoothSocket()

    # 搜索可用端口
    for i in range(1, 30):
        try:
            server_sock.bind((my_addr, i))
            print(f"端口号{i}可用")
            break
        except OSError:
            # print(f"OSError, 端口号{i}被占用")
            continue

    server_sock.listen(1)
    port = server_sock.getsockname()[1]

    print("RFCOMM通道正在等待连接：", port)

    while True:
        client_sock, client_info = server_sock.accept()
        print(f"{client_info}已连接")

        while True:
            try:
                length_bytes = client_sock.recv(4)
                message_length = int.from_bytes(length_bytes, 'big')

                message_bytes = client_sock.recv(message_length)
                if message_bytes:
                    message = pickle.loads(message_bytes)
                    # print(message)

                    if message[0] == -1:  # 结束
                        break
                    else:
                        mouse_execution(message)
            except OSError as e:
                print(e)
                break
            except bluetooth.btcommon.BluetoothError as err:
                print("Connection lost: ", err)

        print(f"{client_info}连接已断开")
        client_sock.close()
    server_sock.close()
    print("全部关闭")


if __name__ == "__main__":
    # 读取蓝牙地址
    with open('controlled_end.txt', 'r') as f:
        my_addr = f.readline().strip()  # 本机蓝牙地址

    print(f"本机蓝牙地址：{my_addr}")
    main(my_addr)
