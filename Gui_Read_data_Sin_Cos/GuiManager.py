from tkinter import *
from tkinter import messagebox, filedialog
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.font_manager import FontProperties
import numpy as np
import threading


class RootGUI:
    def __init__(self):
        self.root = Tk()

        # self.root.table = None

        self.resolution = ["800x600", "1024x768", "1152x864", "1280x768"]

        self.root.title("Serial Communication")
        self.root.geometry(self.resolution[3])
        self.root.config(bg="white")

        self.root.frontType = 'Times New Roman'
        self.root.frontSize = {
            "title": 36,
            "frame": 18,
            "normal": 14
        }

        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.title = Label(self.root, text="Inverted Pendulum", bg="white", font=(self.root.frontType, self.root.frontSize["title"]))
        self.title.grid(row=0, column=1, columnspan=30, pady=20, sticky="ew")

    def open(self):
        self.root.mainloop()

    def close(self):
        self.root.quit()
        self.root.destroy()

class WidgetManeger:
    def __init__(self, root, serial, dataPool):
        self.root = root
        self.serial = serial
        self.dataPool = dataPool

        

        self.root.table = TableView(root, dataPool)

        self.root.graph = GraphView(root, dataPool)
        self.root.com = ComManager(root, serial, dataPool)
        self.root.control = ControlPanel(root, serial, dataPool)

