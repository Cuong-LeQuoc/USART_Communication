import serial
import csv
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import queue

try:
    ser = serial.Serial(port="COM3", baudrate=576000, timeout=1)
    print("Connect Sucessful!")

    csv_filename = input("Enter file's name measurement data: ")

    with open(csv_filename + ".csv", mode='a', newline='') as file:
        writer = csv.writer(file)

        # Ghi tiêu đề nếu file rỗng (dòng đầu tiên)
        if file.tell() == 0:
            writer.writerow(["time", "timeStep", "Voltage", "Angle", "Velocity", "RawVelocity"])

        partTime = 0
        globalTime = 0

        time_list, angle_list, velocity_list, raw_velocity_list = [], [], [], []

        data_queue = queue.Queue(maxsize = 1)
        running = True

        def readSerial():
            global globalTime, partTime

            dt = 0

            partTime = time.time()
            # Hàm chạy nền liên tục đọc dữ liệu từ Serial
            while running:
                data = ser.readline().decode("utf-8", errors="ignore").strip()
                state = data[1:].split()

                if (not data) or (data[0] != 'S') or (len(state) != 4):
                    partTime = time.time()
                    continue

                try:
                    voltage = float(state[0])
                    angle = float(state[1])
                    velocity = float(state[2])
                    rawVel = float(state[3])
                    
                    dt = time.time() - partTime
                    globalTime += dt
                    partTime = time.time()

                    if not data_queue.empty():
                        data_queue.get()
                    data_queue.put([angle, velocity, rawVel])

                    # print(f"Voltage: {voltage}")

                    writer.writerow([globalTime, dt, voltage, angle, velocity, rawVel])
                    file.flush()

                except ValueError:
                    pass  # Bỏ qua dòng lỗi

        # Khởi động luồng đọc Serial
        serial_thread = threading.Thread(target = readSerial, daemon=True)
        serial_thread.start()

        fig, ax = plt.subplots()
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Values")
        ax.set_title("Real-time Motor Data")
        ax.grid(True)

        lineRawVel, = ax.plot([], [], label="Raw Velocity", color='green')
        lineVel, = ax.plot([], [], label="Velocity", color='red')
        
        ax.legend()

        ax.set_ylim(-500, 500)

        def update(frame):
            global globalTime, time_list, velocity_list, raw_velocity_list

            if not data_queue.empty():
                angle, velocity, rawVel = data_queue.get()

                # print(f"Time: {globalTime}")

                time_list.append(globalTime)
                angle_list.append(angle)
                velocity_list.append(velocity)
                raw_velocity_list.append(rawVel)

                max_points = 1000
                if len(time_list) > max_points:
                    time_list.pop(0)
                    angle_list.pop(0)
                    velocity_list.pop(0)
                    raw_velocity_list.pop(0)

                lineVel.set_data(time_list, velocity_list)
                lineRawVel.set_data(time_list, raw_velocity_list)

                ax.set_xlim(max(0, globalTime - 10), globalTime + 1)
                # ax.set_ylim(min(min(velocity_list + raw_velocity_list), -10),
                #             max(max(velocity_list + raw_velocity_list), 10))
                
                ax.relim()
                ax.autoscale_view()

        ani = animation.FuncAnimation(fig, update, interval = 50, cache_frame_data=False)
        plt.show()

except serial.SerialException as e:
    print(f"Open fail: {e}")

except KeyboardInterrupt:
    print(f"Interrupt!!")

finally:
    running = False
    serial_thread.join()

    if ser.is_open and ('ser' in locals()):
        ser.close()
        print("Serial port Disconnect!")