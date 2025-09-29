from customer import Customer
import gurobipy as gp
from math import inf
import random as rd
from utility import Eucdist,Route, Allocation, Sequence, decode0, decode1,  Gantt0, Gantt1
class SptpTwoEchoModels:
    # data members
    def __init__(self):
        self.HomeDeliveryCustomerSet:set[int] = set() # home-delivery customer indeself.x
        self.SelfPickUpCustomerSet:set[int] = set() # self-pickup  customer indeself.x
        
        self.ProductionTime:dict[int, int] = dict() # production time
        self.VehDistDict:dict[tuple[int, int], int] =dict() # the transportation time of pathes which vehicle takes
        self.CpToHdDistDict:dict[tuple[int, int], int] =dict() # the transporation time of pathes which self-pickup customers takes
        
        self.M = inf # big-M
        self.E = inf # the maself.ximum acceptable transportation time for self-pickup customers to pick up their orders
        
        self.Model = gp.Model() # self.Model
    
    def setSet(self, set1, set2):
        self.HomeDeliveryCustomerSet = set1
        self.SelfPickUpCustomerSet = set2
    
    def setParams(self, p, vd, cd, m, e):
        self.ProductionTime = p
        self.VehDistDict = vd
        self.CpToHdDistDict = cd
        self.M = m
        self.E = e
    def setVars(self):
        self.x = self.Model.addVars(((i, j)
                                     for i in {0} | self.HomeDeliveryCustomerSet
                                     for j in {0} | self.HomeDeliveryCustomerSet
                                     if i != j),
                                    vtype=gp.GRB.BINARY, name='x')
        self.z = self.Model.addVars(((k, j)
                                     for k in self.SelfPickUpCustomerSet
                                     for j in self.HomeDeliveryCustomerSet),
                                    vtype=gp.GRB.BINARY, name='z')
        self.y = self.Model.addVars(((h, k, j)
                                     for j in self.HomeDeliveryCustomerSet
                                     for h in {0} | self.SelfPickUpCustomerSet | {j}
                                     for k in {0} | self.SelfPickUpCustomerSet | {j}
                                     if h != k),
                                    vtype=gp.GRB.BINARY, name='y')
        self.alpha = self.Model.addVars(self.HomeDeliveryCustomerSet | self.SelfPickUpCustomerSet,
                                        lb=0, ub=sum(self.ProductionTime.values()), vtype=gp.GRB.INTEGER,
                                        name='completion time')
        self.beta = self.Model.addVars(self.HomeDeliveryCustomerSet | self.SelfPickUpCustomerSet,
                                       lb=0, vtype=gp.GRB.INTEGER, name='delivery time')
        self.a = self.Model.addVars(self.HomeDeliveryCustomerSet, lb=0, vtype=gp.GRB.INTEGER, name='arrival time')
        self.d = self.Model.addVars(self.HomeDeliveryCustomerSet, lb=0, vtype=gp.GRB.INTEGER, name='departure time')
        self.A = self.Model.addVars(self.HomeDeliveryCustomerSet,
                                    lb=0, ub=sum(self.ProductionTime.values()), vtype=gp.GRB.INTEGER,
                                    name='batch completion time')
        self.T = self.Model.addVar(vtype=gp.GRB.INTEGER, lb=0, name='the total trip time')
    def setObj(self):
        self.Model.setObjective(self.T, gp.GRB.MINIMIZE)  # set objective function
    def setModel(self, strategy = 0):
        # constrs1 和 constrs2保证车辆路径结点的出入度为1
        self.constrs1 = self.Model.addConstrs(gp.quicksum(self.x[i,j] for i in {0} | self.HomeDeliveryCustomerSet if i != j) == 1
                                    for j in {0} | self.HomeDeliveryCustomerSet)
        self.constrs2 = self.Model.addConstrs(gp.quicksum(self.x[j,i] for i in {0} | self.HomeDeliveryCustomerSet if i != j) == 1
                                    for j in {0} | self.HomeDeliveryCustomerSet)
        # constrs3 和 constrs4保证满足自提客户的分配要求
        self.constrs3 = self.Model.addConstrs(gp.quicksum(self.z[k,j] for j in self.HomeDeliveryCustomerSet) == 1
                                    for k in self.SelfPickUpCustomerSet)
        self.constrs4 = self.Model.addConstrs(gp.quicksum(self.z[k,j] * self.CpToHdDistDict[(k,j)] for j in self.HomeDeliveryCustomerSet) <= self.E
                                    for k in self.SelfPickUpCustomerSet)
        # constrs5 和 constrs6保证当HD customer没有被分配自提客户时，其Batch {j}有且只有一个job {j}
        self.constrs5 = self.Model.addConstrs(1-self.y[0,j,j]<=gp.quicksum(self.z[k,j] for k in self.SelfPickUpCustomerSet)
                                    for j in self.HomeDeliveryCustomerSet)
        self.constrs6 = self.Model.addConstrs(1-self.y[j,0,j]<=gp.quicksum(self.z[k,j] for k in self.SelfPickUpCustomerSet)
                                    for j in self.HomeDeliveryCustomerSet)
        # constrs7 和 constrs8 保证自提客户被分配到HD customer {j}时，其在Batch {j}上必有一道前序任务和一道后续任务
        self.constrs7 = self.Model.addConstrs(gp.quicksum(self.y[h,k,j] for h in {0} | self.SelfPickUpCustomerSet | {j} if h != k) == self.z[k,j]
                                    for j in self.HomeDeliveryCustomerSet
                                    for k in self.SelfPickUpCustomerSet)
        self.constrs8 = self.Model.addConstrs(gp.quicksum(self.y[h,k,j] for k in {0} | self.SelfPickUpCustomerSet | {j} if h != k) == self.z[h,j]
                                    for j in self.HomeDeliveryCustomerSet
                                    for h in self.SelfPickUpCustomerSet)
        # constrs9 和 constrs10保证订单j必有一道前序工序和一道后续工序
        self.constrs9 = self.Model.addConstrs(gp.quicksum(self.y[k,j,j] for k in {0} | self.SelfPickUpCustomerSet) == 1
                                    for j in self.HomeDeliveryCustomerSet)
        self.constrs10 = self.Model.addConstrs(gp.quicksum(self.y[j,k,j] for k in {0} | self.SelfPickUpCustomerSet) == 1
                                    for j in self.HomeDeliveryCustomerSet)
        # constrs11 和 constrs12保证batch{j}必有一个开始任务和一个结束任务
        self.constrs11 = self.Model.addConstrs(gp.quicksum(self.y[0,k,j] for k in self.SelfPickUpCustomerSet | {j}) == 1
                                    for j in self.HomeDeliveryCustomerSet)
        self.constrs12 = self.Model.addConstrs(gp.quicksum(self.y[h,0,j] for h in self.SelfPickUpCustomerSet | {j}) == 1
                                    for j in self.HomeDeliveryCustomerSet)
        # Completion Time Constraints
        self.constrs13 = self.Model.addConstrs(self.A[i] + self.ProductionTime[j] + gp.quicksum(self.z[k,j]*self.ProductionTime[k] for k in self.SelfPickUpCustomerSet) + self.M*(self.x[i,j]-1) <= self.A[j]
                                    for j in self.HomeDeliveryCustomerSet
                                    for i in self.HomeDeliveryCustomerSet
                                    if i!=j)

        self.constrs14 = self.Model.addConstrs(self.ProductionTime[j] + gp.quicksum(self.z[k,j]*self.ProductionTime[k] for k in self.SelfPickUpCustomerSet) <= self.A[j]
                                    for j in self.HomeDeliveryCustomerSet)

        self.constrs15 = self.Model.addConstrs(self.ProductionTime[j] <= self.alpha[j] for j in self.HomeDeliveryCustomerSet)

        self.constrs16 = self.Model.addConstrs(self.A[i] + self.ProductionTime[j] + self.M * (self.y[0,j,j]+self.x[i,j]-2)<=self.alpha[j]
                                    for j in self.HomeDeliveryCustomerSet
                                    for i in self.HomeDeliveryCustomerSet
                                    if i!=j)
        self.constrs17 = self.Model.addConstrs(self.A[i] + self.ProductionTime[k] + self.M * (self.y[0,k,j]+self.z[k,j]+self.x[i,j]-3)<=self.alpha[k]
                                    for k in self.SelfPickUpCustomerSet
                                    for j in self.HomeDeliveryCustomerSet
                                    for i in self.HomeDeliveryCustomerSet
                                    if i != j)
        self.constrs18 = self.Model.addConstrs(self.alpha[j] + self.ProductionTime[k] + self.M * (self.y[j,k,j] + self.z[k,j] - 2) <= self.alpha[k]
                                    for k in self.SelfPickUpCustomerSet
                                    for j in self.HomeDeliveryCustomerSet)
        self.constrs19 = self.Model.addConstrs(self.alpha[k] + self.ProductionTime[j] + self.M * (self.y[k,j,j] + self.z[k,j] -2) <= self.alpha[j]
                                    for j in self.HomeDeliveryCustomerSet
                                    for k in self.SelfPickUpCustomerSet)
        self.constrs20 = self.Model.addConstrs(self.alpha[h] + self.ProductionTime[k] + self.M * (self.y[h,k,j] + self.z[h,j] + self.z[k,j] - 3) <= self.alpha[k]
                                    for j in self.HomeDeliveryCustomerSet
                                    for h in self.SelfPickUpCustomerSet
                                    for k in self.SelfPickUpCustomerSet
                                    if h != k)

        # Delivery Time Constraints
        if strategy == 0:
            self.constrs21 = self.Model.addConstrs(self.alpha[j] <= self.beta[j] for j in self.HomeDeliveryCustomerSet)
            self.constrs22 = self.Model.addConstrs(self.a[j] <= self.beta[j] for j in self.HomeDeliveryCustomerSet)
            self.constrs23 = self.Model.addConstrs(self.a[j] + self.M * (self.z[k,j]- 1) <= self.beta[k]
                                        for j in self.HomeDeliveryCustomerSet
                                        for k in self.SelfPickUpCustomerSet)
            self.constrs24 = self.Model.addConstrs(self.alpha[k] + self.CpToHdDistDict[(k,j)] + self.M * (self.z[k,j] -1) <= self.beta[k]
                                        for k in self.SelfPickUpCustomerSet
                                        for j in self.HomeDeliveryCustomerSet)
        else:
            self.constrs21 = self.Model.addConstrs(self.alpha[j] <= self.beta[j] for j in self.HomeDeliveryCustomerSet | self.SelfPickUpCustomerSet)
            self.constrs22 = self.Model.addConstrs(self.a[j] <= self.beta[j] for j in self.HomeDeliveryCustomerSet)
            self.constrs23 = self.Model.addConstrs(self.a[j] + self.CpToHdDistDict[k, j] + self.M *(self.z[k, j] - 1) <= self.beta[k]
                                                   for j in self.HomeDeliveryCustomerSet
                                                   for k in self.SelfPickUpCustomerSet)
        # arrival time constraints
        self.constrs25 = self.Model.addConstrs(self.VehDistDict[(0,j)] * self.x[0,j] <= self.a[j] for j in self.HomeDeliveryCustomerSet)
        self.constrs26 = self.Model.addConstrs(self.d[i] + self.VehDistDict[(i,j)] + self.M*(self.x[i,j] -1) <= self.a[j]
                                    for j in self.HomeDeliveryCustomerSet
                                    for i in self.HomeDeliveryCustomerSet
                                    if i != j)
        # departure time constraints
        self.constrs27 = self.Model.addConstrs(self.beta[j] <= self.d[j] for j in self.HomeDeliveryCustomerSet)
        self.constrs28 = self.Model.addConstrs(self.beta[k] + self.M * (self.z[k,j] - 1) <= self.d[j]
                                    for j in self.HomeDeliveryCustomerSet
                                    for k in self.SelfPickUpCustomerSet)
        # the total trip time constraints
        self.constrs29 = self.Model.addConstrs(self.d[j] + self.VehDistDict[(j,0)]*self.x[j,0] <= self.T for j in self.HomeDeliveryCustomerSet)
    
    def optimize(self):
        self.Model.setParam("TimeLimit", 3600)
        self.Model.optimize()
        
    def getSolution(self):
        xOne = {k: v.X for k, v in self.x.items() if v.X > 0.5}
        zOne = {k: v.X for k, v in self.z.items() if v.X > 0.5}
        yOne = {k: v.X for k, v in self.y.items() if v.X > 0.5}
        veharclist = [key for key in xOne.keys()]
        cptohdarclist = [key for key in zOne.keys()]
        sequencelist = [key for key in yOne.keys()]
        return veharclist, cptohdarclist,sequencelist

    def getRuntime(self):
        return self.Model.Runtime
    def getNodeCount(self):
        return self.Model.NodeCount
    
