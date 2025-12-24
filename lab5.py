#Alex Anderson

import socket
from time import sleep
from pynput import keyboard
import sys
import threading
import enum

socketLock = threading.Lock()

class States(enum.Enum):
    STRAIGHT = enum.auto()

class StateMachine():
    def __init__(self):
        self.IP_ADDRESS = "192.168.1.106"
        self.CONTROLLER_PORT = 5001
        self.TIMEOUT = 10
        self.STATE = States.STRAIGHT
        self.RUNNING = True
        self.DIST = False

        try:
            with socketLock:
                self.sock = socket.create_connection((self.IP_ADDRESS, self.CONTROLLER_PORT), self.TIMEOUT)
                self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            print("Connected to RP")
        except Exception as e:
            print("ERROR with socket connection", e)
            sys.exit(0)

        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def main(self):
        # init robot
        with socketLock:
            self.sock.sendall("i /dev/ttyUSB0".encode())
            print("Sent command")
            result = self.sock.recv(128)
            #result = self.sock.recv(128)
            print("\n", result)
            if result.decode(errors="ignore").strip() != "i /dev/ttyUSB0":
                # controller may not echo; don't kill RUNNING on mismatch
                pass

        sleep(0.2)
        self.sensors = Sensing(self.sock)
        self.sensors.start()

        # FIX: use the correct flag name
        while self.RUNNING:
            sleep(0.1)

            # control loop
            # (comment block simplified)
            # if self.DIST:
            #     print("Distance requested")
            #     with socketLock:
            #         self.sock.sendall("d".encode())
            #         distance = self.sock.recv(128).decode().strip()
            #     print("Distance: ", distance)
            #     self.DIST = False

            print("bout to go straight")

            # FIX: guard socket with lock
            with socketLock:
                self.sock.sendall("a drive_straight(75)".encode())
                _ = self.sock.recv(128)  # optional: depends on your controller
            sleep(2)

            # FIX: stop by commanding 0, and guard with lock
            with socketLock:
                self.sock.sendall("a drive_straight(0)".encode())
                _ = self.sock.recv(128)  # optional
            sleep(0.5)

            # FIX: read ticks from the sensing thread object
            avg_ticks = (self.sensors.leftSensor + self.sensors.rightSensor) / 2
            print("Went", self.sensors.distance, "mm forward")


            # OPTIONAL: break after one cycle so it doesn’t loop forever
            self.RUNNING = False

        # shutdown
        self.sensors.RUNNING = False
        self.sensors.join()

        with socketLock:
            self.sock.sendall("c".encode())
            print(self.sock.recv(128))
            self.sock.close()

        self.listener.stop()

    def on_press(self, key):
        try:
            print('alphanumeric key {0} pressed'.format(key.char))
            if key.char == 'd':
                self.DIST = True
        except AttributeError:
            print('special key {0} pressed'.format(key))

    def on_release(self, key):
        print('{0} released'.format(key))
        if key == keyboard.Key.esc or key == keyboard.Key.ctrl:
            self.RUNNING = False
            return False

class Sensing(threading.Thread):
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.sock = socket
        self.RUNNING = True
        self.leftSensor = 0
        self.rightSensor = 0
        self.distance = 0

    def run(self):
        while self.RUNNING:
            sleep(0.1)
            with socketLock:
                self.sock.sendall("a left_encoder_counts".encode())
                left_str = self.sock.recv(128).decode(errors="ignore").strip()
            with socketLock:
                self.sock.sendall("a right_encoder_counts".encode())
                right_str = self.sock.recv(128).decode(errors="ignore").strip()

            with socketLock:
                self.sock.sendall("a distance".encode())
                distanceTry = self.sock.recv(128).decode(errors="ignore").strip()

            # FIX: robust int parse
            try:
                self.leftSensor = int(left_str.split()[0])
            except:
                # print("Parse left failed:", left_str)
                pass
            try:
                self.rightSensor = int(right_str.split()[0])
            except:
                # print("Parse right failed:", right_str)
                pass

            try:
                print(distanceTry)
                self.distance = float(distanceTry)
            except:
                
                pass
            



if __name__ == "__main__":
    sm = StateMachine()
    sm.main()