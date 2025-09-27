"""
customer class
"""
from enum import Enum


class Customer:
    class CustomerType(Enum):
        HomeDelivery = 0
        SelfPickUp = 1
        depot = 2

    def __init__(self):
        self.p:int  = 0 # the production time
        self.alpha: int = 0 # the completion time
        self.beta: int = 0 # the delivery time
        self.label: Customer.CustomerType = Customer.CustomerType.depot # the customer label
        self.coords:tuple = (0, 0)

    def setArrivalTime(self, a = 0):
        if self.label == Customer.CustomerType.HomeDelivery: self.a = a
        else: raise Exception("Only Home Delivery Customer can be set Arrival Time")

    def setDepartureTime(self, d = 0):
        if self.label == Customer.CustomerType.HomeDelivery: self.d = d
        else: raise Exception("Only Home Delivery Customer can be set Departure Time")

    def setTime(self, p, alpha, beta):
        self.p = p
        self.alpha = alpha
        self.beta = beta

    def setProductionTime(self, p):
        self.p = p

    def setLabel(self, label:"CustomerType"):
        self.label = label

    def getLabel(self):
        return self.label

    def getTime(self):
        return self.p, self.alpha, self.beta

    def getProductionTime(self):
        return self.p

    def setCompletionTime(self, alpha):
        self.alpha = alpha

    def getCompletionTime(self):
        return self.alpha

    def setDeliveryTime(self, beta):
        self.beta = beta

    def getDeliveryTime(self):
        return self.beta

    def getArrivalTime(self):
        if self.label == Customer.CustomerType.HomeDelivery:
            return self.a
        else: raise Exception("Only Home Delivery Customer can be got its Arrival Time")

    def getDepartureTime(self):
        if self.label == Customer.CustomerType.HomeDelivery:
            return self.d
        else: raise Exception("Only Home Delivery Customer can be got its Departure Time")

    def setBatchCompletionTime(self, A = 0):
        if self.label == Customer.CustomerType.HomeDelivery: self.A = A
        else: raise Exception("Only Home Delivery Customer can be set Batch Completion Time")

    def getBatchCompletionTime(self):
        if self.label == Customer.CustomerType.HomeDelivery: return self.A
        else: raise Exception("Only Home Delivery Customer can be got its Batch Completion Time")

    def setCoords(self, coords:tuple):
        self.coords = coords

    def getCoords(self):
        return self.coords

if __name__ == "__main__":
    try:
        c1 = Customer()
        c2 = Customer()
        print(f"the time of c1:{c1.getTime()}, the time of c2:{c2.getTime()}")
        print(f"The Type of c1:{c1.getLabel()}, the Type of c2:{c2.getLabel()}")
        c1.setLabel(Customer.CustomerType.HomeDelivery)
        c2.setLabel(Customer.CustomerType.SelfPickUp)
        print(f"The Type of c1:{c1.getLabel()}, the Type of c2:{c2.getLabel()}")
        c1.setArrivalTime(10)
        print(f"The Arrival Time of c1:{c1.getArrivalTime()}")
        c2.setArrivalTime(10)
        print(f"The Arrival Time of c2:{c2.getArrivalTime()}")
        c1.setDepartureTime(15)
        print(f"The Departure Time of c1:{c1.getArrivalTime()}")
        c2.setDepartureTime(15)
        print(f"The Departure Time of c1:{c2.getArrivalTime()}")
    except Exception as e:
        print(e)