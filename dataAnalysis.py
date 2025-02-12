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

    csv_filename = input("Fill file's name measurement data: ")

    with open(csv_filename + ".csv", mode='a', newline='') as file:
        writer = csv.writer(file)

        # Ghi tiêu đề nếu file rỗng
        if file.tell() == 0:
            writer.writerow(["time", "Angle", "Velocity", "RawVelocity"])

        startTime = time.time()

        time_list, angle_list, velocity_list, raw_velocity_list = [], [], [], []

        data_queue = queue.Queue(maxsize = 1)
        running = True

        def readSerial():
            # Hàm chạy nền liên tục đọc dữ liệu từ Serial
            while running:
                data = ser.readline().decode("utf-8", errors="ignore").strip()
                state = data[1:].split()
                if not data:
                    continue
                elif (data[0] != 'S') or (len(state) != 3):
                    continue

                try:
                    angle = float(state[0])
                    velocity = float(state[1])
                    rawVel = float(state[2])
                    dt = time.time() - startTime

                    if data_queue.full():
                        data_queue.get()  # Xóa phần tử cũ nhất nếu queue đầy
                    else:
                        data_queue.put([dt, angle, velocity, rawVel])
                    # data_queue.put((dt, angle, velocity, rawVel))
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
            global time_list, velocity_list, raw_velocity_list
            
            while not data_queue.empty():
                dt, angle, velocity, rawVel = data_queue.get()

                # print(f"Motor's Angle: {angle}")
                # print(f"Motor's Velocity: {velocity}")
                # print(f"Motor's Raw Velocity: {rawVel}")
                print(f"Time: {dt}")

                time_list.append(dt)
                angle_list.append(angle)
                velocity_list.append(velocity)
                raw_velocity_list.append(rawVel)

                if len(time_list) % 1000 == 0:
                    writer.writerows(zip(time_list, angle_list, velocity_list, raw_velocity_list))
                    file.flush()

                max_points = 1000
                if len(time_list) > max_points:
                    time_list.pop(0)
                    angle_list.pop(0)
                    velocity_list.pop(0)
                    raw_velocity_list.pop(0)

                lineVel.set_data(time_list, velocity_list)
                lineRawVel.set_data(time_list, raw_velocity_list)

                ax.set_xlim(max(0, dt - 10), dt + 1)
                # ax.set_ylim(min(min(velocity_list + raw_velocity_list), -10),
                #             max(max(velocity_list + raw_velocity_list), 10))
                

                ax.relim()
                ax.autoscale_view()


        
        ani = animation.FuncAnimation(fig, update, interval=50, cache_frame_data=False)
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