if __name__ == "__main__":
    cumlist = [Customer() for _ in range(11)]
    hdlist = {2, 4, 6, 8, 10}
    cplist = {1, 3, 5, 7, 9}
    cumindexlist = hdlist | cplist
    strategy = [0, 1]
    seed = {1, 2, 3, 4, 5}
    optdict = {}
    metric = {}
    for item1 in strategy:
        for item2 in seed:
            rd.seed(item2)
            ptime = {idx:rd.randint(20, 30) for idx in cumindexlist}
            for idx, cum in enumerate(cumlist):
                if idx == 0 : continue
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
            sptpmodel.setSet(set1 = hdlist, set2=cplist)
            sptpmodel.setParams(p=ptime, vd=vehdistdict, cd=cptohddistdict,e=max(cptohddistdict.values()),
                                m=sum(ptime.values()) + max(vehdistdict.values()) * len(cplist | {0}) + max(vehdistdict.values()) * len(cplist))
            sptpmodel.setVars()
            sptpmodel.setObj()
            sptpmodel.setModel(strategy=item1)
            sptpmodel.optimize()
            if sptpmodel.Model.status == gp.GRB.OPTIMAL:
                optdict[item1, item2] = sptpmodel.Model.ObjVal
            metric[item1, item2] = (sptpmodel.Model.Status, sptpmodel.getRuntime(), sptpmodel.getNodeCount())
            l1, l2, l3 = sptpmodel.getSolution()

            route= Route(l1)
            allo = Allocation(route, l2)
            seq = Sequence(route, l3)
            print(f"Route: {route}\nAllocation: {allo}\nSequence: {seq}")
            if item1 == 0:
                decode0(cumlist, route, allo, seq, vehdistdict, cptohddistdict)
                fig = Gantt0(cumlist, l1, l2, route, seq, vehdistdict, cptohddistdict)
                fig.savefig(f"image/Gantt{len(cumlist)}_{len(hdlist)}_{len(cplist)}_{item2}_{item1}.png")
            if item1 == 1:
                decode1(cumlist, route, allo, seq, vehdistdict, cptohddistdict)
                fig = Gantt1(cumlist, l1, l2, route, seq, vehdistdict, cptohddistdict)
                fig.savefig(f"image/Gantt{len(cumlist)}_{len(hdlist)}_{len(cplist)}_{item2}_{item1}.png")

    for key, value in optdict.items():
        print(f"{key}: {value}")
    for key,value in metric.items():
        print(f"{key}: {value}")


    
    