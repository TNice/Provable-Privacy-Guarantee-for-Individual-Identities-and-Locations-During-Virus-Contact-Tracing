import random as r
import pickle
import time

Q = 109077913558799
infectionDistance = 0.00005

class Person:
    def __init__(self, _id):
        self.points = []

class Region():
    def __init__(self, _id):
        self.children = []
        self.id = _id

class Cell():
    def __init__(self, _id):
        self.points = []
        self.id = _id

class Controll():
    def __init__(self):
        self.people = {}
        self.regions = []
        
    def InsertPoint(self, point: list):
        if point[0] not in self.people:
            self.people[point[0]] = []

        #If No Regions In Data Then Create New Region And Children
        region_0 = None
        region_1 = None
        grid = None

        if len(self.regions) == 0:
            region_0 = Region(point[1])
            self.regions.append(region_0)
            region_1 = Region(point[2])
            region_0.children.append(region_1)
            grid = Cell(point[3])
            region_1.children.append(grid)
            grid.points.append([point[0], point[4], point[5], point[6], point[7]])
            self.people[point[0]].append(grid)
            return

        #Check All Base Level Regions
        for r in self.regions:
            if r.id == point[1]:
                region_0 = r
        
        #If No Regions Is Found In The Data Then Create New Region And Children
        if region_0 == None:
            region_0 = Region(point[1])
            self.regions.append(region_0)
            region_1 = Region(point[2])
            region_0.children.append(region_1)
            grid = Cell(point[3])
            region_1.children.append(grid)
            grid.points.append([point[0], point[4], point[5], point[6], point[7]])
            self.people[point[0]].append(grid)
            return
        
        #Checks 2nd Level Of Regions
        for r in region_0.children:
            if point[2] == r.id:
                region_1 = r
        
        #If No Region Found In Children Create Children To Point
        if region_1 == None:
            region_1 = Region(point[2])
            region_0.children.append(region_1)
            grid = Cell(point[3])
            region_1.children.append(grid)
            grid.points.append([point[0], point[4], point[5], point[6], point[7]])
            self.people[point[0]].append(grid)
            return

        #Checks Grid Cells
        for c in region_1.children:
            if point[3] == c.id:
                grid = c
                break
        
        #If No Cell Found In Data Create Cell and Insert Point
        if grid == None:
            grid = Cell(point[3])
            region_1.children.append(grid)
            grid.points.append([point[0], point[4], point[5], point[6], point[7]])
            self.people[point[0]].append(grid)
            return
        else:
            grid.points.append([point[0], point[4], point[5], point[6], point[7]])

            if grid not in self.people[point[0]]:
                self.people[point[0]].append(grid)

    def Querry(self, uId: int):
        global Q
        global infectionDistance

        infectedUsers = []
        for cell in self.people[uId]:
            if len(cell.points) <= 1:
                continue
            
            infected = []
            other = []
            for j, point in enumerate(cell.points):
                if point[0] == uId:
                    infected.append(point)
                else:
                    other.append(point)

            if len(other) == 0:
                continue
            
            for iPoint in infected:
                for oPoint in other:
                    if iPoint[1] > oPoint[2] or oPoint[1] > iPoint[2]:
                        continue

                    distance = (iPoint[1] - oPoint[1])**2 + (iPoint[2] - iPoint[2])**2

                    if distance <= infectionDistance:
                        infectedUsers.append(oPoint[0])
            
            return infectedUsers


controller = Controll()

print('Loading...')
with open(f'DATA_TRAJECTORIES_1M_14_10_RAW_PART0_Unsecure_Res10.p', 'rb') as f:
        people = pickle.load(f)
# with open(f'DATA_TRAJECTORIES_TESTING.p', 'rb') as f:
#     people = pickle.load(f)
print("Done")

def Test(test_name, fileNames):
    buffer = []
    timingSplits = (10**2, 10**3, 10**4, 2 * 10**4, 5 * 10**4 ,10**5)
    avgTimes = {}
    count = 0
    for file_num in range(len(fileNames)):
        print('Loading...')
        with open(fileNames[file_num], 'rb') as f:
            people = pickle.load(f)
        print("Done")
    for i, p in enumerate(people):
        if i % 100 == 0:
            print(f"Inserting 100 People\t {i} / {len(people)}")

        for j, pt in enumerate(p.points):
            count += 1
            buffer.append(pt)
        
        if (i + 1) % 100 == 0 and i != 0:
            startingTime = time.perf_counter()

            for k, data in enumerate(buffer):
                controller.InsertPoint(data)

            elapsedTime = (time.perf_counter() - startingTime) 
            if i + 1 in timingSplits:
                avgTimes[i+1] = elapsedTime / 100

            print(f"\nElapsedTime = {elapsedTime}\t Number of Points = {count}\n")
            count = 0
            buffer = []

    print("Done")
    print("Starting Querry")
    startingTime = time.perf_counter()
    for _ in range(100):
        controller.Querry(r.randint(0,100000))
    elapsedTime = (time.perf_counter() - startingTime)

    print(f"\nElapsedTime = {elapsedTime / 100}")
    print("Finished")

    with open('QuerryAverageTimes.txt', 'w') as f:
        f.write(str(elapsedTime / 100))

    with open('InsertionAverageTimes.p', 'wb') as f:
        pickle.dump(avgTimes, f)

    with open('InsertionAverageTimes.txt', 'w') as f:
        for k,v in avgTimes.items():
            f.write(f'{k}, {v}\n')

if __name__ == '__main__':
    Test('Large Grid No Protect', ['data_large_grid_no_protect.p'])