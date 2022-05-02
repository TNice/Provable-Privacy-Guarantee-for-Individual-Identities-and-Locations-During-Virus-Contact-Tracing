import random as r
import pickle
import time
from tqdm import tqdm

Q = 109077913558799
infectionDistance = 0.00005

class Person:
    def __init__(self, _id):
        self.points = []

def GenerateShares(secret):
    global Q 
    shares  = [ r.randrange(Q) for _ in range(1) ]
    shares += [ (secret - sum(shares)) % Q ]
    shares = [round(x, 1) for x in shares]
    return shares

class Region():
    def __init__(self, _id):
        self.children = []
        self.id = _id

class Cell():
    def __init__(self, _id):
        self.points = []
        self.id = _id

class Controll():
    class S1():
        def __init__(self):
            self.regions = []

    class S2():
        def __init__(self):
            self.regions = []

    def __init__(self):
        self.people = {}
        self.s1 = self.S1()
        self.s2 = self.S2()
        self.uvw = self.GenerateUVW()
        self.grids1 = {}
        self.grids2 = {}

    def GenerateUVW(self):
        global Q
        u = r.randint(0, Q)
        v = r.randint(0, Q)
        w = u*v

        return [GenerateShares(u), GenerateShares(v), GenerateShares(w)]

    def InsertPoint(self, point1: list, point2: list):
        if point1[0] not in self.people:
            self.people[point1[0]] = []

        #If No Regions In Data Then Create New Region And Children
        region1_0 = None
        region1_1 = None
        grid1 = None
        region2_0 = None
        region2_1 = None
        grid2 = None

        newPt1 = [point1[0], point1[4], point1[5], point1[6], point1[7]]
        newPt2 = [point2[0], point2[4], point2[5], point2[6], point2[7]]

        #if no regions exist create a new region
        if len(self.s1.regions) == 0:
            region1_0 = Region(point1[1])
            self.s1.regions.append(region1_0)
            region1_1 = Region(point1[2])
            region1_0.children.append(region1_1)
            grid1 = Cell(point1[3])
            region1_1.children.append(grid1)
            grid1.points = [newPt1]
            
            region2_0 = Region(point2[1])
            self.s2.regions.append(region2_0)
            region2_1 = Region(point2[2])
            region2_0.children.append(region2_1)
            grid2 = Cell(point2[3])
            region2_1.children.append(grid2)
            grid2.points = [newPt2]
            
            self.people[point1[0]].append((grid1, grid2))
            return

        #Check All Base Level Regions
        for i, r in enumerate(self.s1.regions):
            if self.Compare([r.id, self.s2.regions[i].id], [point1[1], point2[1]]) == 0:
                region1_0 = r
                region2_0 = self.s2.regions[i]
                break
        
        #If No Regions Is Found In The Data Then Create New Region And Children
        if region1_0 == None:
            region1_0 = Region(point1[1])
            self.s1.regions.append(region1_0)
            region1_1 = Region(point1[2])
            region1_0.children.append(region1_1)
            grid1 = Cell(point1[3])
            region1_1.children.append(grid1)
            grid1.points = [newPt1]
            
            region2_0 = Region(point2[1])
            self.s2.regions.append(region2_0)
            region2_1 = Region(point2[2])
            region2_0.children.append(region2_1)
            grid2 = Cell(point2[3])
            region2_1.children.append(grid2)
            grid2.points = [newPt2]
            
            self.people[point1[0]].append((grid1, grid2))
            return
        
        #Checks 2nd Level Of Regions
        for i, r in enumerate(region1_0.children):
            if self.Compare([r.id, region2_0.children[i].id], [point1[2], point2[2]]) == 0:
                region1_1 = r
                region2_1 = region2_0.children[i]
                break
        
        #If No Region Found In Children Create Children To Point
        if region1_1 == None:
            region1_1 = Region(point1[2])
            region1_0.children.append(region1_1)
            grid1 = Cell(point1[3])
            region1_1.children.append(grid1)
            grid1.points = [newPt1]
            
            region2_1 = Region(point2[2])
            region2_0.children.append(region2_1)
            grid2 = Cell(point2[3])
            region2_1.children.append(grid2)
            grid2.points = [newPt2]
            
            self.people[point1[0]].append((grid1, grid2))
            return

        #Checks Grid Cells
        for i, c in enumerate(region1_1.children):
            if self.Compare([c.id, region2_1.children[i].id], [point1[3], point2[3]]) == 0:
                grid1 = c
                grid2 = region2_1.children[i]
                break
        
        #If No Cell Found In Data Create Cell and Insert Point
        if grid1 == None:
            grid1 = Cell(point1[3])
            region1_1.children.append(grid1)
            grid1.points = [newPt1]
            
            grid2 = Cell(point2[3])
            region2_1.children.append(grid2)
            grid2.points = [newPt2]
            
            self.people[point1[0]].append((grid1, grid2))
        else:
            grid1.points.append(newPt1)
            grid2.points.append(newPt2)

            if grid1 not in self.people[point1[0]]:
                self.people[point1[0]].append((grid1, grid2))
    
    def Compare(self, a: list, b: list):
        global Q

        alphas = [a[0] - b[0], a[1] - b[1]] #subtract a - b
        betas = [r.randint(0, Q-1), r.randint(0, Q-1)] #random number to multiply
        chi = alphas[0] + self.uvw[0][0] + alphas[1] + self.uvw[0][1]
        gamma = betas[0] + self.uvw[1][0] + betas[1] + self.uvw[1][1]

        product1 = (chi * gamma) - (chi * self.uvw[1][0]) - (gamma * self.uvw[0][0])  + self.uvw[2][0]
        product2 = -(chi * self.uvw[1][1]) - (gamma * self.uvw[0][1]) + self.uvw[2][1]
        
        return ((product1 + product2) % Q) #return 0 if true or some value if false

    def Querry(self, uId: int):
        global Q
        global infectionDistance

        infectedUsers = []
        for cell1, cell2 in self.people[uId]:      
            #if cell contains has only 1 entry there is no need to querry as only the infected person was in it.
            if len(cell1.points) <= 1:
                continue
            
            infected = []
            other = []
            #seperate points into those that belong to infected person to be querried and other people
            for j, point in enumerate(cell1.points):
                if point[0] == uId:
                    infected.append([point, cell2.points[j]])
                else:
                    other.append([point, cell2.points[j]])

            #if no other person is in the cell then ignore cell and go to next one.
            if len(other) == 0:
                continue
            
            for iPoint in infected:
                for oPoint in other:
                    #If points time ranges do not overlap go to next point
                    if self.Compare([iPoint[0][3], iPoint[1][3]], [oPoint[0][4], oPoint[1][4]]) > 0 or self.Compare([oPoint[0][3], oPoint[1][3]], [iPoint[0][4], iPoint[1][4]]) > 0:
                        continue
                    
                    deltaXs = [iPoint[0][1] - oPoint[0][1], iPoint[1][1] - oPoint[1][1]]
                    deltaYs = [iPoint[0][2] - oPoint[0][2], iPoint[1][2] - oPoint[1][2]]

                    #Secure multiplication
                    alphas = deltaXs
                    betas = deltaXs
                    chi = alphas[0] + self.uvw[0][0] + alphas[1] + self.uvw[0][1]
                    gamma = betas[0] + self.uvw[1][0] + betas[1] + self.uvw[1][1]

                    product1 = (chi * gamma) - (chi * self.uvw[1][0]) - (gamma * self.uvw[0][0])  + self.uvw[2][0]
                    product2 = -(chi * self.uvw[1][1]) - (gamma * self.uvw[0][1]) + self.uvw[2][1]

                    xSquared = [product1, product2]

                    alphas = deltaYs
                    betas = deltaYs
                    chi = alphas[0] + self.uvw[0][0] + alphas[1] + self.uvw[0][1]
                    gamma = betas[0] + self.uvw[1][0] + betas[1] + self.uvw[1][1]

                    product1 = (chi * gamma) - (chi * self.uvw[1][0]) - (gamma * self.uvw[0][0])  + self.uvw[2][0]
                    product2 = -(chi * self.uvw[1][1]) - (gamma * self.uvw[0][1]) + self.uvw[2][1]


                    x = (sum(xSquared)) % Q
                    y = (sum(xSquared)) % Q

                    distance = (x + y) / 10**10 #need to devide awnser by 10^(2 * Decimal Percision) in order to bring awnser to same scale

                
                    if distance <= infectionDistance:
                        infectedUsers.append(oPoint[0][0])
            
            return infectedUsers #return all infected uIds

