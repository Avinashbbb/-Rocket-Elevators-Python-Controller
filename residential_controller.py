from asyncio.windows_events import NULL
from pyparsing import null_debug_action
from time import sleep

elevatorID = 1
floorRequestButtonID = 1
callButtonID = 1

class Column:
    def __init__(self, _id, _amountOfFloors, _amountOfElevators):
        self.ID = _id
        self.status = "online"
        self.elevatorList = []
        self.callButtonList = []
        self.createElevators(_amountOfFloors,_amountOfElevators)
        self.createCallButtons(_amountOfFloors)

    def createElevators(self,_amountOfFloors,_amountOfElevators):
        global elevatorID
        for x in range(_amountOfElevators):
            elevator = Elevator(elevatorID,_amountOfFloors)
            self.elevatorList.append(elevator)
            elevatorID += 1

    def createCallButtons(self,_amountOfFloors):
        global callButtonID
        buttonFloor = 1
        for x in range(_amountOfFloors):
            if buttonFloor < _amountOfFloors:
                callButton = CallButton(callButtonID,buttonFloor,"up")
                self.callButtonList.append(callButton)
                callButton.ID += 1
            if buttonFloor > 1:
                callButton = CallButton(callButtonID,buttonFloor,"down")
                self.callButtonList.append(callButton)
                callButton.ID += 1
            buttonFloor += 1
    
    def requestElevator(self,floor,direction):
        elevator = self.findElevator(floor,direction)
        elevator.floorRequestList.append(floor)
        elevator.move()
        elevator.operateDoors()
        return elevator

    def findElevator(self,requestedFloor,requestedDirection):
        bestElevator = None
        bestScore = 5
        referenceGap = 10000000
        bestElevatorInformations = None

        for i in self.elevatorList:
            if requestedFloor == i.currentFloor and i.status =="stopped" and requestedDirection == i.direction:
                bestElevatorInformations = self.checkIfElevatorIsBetter(1,i,bestScore,referenceGap,bestElevator,requestedFloor)
            elif requestedFloor > i.currentFloor and i.direction =="up" and requestedDirection == i.direction:
                bestElevatorInformations = self.checkIfElevatorIsBetter(2,i,bestScore,referenceGap,bestElevator,requestedFloor)
            elif requestedFloor < i.currentFloor and i.direction == "down" and requestedDirection == i.direction:
                bestElevatorInformations = self.checkIfElevatorIsBetter(2,i,bestScore,referenceGap,bestElevator,requestedFloor)
            elif i.status == "idle":
                bestElevatorInformations = self.checkIfElevatorIsBetter(3,i,bestScore,referenceGap,bestElevator,requestedFloor)
            else:
                bestElevatorInformations = self.checkIfElevatorIsBetter(4,i,bestScore,referenceGap,bestElevator,requestedFloor)
            bestElevator = bestElevatorInformations["bestElevator"]
            bestScore = bestElevatorInformations["bestScore"]
            referenceGap = bestElevatorInformations["referenceGap"]
        return bestElevator
    def checkIfElevatorIsBetter(self,scoreToCheck,newElevator,bestScore,referenceGap,bestElevator,floor):
        if scoreToCheck < bestScore:
            bestScore = scoreToCheck
            bestElevator = newElevator
            referenceGap = abs(newElevator.currentFloor - floor)
        elif bestScore == scoreToCheck:
            gap = abs(newElevator.currentFloor - floor)
            if referenceGap >gap:
                bestElevator = newElevator
                referenceGap = gap
        bestElevatorInformations = {"bestElevator":bestElevator,"bestScore":bestScore,"referenceGap":referenceGap}
        return bestElevatorInformations

class Elevator:
    def __init__(self, _id, _amountOfFloors):
        self.ID = _id
        self.status = "idle"
        self.currentFloor = 1
        self.direction = None
        self.overweight = False
        self.obstruction = False
        self.door = Door(_id)
        self.floorRequestButtonList = []
        self.floorRequestList = []
        self.createFloorRequestButtons(_amountOfFloors)

    def createFloorRequestButtons(self,_amountOfFloors):
        global floorRequestButtonID
        buttonFloor = 1
        for i in range(_amountOfFloors):
            floorRequestButton = None
            floorRequestButton = FloorRequestButton(floorRequestButtonID,buttonFloor)
            self.floorRequestButtonList.append(floorRequestButton)
            buttonFloor += 1
            floorRequestButtonID += 1
    
    def requestFloor(self,floor):
        self.floorRequestList.append(floor)
        self.move()
        self.operateDoors()
    
    def move(self):
        while len(self.floorRequestList) > 0:
            destination = self.floorRequestList[0]
            self.status = "moving"
            if self.currentFloor < destination:
                self.direction ="up"
                self.sortFloorList()
                while self.currentFloor < destination:
                    self.currentFloor += 1
                    self.screenDisplay = self.currentFloor
            elif self.currentFloor >destination:
                self.direction = "down"
                self.sortFloorList()
                while self.currentFloor >destination:
                    self.currentFloor -= 1
                    self.screenDisplay =self.currentFloor
            self.status = "stopped"
            self.floorRequestList.pop(0)
        self.status = "idle"

    def sortFloorList(self):
        if self.direction == "up":
            self.floorRequestList.sort()
        else:
            self.floorRequestList.sort(reverse=True)

    def operateDoors(self):
        self.door.status = "opened"
        sleep(5)
        if not self.overweight:
            self.door.status = "closing"
            if not self.obstruction:
                self.door.status = "closed"
            else:
                self.operateDoors()
        else:
            while self.overweight:
                print("overweight alarm")
            self.operateDoors()
            

class CallButton:
    def __init__(self,_id,_floor,_direction):
        self.ID = _id
        self.status = "idle"
        self.floor = _floor
        self.direction = _direction

class FloorRequestButton:
    def __init__(self,_id,_floor):
        self.ID = _id
        self.status ="idle"
        self.floor = _floor

class Door:
    def __init__(self,_id):
        self.ID = _id
        self.status = "idle"