import serial
import csv
import time
import sys
import select
from datetime import datetime

port = '/dev/ttyUSB0'
baud_rate = 115200
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_file = f"servo_data_{timestamp}.csv"

ser = serial.Serial(port, baud_rate, timeout=0.1)

time.sleep(2)

with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)

    print("Logging started")
    print("Type an angle (0-180) and press ENTER")

    try:
        while True:

            # ----- READ SERIAL DATA -----
            line = ser.readline().decode('utf-8').strip()

            if line:
                print(line)
                writer.writerow(line.split(','))

            # ----- CHECK IF USER TYPED A COMMAND -----
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:

                command = sys.stdin.readline().strip()

                if command.isdigit():
                    ser.write((command + '\n').encode())
                    print("Command sent:", command)

    except KeyboardInterrupt:
        print("\nLogging stopped")

ser.close()