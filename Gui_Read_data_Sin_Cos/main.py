from GuiManager import RootGUI, WidgetManeger
from SerialCommunicator import SerialCtrl
from DataReciver import DataPool

def main():
    try:
        monitor = RootGUI()

        dataPool = DataPool()

        serial = SerialCtrl()

        WidgetManeger(monitor.root, serial, dataPool)
        
        monitor.open()



    except KeyboardInterrupt:
        print("Intrupted by user")

if __name__ == "__main__":
    main()

