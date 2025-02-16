import serial
import serial.tools.list_ports as port_list
import threading

class SerialCtrl:
    def __init__(self):
        self.running = True

    def getCOMList(self):
        self.comList = []
        for port in list(port_list.comports()):
            self.comList.append(port.device)

        self.comList.insert(0, '-')

        return self.comList
    
    def readData(self):
        buffer = self.ser.readline().decode("utf-8", errors="ignore").strip()
        return buffer[1:].split()

    def serialReader(self, dataPool):
        self.running = True
        self.serialThread = threading.Thread(target=self.serialRead, args=(dataPool,), daemon=True)
        self.serialThread.start()

        
    def serialRead(self, controlPanel):
        controlPanel.dataPool.setRefTime()
        
        controlPanel.updateDisplay()

        while self.running:
            try:
                if not self.ser.is_open:
                    return
                controlPanel.dataPool.msg = self.readData() # [str, str]
                if controlPanel.dataPool.vaildData():
                    controlPanel.dataPool.updateData()
                if controlPanel.dataPool.adjustData():
                    if controlPanel.dataPool.saving:
                        controlPanel.dataPool.writeData() # thêm file name

                    controlPanel.dataPool.viewing = True    

            except ValueError:
                pass  # Bỏ qua dữ liệu không hợp lệ
            except Exception as e:
                print(f"Stop error: {e}")

    def serialWrite(self, voltage):
        buffer = f"V{voltage:.2f}\n"
        self.ser.write(buffer.encode())
        print(buffer.encode())

    def serialOpen(self, comManager):
        try:
            if not hasattr(self, 'ser') or not self.ser.is_open:
                PORT = comManager.clickedCom.get()
                BAUDRATE = comManager.clickedBaud.get()
                self.ser = serial.Serial()
                self.ser.timeout = 1
                self.ser.baudrate = BAUDRATE
                self.ser.port = PORT
                self.ser.open()
                self.ser.flushInput()
                self.ser.status = True
        except Exception as e:
            print(f"Error opening serial port: {e}")
            self.ser.status = False

    def serialClose(self):
        try:
            if self.ser.is_open:
                self.ser.status = False
                self.running = False
                self.ser.close()

        except:
            self.ser.status = False
            self.running = False