from copy import deepcopy
from math import sqrt

from customer import Customer
import matplotlib.pyplot as plt

def Eucdist(coords1:tuple, coords2:tuple):
    eucdist = sqrt((coords1[0]- coords2[0]) ** 2 + (coords1[1] - coords2[1]) ** 2)
    return eucdist

def Route(vehArcList:"list[tuple[int,int]]"):
    route = [0]
    cur = 0 # current node
    succ = 0 # successor node
    for idx in range(len(vehArcList)):
        for item in vehArcList:
            if item[0] == cur:
                succ = item[1] # note that the successor node of the current node
                route.append(succ)
                break
            else: continue
        cur = succ
    return route

def Sequence(route: "list[int]", sequencelist: "list[tuple[int, int, int]]")->list[int]:
    rt = deepcopy(route)
    del rt[0], rt[len(rt) - 1] # 删除depot
    sequence = []
    for item1 in rt:
        batchsequnce = []
        for item2 in sequencelist:
            if item2[2] == item1:
                batchsequnce.append((item2[0], item2[1]))
            else:
                continue
        cur = 0
        succ = 0
        for idx in range(len(batchsequnce)):
            for item in batchsequnce:
                if item[0] == cur and item[1] != 0:
                    succ = item[1]
                    sequence.append(succ)
                    break
                else: continue
            cur = succ
    return sequence

def Allocation(route:"list[int]", cptoArcList:"list[tuple[int,int]]")->"dict[[int],list[int]]":
    rt = deepcopy(route)
    del rt[0], rt[len(rt) - 1]
    allocation = {}
    for item1 in rt:
        batchallocation = []
        for item2 in cptoArcList:
            if item2[1] == item1:
                batchallocation.append(item2[0])
            else: continue
        allocation[item1] = batchallocation
    return allocation

def decodeCompletion(nodelist: "list[Customer]",sequence:list):
    startTime = 0
    for seq in sequence:
        completionTime = startTime + nodelist[seq].getProductionTime()
        nodelist[seq].setCompletionTime(completionTime)
        startTime = completionTime

def decode0(nodelist:"list[Customer]", route:"list[int]", allocation:"dict[[int],list[int]]",sequence:"list[int]",
           vehdistdict:"dict[tuple[int,int], int]", cptohddistdict:"dict[tuple[int,int],int]"):
    decodeCompletion(nodelist, sequence) # setting production time
    rt = deepcopy(route)
    del  rt[0], rt[len(rt) - 1]
    startTime = 0
    departureTime = 0
    curidx = 0
    for idx1 in rt:
        arrivalTime = departureTime + vehdistdict[(curidx, idx1)]
        nodelist[idx1].setArrivalTime(arrivalTime) # 设置arrival time
        deliveryTime = max(arrivalTime, nodelist[idx1].getCompletionTime())
        nodelist[idx1].setDeliveryTime(deliveryTime) # 设置delivery time
        deliveryTimeList = [deliveryTime]
        batch = allocation[idx1]
        for idx2 in batch:
            arrivalTimeInBatch = nodelist[idx2].getCompletionTime() + cptohddistdict[(idx2, idx1)]
            deliveryTimeInBatch = max(arrivalTimeInBatch, arrivalTime)
            nodelist[idx2].setDeliveryTime(deliveryTimeInBatch) # 设置delivery time
            deliveryTimeList.append(deliveryTimeInBatch)
        departureTime = max(deliveryTimeList) # 更新departure time
        nodelist[idx1].setDepartureTime(departureTime) #设置 departure time
        curidx = idx1

def decode1(nodelist:"list[Customer]", route:"list[int]", allocation:"dict[[int],list[int]]",sequence:"list[int]",
           vehdistdict:"dict[tuple[int,int], int]", cptohddistdict:"dict[tuple[int,int],int]"):
    decodeCompletion(nodelist, sequence)  # setting production time
    rt = deepcopy(route)
    del rt[0], rt[len(rt) - 1]
    startTime = 0
    departureTime = 0
    curidx = 0
    for idx1 in rt:
        arrivalTime = departureTime + vehdistdict[(curidx, idx1)]
        nodelist[idx1].setArrivalTime(arrivalTime)  # 设置arrival time
        deliveryTime = max(arrivalTime, nodelist[idx1].getCompletionTime())
        nodelist[idx1].setDeliveryTime(deliveryTime)  # 设置delivery time
        deliveryTimeList = [deliveryTime]
        batch = allocation[idx1]
        for idx2 in batch:
            arrivalTimeInBatch = nodelist[idx1].getArrivalTime() + cptohddistdict[(idx2, idx1)]
            deliveryTimeInBatch = max(arrivalTimeInBatch, nodelist[idx2].getCompletionTime())
            nodelist[idx2].setDeliveryTime(deliveryTimeInBatch)  # 设置delivery time
            deliveryTimeList.append(deliveryTimeInBatch)
        departureTime = max(deliveryTimeList)  # 更新departure time
        nodelist[idx1].setDepartureTime(departureTime)  # 设置 departure time
        curidx = idx1

