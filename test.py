from customer import Customer
from model import SptpTwoEchoModels
import random as rd
from utility import Eucdist,Route, Allocation, Sequence, decode0, decode1,  Gantt0, Gantt1

cumlist = [Customer() for _ in range(11)]
hdlist = {2, 4, 6, 8, 10}
cplist = {1, 3, 5, 7, 9}
cumindexlist = hdlist | cplist

strategy = [1, 0]

for stg in strategy:
    rd.seed(34)
    ptime = {idx: rd.randint(31, 50) for idx in cumindexlist}
    for idx, cum in enumerate(cumlist):
        if idx == 0: continue
        if idx in hdlist: cum.setLabel(Customer.CustomerType.HomeDelivery)
        if idx in cplist: cum.setLabel(Customer.CustomerType.SelfPickUp)
        cum.setProductionTime(ptime[idx])

    vehdistdict = {(idx1, idx2): rd.randint(31, 50)
                   for idx1 in {0} | hdlist
                   for idx2 in {0} | hdlist
                   if idx1 != idx2}
    cptohddistdict = {(idx1, idx2): rd.randint(31, 50)
                      for idx1 in cplist
                      for idx2 in hdlist
                      if idx1 != idx2}
    sptpmodel = SptpTwoEchoModels()
    sptpmodel.setSet(set1=hdlist, set2=cplist)
    sptpmodel.setParams(p=ptime, vd=vehdistdict, cd=cptohddistdict, e=max(cptohddistdict.values()),
                        m=sum(ptime.values()) + max(vehdistdict.values()) * len(cplist | {0}) + max(
                            vehdistdict.values()) * len(cplist))
    sptpmodel.setVars()
    sptpmodel.setObj()
    sptpmodel.setModel(strategy=stg)
    sptpmodel.optimize()
    l1, l2, l3 = sptpmodel.getSolution()

    route = Route(l1)
    allo = Allocation(route, l2)
    seq = Sequence(route, l3)
    print(f"Route: {route}\nAllocation: {allo}\nSequence: {seq}")

    if stg == 0:
        decode0(cumlist, route, allo, seq, vehdistdict, cptohddistdict)
        fig = Gantt0(cumlist, l1, l2, route, seq, vehdistdict, cptohddistdict)
        fig.savefig(f"image/Gantt{len(cumlist)}_{len(hdlist)}_{len(cplist)}_{stg}.png")
    if stg == 1:
        decode1(cumlist, route, allo, seq, vehdistdict, cptohddistdict)
        fig = Gantt1(cumlist, l1, l2, route, seq, vehdistdict, cptohddistdict)
        fig.savefig(f"image/Gantt{len(cumlist)}_{len(hdlist)}_{len(cplist)}_{stg}.png")
