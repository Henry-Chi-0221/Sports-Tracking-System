from locale import currency
from simple_pid import PID
import cv2
from time import time
import random
import numpy as np
class eptz(object):
    def __init__(self ,cap):
        self.cap = cap
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

         # PID parameters
        self.kp = 0.005
        self.ki = 0.2
        self.kd = 0.1

        self.current_x = self.width//2
        self.current_y = self.height//2
        self.current_zoom = 1

    def pid(self,target,current):
        des_point = target
        pid = PID( 
                self.kp, 
                self.ki, 
                self.kd, 
                setpoint=des_point,
            )
        pid.sample_time = 0.1
        pid_output = pid(current, dt=pid.sample_time)
        return pid_output
            
    def zoom(self,zoom_ratio = 1  , x_offset =0 , y_offset = 0):
        x_center,y_center = self.width//2 , self.height//2
        width = self.width//zoom_ratio
        height = self.height//zoom_ratio
        x_center = x_offset
        y_center = y_offset
        x1 , x2 = x_center - (width//2) , x_center + (width//2)
        y1 , y2 = y_center - (height//2) , y_center + (height//2)
        x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)
        return x1,y1,x2,y2

    def run(self ,img, zoom_ratio = 1  , x_pos =0 , y_pos = 0):
        
        pid_x = self.pid(x_pos , self.current_x)
        #y_offset += self.height //2

        if  self.width*0.5*(1/self.current_zoom) < self.current_x + pid_x < self.width*(1-0.5*(1/self.current_zoom)):
            self.current_x += pid_x
        
        pid_y = self.pid(y_pos , self.current_y) # target current
        if  self.height*0.5*(1/self.current_zoom) < self.current_y + pid_y < self.height*(1-0.5*(1/self.current_zoom)):
            self.current_y += pid_y
        
        pid_zoom = self.pid(zoom_ratio , self.current_zoom)
        
        if(0 < self.current_zoom + pid_zoom < 3) and (1):
            self.current_zoom += pid_zoom

        x1,y1,x2,y2 = self.zoom(zoom_ratio=self.current_zoom,x_offset=self.current_x,y_offset=self.current_y) #x
        
        res_x = np.clip(np.array([x1,x2]) , 0 , self.width)
        res_y = np.clip(np.array([y1,y2]) , 0 , self.height)
        (x1,x2), (y1,y2) = res_x[:] , res_y[:]
        

        cv2.rectangle(img , (x1,y1) , (x2,y2) , (255,255,255) , 1)
        resized = cv2.resize(img[y1:y2,x1:x2] , (self.width , self.height))
        
        return img ,resized
        

if __name__ == "__main__":
    cap = cv2.VideoCapture('test.mp4')
    eptz_control = eptz(cap=cap)
    x ,y,z = 640 , 360 ,2
    current_time = time()
    while(cap.isOpened()):
        ret , frame = cap.read()
        if not ret:
            break
        
        if (time() - current_time )>1:
            #y += 10
            #print(y)
            x = random.uniform(0 , 1280)
            y = random.uniform(0 , 720)
            z = random.uniform(1.5, 3.0)
            current_time = time()
          
        src , resized = eptz_control.run(frame,zoom_ratio=z ,x_pos= x,y_pos= y)
        cv2.imshow("src" , frame)
        cv2.imshow("resized" , resized)
        if cv2.waitKey(1) & 0xff==ord('q'):
            break
    pass