def Gantt0(nodelist:"list[Customer]", veharclist:"list[tuple[int,int]]",cptohdarclist:"list[tuple[int,int]]",route:"list[int]", sequence:"list[int]",
          vehdistdict:"dict[tuple[int,int],int]", cptohddistdict:"dict[tuple[int,int], int]"):
    startTime = 0
    dict1 = {}
    for item in veharclist:
        if item[0] == 0:
            dict1[f"T{item[0]}->{item[1]}"] = (0, vehdistdict[(item[0], item[1])])
        else:
            dict1[f"T{item[0]}->{item[1]}"] = (nodelist[item[0]].getDepartureTime(), vehdistdict[(item[0], item[1])])
    dict2 = {}
    for item in cptohdarclist:
        dict2[f"T{item[0]}->{item[1]}"] = (nodelist[item[0]].getCompletionTime(), cptohddistdict[(item[0], item[1])])
    dict3 = {}
    for idx in sequence:
        productionTime = nodelist[idx].getProductionTime()
        completionTime = nodelist[idx].getCompletionTime()
        dict3[f"order {idx} "] = (startTime, productionTime)
        startTime = completionTime
    dict3 = dict(sorted(dict3.items(), key=lambda item: int(item[0].split()[1])))
    dict4 = {}
    for idx in range(len(route)-2):
        waittime = nodelist[route[idx+1]].getDepartureTime() - nodelist[route[idx+1]].getArrivalTime()
        if waittime > 0:
            dict4[f"T{route[idx]}->{route[idx + 1]}"] = (nodelist[route[idx + 1]].getArrivalTime(),
                                             waittime)
    fig, ax = plt.subplots(figsize = (15, 10))
    for key,value in dict1.items():
        ax.barh(key, value[1], left = value[0], height = 0.5, align = 'center', color = 'blue')
        ax.text(value[0]+value[1] -5, key, f"{value[0] + value[1]}", va='center')

    for key,value in dict2.items():
        ax.barh(key, value[1], left = value[0], height = 0.5, align = 'center', color = 'yellow')
        ax.text(value[0]+value[1] -5, key, f"{value[0] + value[1]}", va='center')

    for key,value in dict3.items():
        ax.barh(key, value[1], left=value[0], height=0.5, align='center', color='red')
        ax.text(value[0] + value[1]-5, key, f"{value[0] + value[1]}", va='center')

    for key,value in dict4.items():
        ax.barh(key, value[1], left=value[0], height=0.5, align='center', color='grey')
        ax.text(value[0] + value[1] / 2, key, f"{value[1]}", va='center')
    ax.set_yticks(range(len(dict1) + len(dict2) + len(dict3)))
    ax.set_yticklabels(list(dict1.keys()) + list(dict2.keys()) + list(dict3.keys()))
    ax.set_xlabel("Time")
    ax.set_ylabel("task")
    ax.set_title("Gantt Chart")
    plt.tight_layout()
    return fig

