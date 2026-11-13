import serial
import time
import matplotlib.pyplot as plt



class loadcell():
    def __init__(self) -> None:
        pass
    def setup(self):
        try:
            self.arduino = serial.Serial("/dev/ttyACM0",2000000)
        except:
            print("check the port !")
        start_time = time.time()
        current_time = time.time() - start_time
        force_1 = []
        force_2 = []
        self.k_x = 0.2682
        self.k_y = 0.2246
        print('calibrating takes 4 seconds')
        print(current_time)
        while(current_time < 4):
            current_time = time.time() - start_time
            print(current_time)
            # print(line)
            print('calibrating takes 4 seconds')
            try: 
                print('calibrating takes 4 seconds')
                self.arduino.flushInput()
                line = self.arduino.readline()
                string = line.decode('utf-8')  # convert the byte string to a unicode string
                string = string.replace('\r\n', '')
                # print(string)
                # print(("a" in string) and ("b" in string))
                condition = ("a" in string) and ("b" in string)
                # print(condition)
                if(condition):
                    string = string.replace("a","")
                    string = string.replace("b","")
                    # print(string)
                    [sensor_data1, sensor_data2]= string.split(',')
                    
                    # print(float(sensor_data1), float(sensor_data2))

                    force_1.append(float(sensor_data1))

                    force_2.append(float(sensor_data2))
            except:
                print('calibrating takes 4 seconds')
        print('calibrating finished!')
        # print(round(sum(force_1)/len(force_1)), round(sum(force_2)/len(force_2)))
        # print(force_1)
        self.b_x = self.k_x * round(sum(force_1)/len(force_1))
        self.b_y = self.k_y * round(sum(force_2)/len(force_2))
        self.last_f_x = 0
        self.last_f_y = 0
    def read_force(self):
        start_time = time.time()
        # self.arduino.flushInput()

        data = self.arduino.inWaiting()
        line = self.arduino.readline(data)
        # print("spend_time", time.time()-start_time)

        
        # print(line)
        try: 
            string = line.decode('utf-8')  # convert the byte string to a unicode string
            string = string.replace('\r\n', '')
            # print(string)
            string = string.splitlines()
            
            string = string[len(string)-1]
            # print(string)
            condition = ("a" in string) and ("b" in string)
                # print(condition)
            if(condition):
                string = string.replace("a","")
                string = string.replace("b","")
                [sensor_data1, sensor_data2]= string.split(',')
                force_1 = self.k_x * float(sensor_data1) - self.b_x
                force_2 = self.k_y * float(sensor_data2) - self.b_y
            # print(force_1, force_2)
            if(force_1 < -200 or force_1 > 200):
                force_1 = self.last_f_x
            if(force_2 < -200 or force_2 > 200):
                force_2 = self.last_f_y  
            self.last_f_x = force_1
            self.last_f_y = force_2         
        except:
            # print('oop')
            force_1 = self.last_f_x
            force_2 = self.last_f_y
        
        return force_1, force_2

        

if __name__ == '__main__':
    loadcell1 = loadcell()
    loadcell1.setup()
    fig6, pp = plt.subplots()
    pp.set_title('force readings', fontsize=10)
    pp.set_xlabel('time(s)', fontsize=10)
    pp.set_ylabel('force(N)', fontsize=10)
    pp.grid(True)

    ppp, = pp.plot([],[], 'r', linewidth=3)
    pppp, = pp.plot([],[], 'g', linewidth=3)
    pp.legend(['x','y'])
    start_time = time.time()
    current_time = time.time() - start_time
    time_l = []
    force_X = []
    force_Y = []
    n = 0
    while(1):
        current_time = time.time() - start_time
        a,b = loadcell1.read_force()
        time_l.append(current_time)
        
        force_X.append(a)
        force_Y.append(b)
        ppp.set_xdata(time_l)
        ppp.set_ydata(force_X)
        pppp.set_xdata(time_l)
        pppp.set_ydata(force_Y)
        pp.relim()
        pp.autoscale_view()
        plt.draw()
        plt.pause(0.00001)
        n=n+1
        print(n/current_time)

        
