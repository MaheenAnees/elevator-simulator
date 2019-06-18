from random import randint
import sys
import threading
import datetime
if sys.version_info[0] < 3:
    from Tkinter import *     ## Python 2.x
else:
    from tkinter import *     ## Python 3.x
import time


class Ui():
    def __init__(self, master, elevator):
        #widgets
        self.elevator = elevator
        self.current_floor = self.elevator.get_current_floor()
        self.root = master
        self.dist_floor = None
        self.up_buttons = {}
        self.down_buttons = {}
        self.dist_floor_button = {}
        self.clicked_button = None
        self.floor_frame = None
        self.elevator_box_frame = {}
        self.elevator_frame = Frame (self.root, width = 500, height = 800, padx=20, pady=20)
        self.elevator_frame.pack_propagate(False)
        self.elevator_frame.pack() 
        self.button_box_frame = {}
        self.number_of_floors = self.elevator.number_of_floors
        self.current_floor = IntVar()
        self.current_floor.set(self.elevator.get_current_floor()) 
        print("elavtor started in floor." + str(self.current_floor.get())) 
        
    #update the current floor in ui 
    def update(self):
        self.current_floor = elevator.get_current_floor()
        #time.sleep(0.5)
        self.root.after(500, self.update_widgets)

    #Initial ui widgets
    def basic_ui(self): 
        floors = [i for i in range(self.number_of_floors+1)]
        #The first floor start at 0 and last floor is 7
        for floor in floors:
            #Frame for each floor to be created
            self.floor_frame = Frame(self.elevator_frame, width = 700, height =200, pady=2)  
            self.floor_frame.pack(side = BOTTOM)
            #floor index to be passed to the callback func
            self.up_buttons[floor] = Button(self.floor_frame, text="UP", bg="black", fg="white", command = lambda floor=floor, text="UP" : self.call_elevator(floor, text))
            self.up_buttons[floor].pack(side = LEFT) 
            self.down_buttons[floor] = Button(self.floor_frame, text="DOWN", bg="black", fg="white", command = lambda floor=floor, text="DOWN" : self.call_elevator(floor, text))
            self.down_buttons[floor].pack(side = LEFT) 
            #Elevator Box
            self.elevator_box_frame[floor] = Frame(self.floor_frame, width = 320, height =90, bg="blue", padx=10, pady=20)
            self.elevator_box_frame[floor].pack_propagate(False)
            self.elevator_box_frame[floor].pack(side=RIGHT)
            if floor == self.elevator.get_current_floor():
                self.current_frame = self.elevator_box_frame[floor]
    
    #update the buttons in the current floor 
    def update_widgets(self): 
        #delete old widgets
        if self.button_box_frame != {}:
            self.button_box_frame.pack_forget()
        floors = [i for i in range(self.number_of_floors+1)]
        #buttonbox built on the current floor
        self.button_box_frame = Frame(self.elevator_box_frame[self.current_floor], width = 320, height =90, bg="white", padx=5, pady=10)
        self.button_box_frame.pack_propagate(False)
        self.button_box_frame.pack()
        for floor in floors:
            #passing the distiantion floor index in the callback
            self.dist_floor_button[floor]= Button(self.button_box_frame ,text=str(floor), bg="blue", fg="white", command = lambda dist_floor = floor, text="INBUTTON": self.call_elevator(dist_floor, text))
            self.dist_floor_button[floor].pack(side=LEFT)  
         
    #change lights on and off  
    def light(self):
        if self.elevator.button_light:
            print("Button lights on")
            self.clicked_button.configure(bg="white")
            self.clicked_button.configure(fg="black")
        else:
            print("Button lights off")
            self.clicked_button.configure(bg="black")
            self.clicked_button.configure(fg="white")
    
    #handle door opens and close 
    def door(self):
        if self.elevator.door_open:
            print("door opens")
            self.current_frame.configure(bg="white")
            #set the flag to false to close it
            self.elevator.door_open = False
        else:
            print("door closes")
            self.current_frame.configure(bg="blue")
    
    #handle button clicks 
    def call_elevator(self, dist, text):
        if self.elevator.button_light:
            #checking if the button is already on
            #it means that the elevator is going somewhere
            #this will start anew thread of elevator travel
            if self.currentFloor <= dist < self.dist_floor and text == "UP": 
                thread = threading.Thread(target=self.elevator.move_elevator, args=(dist, self.elevator))
                thread.daemon = True
                thread.start()
            elif self.dist_floor <= dist < self.current_floor and text == "DOWN":
                thread = threading.Thread(target=self.elevator.move_elevator, args=(dist, self.elevator))
                thread.daemon = True
                thread.start() 
        else:
            self.dist_floor = dist
            #boolean flag status for light
            self.elevator.button_light = True
            #saving the current object of button
            self.current_frame = self.elevator_box_frame[dist]
            #call the light function, pass it 
            #the right button to light up
            if(text=="UP"):
                self.clicked_button = self.up_buttons[dist]
            elif(text=="DOWN"):
                self.clicked_button = self.down_buttons[dist]
            else:
                self.clicked_button = self.dist_floor_button[dist]
            self.light()
            #starting the main engine from the elevator class
            self.elevator.move_elevator(dist, self.elevator)
            self.root.after(500, self.light)
            self.root.after(500, self.door) 
            self.root.after(1000, self.door)
    