controller = Controll()

from tqdm import tqdm

def Test(test_name, fileNames):
    buffer = []
    timingSplits = (10**2, 10**3, 10**4, 10**5)
    avgTimes = {}
    querry_times = []
    count = 0
    for file_num in range(len(fileNames)):
        print('Loading...')
        with open(fileNames[file_num], 'rb') as f:
            people = pickle.load(f)
        print("Done")
        for i, p in enumerate(tqdm(people)):
            for j, pt in enumerate(p.points):
                point1 = [pt[0][0], int(pt[0][1][0]), int(pt[0][2][0]), int(pt[0][3][0]), int(pt[0][4][0]), int(pt[0][5][0]), int(pt[0][6][0]), int(pt[0][7][0])]
                point2 = [pt[0][0], int(pt[0][1][1]), int(pt[0][2][1]), int(pt[0][3][1]), int(pt[0][4][1]), int(pt[0][5][1]), int(pt[0][6][1]), int(pt[0][7][1])]
                buffer.append([point1, point2])
            
            if (i + 1) % 100 == 0 and i != 0:
                startingTime = time.perf_counter()

                for k, data in enumerate(buffer):
                    controller.InsertPoint(data[0], data[1])
                elapsedTime = (time.perf_counter() - startingTime) 
                if file_num > 0 and i + 1 == 10**5:
                    avgTimes[(i+1) * (file_num+1)] = elapsedTime / 100
                elif file_num == 0 and i + 1 in timingSplits:
                    avgTimes[(i+1)] = elapsedTime / 100

                count = 0
                buffer = []

        people = None

        print("Done")
        print("Starting Querry")
        startingTime = time.perf_counter()
        for _ in range(100):
            controller.Querry(r.randint(0,100-1))
        elapsedTime = (time.perf_counter() - startingTime)
        querry_times.append(elapsedTime)

        print(f"\nElapsedTime = {elapsedTime / 100}")
        print("Finished")


        with open(f'QuerryAverageTimes_{test_name}.txt', 'w') as f:
            for t in querry_times:
                f.write(f'{t}\n')

        with open(f'InsertionAverageTimes_{test_name}.txt', 'w') as f:
            for k,v in avgTimes.items():
                f.write(f'{k}, {v}\n')
    
    return

if __name__ == '__main__':
    Test('Large Grid', ['data_large_grid.p'])