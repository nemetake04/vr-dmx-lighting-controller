#dmx_2
#unityからは右コントローラのステック（x,y）、A・Bボタン（on/off）を文字列で受け取る。
# dmx_1,3 : スティック入力（加算式・0〜255クランプ）
# dmx_5   : A_ONで+10、B_ONで-10（0〜140ループ）
# dmx_8   : Trigger_ONでON/OFFトグル（0 / 255）

import socket
import serial
import threading
import time
import queue

DMX_UNIVERSE_SIZE = 512
UDP_PORT = 5005

# -------------------------------
# DMX Controller（送信ループ）
# -------------------------------
class DMXController:
    def __init__(self, port="COM6"):
        self.dmx = [0] * DMX_UNIVERSE_SIZE
        try:
            self.ser = serial.Serial(port, baudrate=250000, bytesize=8, parity="N", stopbits=2, timeout=0)
            time.sleep(0.1)
            print(f"✅ Serial Open: {port}")
        except Exception as e:
            print(f"⚠ Serial Error: {e}")
            self.ser = None

        self.running = True
        self.thread = threading.Thread(target=self._loop)
        self.thread.daemon = True
        self.thread.start()

    def _loop(self):
        while self.running:
            self.send()
            time.sleep(0.05)  # 20fps

    def send(self):
        if not self.ser:
            return
        try:
            self.ser.break_condition = True
            time.sleep(0.0001)
            self.ser.break_condition = False
            time.sleep(0.000012)
            self.ser.write(bytes([0]) + bytes(self.dmx))
        except:
            pass

    def set_channel(self, ch, value):
        idx = ch - 1
        if 0 <= idx < DMX_UNIVERSE_SIZE:
            self.dmx[idx] = int(max(0, min(255, value)))

    def close(self):
        self.running = False
        if self.ser:
            self.ser.close()

# -------------------------------
# Stick値 → DMX変換
# -------------------------------
def stick_to_dmx(value: float) -> int:
    value = max(-1.0, min(1.0, value))
    return int((value + 1.0) * 127.5)

# -------------------------------
# UDP Receiver（スレッド）
# -------------------------------
def udp_receiver(q: queue.Queue):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", UDP_PORT))
    print(f"UDP Listening on {UDP_PORT} ...")

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            msg = data.decode("utf-8").strip()
            
            # Stickデータ
            if msg.startswith("Stick:"):
                x_str, y_str = msg.replace("Stick:", "").split(",")
                x = float(x_str)
                y = float(y_str)
                q.put(("Stick", x, y))
            
            # Trigger_ON
            elif msg == "Trigger_ON":
                q.put(("Trigger_ON",))
            
            # A_ON
            elif msg == "A_ON":
                q.put(("A_ON",))
            
            # B_ON
            elif msg == "B_ON":
                q.put(("B_ON",))

        except Exception as e:
            print("UDP Error:", e)

# -------------------------------
# ステックの変化量に関する関数
# -------------------------------
def stick_to_delta(value: float, speed=2.0, deadzone=0.12) -> float:
    if abs(value) < deadzone:
        return 0.0
    value = max(-1.0, min(1.0, value))#min(a,b)->a,bで小さいほうを選択
    return value * speed


# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":
    dmx = DMXController("COM6")
    q = queue.Queue()

    # UDP受信スレッド
    t = threading.Thread(target=udp_receiver, args=(q,), daemon=True)
    t.start()

    print("DMX output started")

    # 状態管理
    dmx5_value = 0
    dmx8_state = False
    dmx1_value = 127
    dmx3_value = 127

    # ★ スティックの最新値を保持
    stick_x = 0.0
    stick_y = 0.0

    while True:
        try:
            # -------- UDP入力処理 --------
            while not q.empty():
                item = q.get()

                if item[0] == "Stick":
                    _, stick_x, stick_y = item

                elif item[0] == "Trigger_ON":
                    dmx8_state = not dmx8_state
                    val = 255 if dmx8_state else 0
                    dmx.set_channel(8, val)
                    print(f"Trigger_ON → DMX8={val}")

                elif item[0] == "A_ON":
                    dmx5_value += 10
                    if dmx5_value > 140:
                        dmx5_value = 0
                    dmx.set_channel(5, dmx5_value)
                    print(f"A_ON → DMX5={dmx5_value}")

                elif item[0] == "B_ON":
                    dmx5_value -= 10
                    if dmx5_value < 0:
                        dmx5_value = 140
                    dmx.set_channel(5, dmx5_value)
                    print(f"B_ON → DMX5={dmx5_value}")

            # -------- スティック処理（毎フレーム） --------
            dx = -stick_to_delta(stick_x)
            dy = -stick_to_delta(stick_y)

            dmx1_value += dx
            dmx3_value += dy

            dmx1_value = max(0, min(255, int(dmx1_value)))
            dmx3_value = max(0, min(255, int(dmx3_value)))

            dmx.set_channel(1, dmx1_value)
            dmx.set_channel(3, dmx3_value)

            # 表示方法はそのまま
            if dx != 0 or dy != 0:
                print(
                    f"Stick X={stick_x:.2f} → DMX1={dmx1_value} | "
                    f"Y={stick_y:.2f} → DMX3={dmx3_value}"
                )

            time.sleep(0.01)  # 100fps

        except KeyboardInterrupt:
            dmx.close()
            break