class ComManager:
    def __init__(self, root, serial, dataPool):
        self.root = root
        self.dataPool = dataPool
        self.serial = serial
        self.frame = LabelFrame(root, text="Com Manager", bg="white", font=(self.root.frontType, self.root.frontSize["frame"]),
                                padx=5, pady=5)
        self.labelCom = Label(self.frame, text="Available Port(s): ", font=(self.root.frontType, self.root.frontSize["normal"]),
                               bg="white", width=15, anchor="w")
        self.labelBaud = Label(self.frame, text="Baudrate: ", font=(self.root.frontType, self.root.frontSize["normal"]),
                                   bg="white", width=15, anchor="w")

        self.btnConnect = Button(self.frame, text="Connect", bg="white", width=10, font=(self.root.frontType, self.root.frontSize["normal"]),
                                 state="disabled", command=self.serialConnect)
        self.btnRefresh = Button(self.frame, text="Refresh", bg="white", width=10, font=(self.root.frontType, self.root.frontSize["normal"]),
                                 state="normal", command=self.comRefresh)
        
        self.btnReset = Button(self.frame, text="Reset", bg="white", width=10, font=(self.root.frontType, self.root.frontSize["normal"]),
                                 state="normal", command=self.comReset)

        self.ComOptionMenu()
        self.BaudOptionMenu()

        self.publish()

    def publish(self):
        self.frame.grid(row=1, column=1, rowspan=5, columnspan=10, padx=5, pady=5)
        self.labelCom.grid(column=1, row=1)
        self.labelBaud.grid(column=1, row=2)
        self.comMenu.grid(column=2, row=1, padx=5)
        self.baudMenu.grid(column=2, row=2, padx=5)
        self.btnConnect.grid(column=3, row=1)
        self.btnRefresh.grid(column=3, row=2)
        self.btnReset.grid(column=3, row=3)

    def ComOptionMenu(self):
        self.serial.getCOMList()
        self.clickedCom = StringVar()   # save the selected value
        self.clickedCom.set(self.serial.comList[0]) # default value
        self.comMenu = OptionMenu(self.frame, self.clickedCom, *self.serial.comList,
                                  command=self.connectAccess)
        self.comMenu.config(width=10, font=(self.root.frontType, self.root.frontSize["normal"]))
        self.comMenu["menu"].config(font=(self.root.frontType, self.root.frontSize["normal"]))

    def BaudOptionMenu(self):
        bauds = ["-", "115200", "576000", "921600"]
        self.clickedBaud = StringVar()
        self.clickedBaud.set(bauds[0])
        self.baudMenu = OptionMenu(self.frame, self.clickedBaud, *bauds, 
                                   command=self.connectAccess)
        self.baudMenu.config(width=10, font=(self.root.frontType, self.root.frontSize["normal"]))
        self.baudMenu["menu"].config(font=(self.root.frontType, self.root.frontSize["normal"]))

    def connectAccess(self, _):
        if '-' in self.clickedCom.get() or '-' in self.clickedBaud.get():
            self.btnConnect["state"] = "disable"
        else:
            self.btnConnect["state"] = "active"
    
    def serialConnect(self):
        if "Connect" in self.btnConnect["text"]:
            self.serial.serialOpen(self)
            if self.serial.ser.status:
                self.btnConnect["text"] = "Disconnect"
                self.btnRefresh["state"] = "disable"
                self.comMenu["state"] = "disable"
                self.baudMenu["state"] = "disable"
                infoMsg = f"Successful UART connection using {self.clickedCom.get()}"
                messagebox.showinfo("UART Connection", infoMsg)

            else:
                

                ErrorMsg = f"Failure to estabish UART connection using {self.clickedCom.get()}"
                messagebox.showerror("showerror", ErrorMsg)

        else:
            # Close connect
            self.serial.running = False
            self.dataPool.viewing = False
            self.serial.serialClose()
            infoMsg = f"Successful UART {self.clickedCom.get()} is closed"
            messagebox.showinfo("UART Connection", infoMsg)
            self.btnConnect["text"] = "Connect"
            self.btnRefresh["state"] = "active"
            self.comMenu["state"] = "active"
            self.baudMenu["state"] = "active"

    def comRefresh(self):
        self.comMenu.destroy()
        self.ComOptionMenu()
        self.comMenu.grid(column=2, row=1, padx=5)
        self.connectAccess(None)

    def comReset(self):
        COM = self.clickedCom.get()

        # Disconnect
        self.serial.running = False
        self.dataPool.viewing = False
        self.serial.serialClose()
        # infoMsg = f"Successful UART {self.clickedCom.get()} is closed"
        # messagebox.showinfo("UART Connection", infoMsg)
        # self.btnConnect["text"] = "Connect"
        # self.btnRefresh["state"] = "active"
        # self.comMenu["state"] = "active"
        # self.baudMenu["state"] = "active"


        self.comRefresh()

        self.clickedCom.set(COM)

        # Reconnect
        self.serial.serialOpen(self)
        if self.serial.ser.status:
            self.btnConnect["text"] = "Disconnect"
            self.btnConnect["state"] = "active"
            self.comMenu["state"] = "disable"
            self.baudMenu["state"] = "disable"
            infoMsg = f"Successful UART connection using {self.clickedCom.get()}"
            messagebox.showinfo("UART Connection", infoMsg)

        else:
            ErrorMsg = f"Failure to estabish UART connection using {self.clickedCom.get()}"
            messagebox.showerror("showerror", ErrorMsg)



