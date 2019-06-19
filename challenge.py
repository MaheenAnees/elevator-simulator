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
        self.current_floor = self.elevator.get_current_floor()
        print("elavtor started in floor." + str(self.current_floor)) 
        
    #update the current floor in ui 
    def update(self):
        self.current_floor = self.elevator.get_current_floor()
        self.root.after(self.elevator.travel_speed, self.update_widgets)

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
            #changing background color of button
            print("Button lights on")
            self.clicked_button.configure(bg="white")
            self.clicked_button.configure(fg="black")
        else:
            print("Button lights off")
            self.clicked_button.configure(bg="black")
            self.clicked_button.configure(fg="white")
          
        
    #handle door opens and close 
    def door(self):
        self.current_frame.configure(bg="white")    
        print("door opens")
        self.root.after(300, lambda: self.current_frame.configure(bg="blue"))
        print("door closes")
        print("###############")

    #handle button clicks 
    def call_elevator(self, dist, text):
        #boolean flag status for light
        self.elevator.button_light = True
        #saving the current object of button
        self.current_frame = self.elevator_box_frame[dist]
        #call the light function, pass it the button that is clicked
        if(text=="UP"):
            self.clicked_button = self.up_buttons[dist]
        elif(text=="DOWN"):
            self.clicked_button = self.down_buttons[dist]
        else:
            self.clicked_button = self.dist_floor_button[dist]
        self.light()
        #starting the main engine from the elevator class
        
        #state of the elevator whether is it tarveling or not
        if not self.elevator.traveling_state:
            #this should be the first ever call
            #or after idle time
            #append to the list if it's empty
            #starting the main engine from the elevator class
            self.elevator.move_elevator(dist)
            print("Distination "+str(dist))
            #change status to true, so next calls is added to the list
            self.elevator.traveling_state = True
        else:
            pass

        self.on_arrival()
    
    #open, close door, turn off light
    def on_arrival(self):
       self.root.after(self.elevator.travel_speed, self.light)
       self.root.after(self.elevator.travel_speed, self.door)
       self.elevator.traveling_state = False

class Elevator():  
    def __init__(self):
        self.traveling_state = False
        self.number_of_floors = 7
        self.list_of_dist_floors=[]
        #idle time 120 seconds
        self.idle_time = 120 
        #start value for direction
        self.direction = None
        #elevator speed moving to floor 1 sec
        self.travel_speed = 2000
        #elevator door open/close timing 1 sec
        self.door_time = 1000
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

    #access modifier for last activity
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

    #this function travels from current to distintion
    def move_elevator(self, dist):
        self.list_of_dist_floors.append(dist)
        for dist_floor in self.list_of_dist_floors:
            difference = self.calculate_moving_difference(dist_floor)
            if difference > 0: 
                self.direction = "UP"
                print("Elevator goes " + self.direction)
                for i in range(1, difference+1):
                    self.set_current_floor(self.get_current_floor()+1)
                    self.add_floors()
                    print("Elevator in floor."+ str(self.get_current_floor()))  
                print("Elevator reaches floor."+str(self.get_current_floor()))
                #ui.basic_ui()
            elif difference < 0:
                self.direction = "DOWN"
                print("Elevator goes " + self.direction)
                for i in range(1, difference*-1+1):
                    elevator.set_current_floor(self.get_current_floor()-1)
                    self.add_floors()
                    print("Elevator in floor."+ str(self.get_current_floor()))
                    #ui.update()
                print("Elevator reaches floor."+str(self.get_current_floor()))
            else:
                elevator.set_current_floor(self.get_current_floor())
                print("Elevator is here already")
            ui.update()
            #remove the first distnation floor from the list
            self.list_of_dist_floors.remove(dist_floor)
            #change button light and door flags
            self.button_light = False
        #run the background idle time again
        #killing old idle time thread
        self.new_thread = True
        time.sleep(0.1)
        self.new_thread = False
        self.run_time_thread() 


    #checks if there are any calls on the way and add it to the list
    def add_floors(self):
        if ui.dist_floor_button[self.get_current_floor()].cget('bg') == "white" or ui.up_buttons[self.get_current_floor()].cget('bg') == "white":
            #if there is calls from outside, stop the elevator
            ui.update()
        if ui.down_buttons[self.get_current_floor()].cget('bg') == "white":
            #if there is a requested floor in the trip
            ui.update()
        
        
if __name__ == "__main__":
    elevator = Elevator()
    root = Tk()
    root.title("Elevator Simulation Challenge")
    ui = Ui(root, elevator)
    ui.basic_ui()
    ui.update()
    root.mainloop()


#class Floor():
#    def __init__( self, fromFloor, toFloor ):
#        self.fromFloor = fromFloor
#        self.toFloor = toFloor
#        self.direction = ""
#        self.__currentFloor = 4
#
#    # send the current and requested floor to the engine
#    def send_floors(self):
#        Elevator.fromFloor = self.fromFloor
#        Elevator.toFloor = self.toFloor
#        Elevator.currentFloor = self.__currentFloor 
#    
#    def set_current_floor(self, value):
#        self.__currentFloor = value
#    
#    def get_current_floor(self):
#        return self.__currentFloor
#
#class Passengers():
#    def __init__(self, numberOfPassengers ):
#        self.numberOfPassengers = numberOfPassengers
#    def send_passengers(self):
#        Elevator.numberOfPassengers = self.numberOfPassengers