def Gantt1(nodelist:"list[Customer]", veharclist:"list[tuple[int,int]]",cptohdarclist:"list[tuple[int,int]]",route:"list[int]", sequence:"list[int]",
          vehdistdict:"dict[tuple[int,int],int]", cptohddistdict:"dict[tuple[int,int], int]"):
    startTime = 0
    dict1 = {}
    for item in veharclist:
        if item[0] == 0:
            dict1[f"T{item[0]}->{item[1]}"] = (0, vehdistdict[(item[0], item[1])]) # departure time, arrival time
        else:
            dict1[f"T{item[0]}->{item[1]}"] = (nodelist[item[0]].getDepartureTime(), vehdistdict[(item[0], item[1])])
    dict2 = {}
    dict5 = {}
    for item in cptohdarclist:
        dict2[f"T{item[0]}->{item[1]}"] = (nodelist[item[1]].getArrivalTime(), cptohddistdict[(item[0], item[1])])
        waittime = nodelist[item[0]].getCompletionTime() - (nodelist[item[1]].getArrivalTime()+cptohddistdict[(item[0], item[1])])
        if waittime > 0:
            dict5[f"T{item[0]}->{item[1]}"] = (nodelist[item[1]].getArrivalTime()+cptohddistdict[(item[0], item[1])], waittime)
    dict3 = {}
    for idx in sequence:
        productionTime = nodelist[idx].getProductionTime()
        completionTime = nodelist[idx].getCompletionTime()
        dict3[f"order {idx} "] = (startTime, productionTime)
        startTime = completionTime
    dict3 = dict(sorted(dict3.items(), key=lambda item: int(item[0].split()[1])))

    dict4 ={}
    for idx in range(len(route) - 2):
        waittime = nodelist[route[idx + 1]].getDepartureTime() - nodelist[route[idx + 1]].getArrivalTime()
        if waittime > 0:
            dict4[f"T{route[idx]}->{route[idx + 1]}"] = (nodelist[route[idx + 1]].getArrivalTime(),
                                                           waittime)
    fig, ax = plt.subplots(figsize = (15, 10))

    for key,value in dict1.items():
        ax.barh(key, value[1], left = value[0], height = 0.5, align = 'center', color = 'blue')
        ax.text(value[0]+value[1]-5, key, f"{value[0] + value[1]}", va='center')

    for key,value in dict2.items():
        ax.barh(key, value[1], left = value[0], height = 0.5, align = 'center', color = 'yellow')
        ax.text(value[0]+value[1]-5, key, f"{value[0] + value[1]}", va='center')

    for key,value in dict3.items():
        ax.barh(key, value[1], left=value[0], height=0.5, align='center', color='red')
        ax.text(value[0] + value[1]-5, key, f"{value[0] + value[1]}", va='center')

    for key,value in dict4.items():
        ax.barh(key, value[1], left=value[0], height=0.5, align='center', color='grey')
        ax.text(value[0] + value[1] / 2, key, f"{value[1]}", va='center')

    for key,value in dict5.items():
        ax.barh(key, value[1], left=value[0], height=0.5, align='center', color='grey')
        ax.text(value[0] + value[1] / 2, key, f"{value[1]}", va='center')

    ax.set_yticks(range(len(dict1) + len(dict2) + len(dict3)))
    ax.set_yticklabels(list(dict1.keys()) + list(dict2.keys()) + list(dict3.keys()))
    ax.set_xlabel("Time")
    ax.set_ylabel("task")
    ax.set_title("Gantt Chart")
    plt.tight_layout()
    return fig


def ShowRoute(nodelist:"list[Customer]", vehArcList:"list", cptohdArcList: "list"):
    xcoords = []
    ycoords = []
    coordslist = []
    fig = plt.figure(figsize=(15, 15), dpi=300)
    for item in nodelist:
        coords = item.getCoords()
        coordslist.append(coords)
        xcoords.append(coords[0])
        ycoords.append(coords[1])

    plt.scatter(xcoords, ycoords, marker = 'o', color = 'r')
    for idx, (xx, yy) in enumerate(coordslist):
        plt.text(xx + 1, yy + 1, str(idx), fontsize=10, color="black")

    for item in vehArcList:
        x1, y1 = nodelist[item[0]].getCoords()
        x2, y2 = nodelist[item[1]].getCoords()
        plt.plot([x1, x2], [y1, y2], 'b-')
        plt.annotate("", xy = (x2, y2), xytext = (x1, y1),
                     arrowprops = dict(arrowstyle = '->', color = 'b', lw = 2))
    for item in cptohdArcList:
        x1, y1 = nodelist[item[0]].getCoords()
        x2, y2 = nodelist[item[1]].getCoords()
        plt.plot([x1, x2], [y1, y2], 'g-')
        plt.annotate("", xy=(x2, y2), xytext=(x1, y1),
                     arrowprops=dict(arrowstyle='->', color='g', lw = 2))
    # plt.show()
    plt.savefig(f"image/opt.png")



if __name__ == "__main__":
    vehArcList = [(0, 8), (3, 10), (7, 3), (8, 7), (10, 0)]
    route = Route(vehArcList)
    print(route)