class ControlPanel:
    def __init__(self, root, serial, dataPool):
        self.root = root

        self.table = root.table
        self.graph = root.graph

        self.serial = serial
        self.dataPool = dataPool

        self.frame = LabelFrame(root, text="Control Panel", bg="white", font=(self.root.frontType, self.root.frontSize["frame"]),
                                padx=5, pady=5)
        self.btnStart = Button(self.frame, text="Start", bg="white", width=8, font=(self.root.frontType, self.root.frontSize["normal"]),
                               state="active", command=self.startView)
        self.btnStop = Button(self.frame, text="Stop", bg="white", width=8, font=(self.root.frontType, self.root.frontSize["normal"]),
                              state="disable", command=self.stopView)
        
        self.boxSendData = Entry(self.frame, width=8, font=(self.root.frontType, self.root.frontSize["normal"]))
        self.btnSend = Button(self.frame, text="Send", bg="white", width=8, font=(self.root.frontType, self.root.frontSize["normal"]),
                              state="active", command=self.sendVoltage)

        self.volLabel = Label(self.frame, text="Voltage (V): ", bg="white", font=(self.root.frontType, self.root.frontSize["normal"]))

        self.publish()

    def sendVoltage(self):
        try:
            self.dataPool.voltage = float(self.boxSendData.get())

            if abs(self.dataPool.voltage) > 11:
                infoMsg = f"Voltage's Value is out range: [-11; 11]"
                messagebox.showinfo("Invalid value", infoMsg)

            else:
                buffer = f"V{self.dataPool.voltage:.2f}\n"
                self.serial.ser.write(buffer.encode())
                print(buffer.encode())
        except ValueError:
            infoMsg = f"Couldn't send value: {self.boxSendData.get()}"
            messagebox.showinfo("Invalid value", infoMsg)
        except AttributeError:
            warningMsg = f"The communication port is not open"
            messagebox.showwarning("Warning when send data", warningMsg)




    def startView(self):
        self.btnStart["state"] = "disable"
        self.btnStop["state"] = "active"

        self.table.btnBrowse["state"] = "disable"
        self.table.saveData["state"] = "disable"

        self.serial.running = True
        self.serialThread = threading.Thread(target=self.serial.serialRead, args=(self,), daemon=True)
        self.serialThread.start()

    def updateDisplay(self):
        if self.dataPool.viewing:
            self.dataPool.viewing = False

            self.table.updateTableView()
            self.graph.updateGraphView()
            
        
        if self.serial.running:
            self.root.after(self.dataPool.timeUpdateView, self.updateDisplay) 

    def stopView(self):
        self.btnStart["state"] = "active"
        self.btnStop["state"] = "disable"

        self.table.btnBrowse["state"] = "normal"
        self.table.saveData["state"] = "normal"       

        self.serial.running = False
        self.dataPool.viewing = False
        if self.serialThread is not None:
            self.serialThread.join()

    def publish(self):
        self.frame.grid(row=6, column=1, rowspan=6, columnspan=3, padx=5, pady=5, sticky='w')

        self.btnStart.grid(column=1, row=0, padx=5, pady=5)
        self.btnStop.grid(column=2, row=0, padx=5, pady=5)

        self.volLabel.grid(row=1, column=0)
        self.boxSendData.grid(column=1, row=1, padx=5, pady=10)
        self.btnSend.grid(column=2, row=1, padx=5, pady=10)
        

class TableView:
    def __init__(self, root, dataPool):
        self.root = root
        self.dataPool = dataPool

        self.clickSave = BooleanVar()

        self.frame = LabelFrame(root, text="Table view data", bg="white", font=(self.root.frontType, self.root.frontSize["frame"]),
                                padx=5, pady=5)

        self.fileNameLabel = Label(self.frame, text="File Name: ", bg="white", font=(self.root.frontType, self.root.frontSize["normal"]))
        self.fileName = Entry(self.frame, width=20, font=(self.root.frontType, self.root.frontSize["normal"]))

        self.btnBrowse = Button(self.frame, text="Browse", bg="white", font=(self.root.frontType, self.root.frontSize["normal"]),
                                state="active", command=self.browseFolder)
        self.savePath = Entry(self.frame, bg="white", font=(self.root.frontType, self.root.frontSize["normal"]))

        self.saveDataLabel = Label(self.frame, text="Save Data: ", bg="white", font=(self.root.frontType, self.root.frontSize["normal"]))
        self.saveData = Checkbutton(self.frame, bg="white", fg="green", state="normal", font=(self.root.frontType, self.root.frontSize["normal"]),
                                    variable=self.clickSave, command=self.savingData)

        self.sinDataLabel = Label(self.frame, text="Sin Value", bg="white", font=(self.root.frontType, self.root.frontSize["normal"]))
        self.sinData = Label(self.frame, bg="white", fg="black", width=10, height=1, font=(self.root.frontType, self.root.frontSize["normal"]))
        self.sinData.config(text="0")

        self.cosDataLabel = Label(self.frame, text="Cos Value", bg="white", font=(self.root.frontType, self.root.frontSize["normal"]))
        self.cosData = Label(self.frame, bg="white", fg="black", width=10, height=1, font=(self.root.frontType, self.root.frontSize["normal"]))
        self.cosData.config(text="1")

        self.publish()

    def publish(self):
        self.frame.grid(row=12, column=1, rowspan=20, columnspan=10, padx=5, pady=5, sticky='w')

        self.fileNameLabel.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.fileName.grid(row=0, column=1, padx=5, pady=5)

        self.btnBrowse.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.savePath.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        self.saveDataLabel.grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.saveData.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        self.sinDataLabel.grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.sinData.grid(row=4, column=0, padx=5, pady=5, sticky='w')

        self.cosDataLabel.grid(row=5, column=0, padx=5, pady=5, sticky='w')
        self.cosData.grid(row=6, column=0, padx=5, pady=5, sticky='w')

    def updateTableView(self):
        self.sinData.config(text=self.dataPool.msg[0])
        self.cosData.config(text=self.dataPool.msg[1])

    def savingData(self):
        if self.clickSave.get():
            self.dataPool.saving = True
            self.saveData["text"] = "...Saving data..."

            self.dataPool.getPath(self.savePath.get(), self.fileName.get())

        else:
            self.dataPool.saving = False
            self.saveData["text"] = ""

    def browseFolder(self):
        folderSelected = filedialog.askdirectory()
        if folderSelected:  # Nếu người dùng chọn thư mục
            self.savePath.delete(0, END)  # Xóa nội dung cũ
            self.savePath.insert(0, folderSelected)  # Ghi đường dẫn vào entry
            self.dataPool.getPath(self.savePath.get(), self.fileName.get())
    