class Elevator():  
    def __init__(self):
        self.number_of_floors = 7
        #idle time 120 seconds
        self.idle_time = 120 
        #start value for direction
        self.direction = None
        #assume the starting floor is random
        self.__current_floor = randint(0, self.number_of_floors)
        #last activity the elevator done
        self.__last_activity = datetime.datetime.now()
        #flags to change door and light 
        self.button_light = False
        self.door_open = False
        #run idle timer as background thread
        self.new_thread = False
        self.run_time_thread()
        
        
    # run the thread of idle time on background
    def run_time_thread(self):
        if(self.get_current_floor() != 4):
            thread = threading.Thread(target=self.idle_timer, args=())
            thread.daemon = True
            thread.start()
    
    def light(self):
        if(self.button_light):
            print("light is on")
        else:
            print("light is off")
    
    # when the elevator is idle for 2 minutes
    def idle_timer(self):
        #background thread run every second 
        #till idle time becomes 120 seconds
        self.set_last_activity(datetime.datetime.now())
        #if a new thread is started before 
        #120 seconds a new  thread starts
        while not self.new_thread:
            time_difference =  datetime.datetime.now()-self.__last_activity
            if(time_difference.seconds >= self.idle_time):
                self.set_current_floor(4)
                ui.update()
                print("Elevator was idle 2 minutes and go to floor.4")
                break
            else:
                time.sleep(0.1)  

    #access modeifier for time
    def set_last_activity(self, time):
        self.__last_activity = time 
    def get_last_activity(self):
        return self.__last_activity

    #differnces between floors
    def calculate_moving_difference(self, dist_floor):
        difference = dist_floor - self.__current_floor
        return(difference)

    #access modifier for floors
    def set_current_floor(self, value):
        self.__current_floor = value 
    def get_current_floor(self):
        return self.__current_floor

    # elevator functions
    def move_elevator(self, dist_floor, elevator):
        difference = self.calculate_moving_difference(dist_floor)
        if difference > 0: 
            self.direction = "UP"
            print("Elevator goes " + self.direction)
            for i in range(1, difference+1):
                elevator.set_current_floor(elevator.get_current_floor()+1)
                print("Elevator in floor."+ str(elevator.get_current_floor()))
                ui.update()    
            print("Elevator reaches floor."+str(elevator.get_current_floor()))
            #ui.basic_ui()
        elif difference < 0:
            self.direction = "DOWN"
            print("Elevator goes " + self.direction)
            for i in range(1, difference*-1+1):
                elevator.set_current_floor(elevator.get_current_floor()-1)
                print("Elevator in floor."+ str(elevator.get_current_floor()))
                ui.update()
            print("Elevator reaches floor."+str(elevator.get_current_floor()))
        else:
            elevator.set_current_floor(elevator.get_current_floor())
            print("Elevator is here already")
            ui.update()

        #run the background idle time again
        #killing old idle time thread
        self.new_thread = True
        time.sleep(0.1)
        self.new_thread = False
        self.run_time_thread() 
        #change button light and door flags
        self.button_light = False
        self.door_open = True

    # increase and decrease number of passengers as we stops
    def passengers(self):
        if(self.insideButton):
            self.numberOfPassengers = self.numberOfPassengers - 1
            print("passenger get out")
        elif(self.outsideButton):
            self.numberOfPassengers = self.numberOfPassengers + 1
            print("passenger get in")
        return(self.numberOfPassengers) 



class Floor():
    def __init__( self, fromFloor, toFloor ):
        self.fromFloor = fromFloor
        self.toFloor = toFloor
        self.direction = ""
        self.__currentFloor = 4

    # send the current and requested floor to the engine
    def send_floors(self):
        Elevator.fromFloor = self.fromFloor
        Elevator.toFloor = self.toFloor
        Elevator.currentFloor = self.__currentFloor 
    
    def set_current_floor(self, value):
        self.__currentFloor = value
    
    def get_current_floor(self):
        return self.__currentFloor



class Passengers:
    def __init__(self, numberOfPassengers ):
        self.numberOfPassengers = numberOfPassengers 

    def send_passengers(self):
        Elevator.numberOfPassengers = self.numberOfPassengers


if __name__ == "__main__":
    elevator = Elevator()
    root = Tk()
    root.title("Elevator Simulation Challenge")
    ui = Ui(root, elevator)
    ui.basic_ui()
    ui.update()
    root.mainloop()

#ref:http://www.diva-portal.se/smash/get/diva2:811554/FULLTEXT01.pdf