class GraphView:
    def __init__(self, root, dataPool):
        self.root = root
        self.dataPool = dataPool

        self.frame = LabelFrame(root, text="System Observation Graph", bg="white", font=(self.root.frontType, self.root.frontSize["frame"]),
                                padx=5, pady=5)
        self.frame.grid(row=1, column=15, padx=5, pady=18, rowspan=20, columnspan=10,
                        sticky="nsew")
        
        self.prop = FontProperties(family='Times New Roman', weight='normal', size=16)

        self.fig = plt.figure(figsize=(7.6, 5.2), dpi=100)
        self.ax = self.fig.add_subplot(111)

        plt.ion()
        self.showGraph()


    def showGraph(self):
        self.ax.set_title("Real-Time State Diagram", fontproperties=self.prop)
        self.ax.set_xlabel("Time (s)", fontproperties=self.prop)
        self.ax.set_ylabel("Value", fontproperties=self.prop)

        self.ax.set_ylim(-60, 60)

        # self.ax.tick_params(axis='x', labelsize=14)  # Cập nhật kích thước font trục X
        # self.ax.tick_params(axis='y', labelsize=14)  # Cập nhật kích thước font trục Y

        # # Cập nhật font cho các nhãn trục X và Y
        # for label in self.ax.get_xticklabels():
        #     label.set_fontproperties(self.prop)

        # for label in self.ax.get_yticklabels():
        #     label.set_fontproperties(self.prop)

        self.ax.grid(color='b', linestyle='-', linewidth=0.2)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().grid(row=0, column=2, sticky="nsew",
                                         padx=5, pady=5)

        

        # self.sinLine, = self.ax.plot([], [], label="Sin", color="red")
        # self.cosLine, = self.ax.plot([], [], label="Cos", color="blue")

        # return self.sinLine, self.cosLine
        # self.ax.legend(prop=self.prop)

    def updateGraphView(self):
        self.ax.clear()

        self.showGraph() 

        self.ax.plot(self.dataPool.timeList, self.dataPool.sinList, 'g-', label="Sine Wave")
        self.ax.plot(self.dataPool.timeList, self.dataPool.cosList, 'r-', label="Cos Wave")
        self.ax.legend(loc='upper right')

        length = len(self.dataPool.timeList)
        self.ax.set_xlim(max(0, self.dataPool.timeList[length-1] - self.dataPool.timeDisplay), self.dataPool.timeList[length-1])

        # self.ax.relim()
        # self.ax.autoscale_view()
        self.canvas.draw()


if __name__ == "__main__":
    RootGUI()
    ComManager()
    ControlPanel()
    TableView()
    GraphView()
    