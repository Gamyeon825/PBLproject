import math
import pandas as pd
from model.Classroom import Classroom


class Building:
    def __init__(self, positionDict, name):
        self.positionDict = positionDict
        self.name = name
        self.x = self.positionDict[self.name]['x']
        self.y = self.positionDict[self.name]['y']
        if 'realX' in self.positionDict[self.name].keys():
            self.realX = self.positionDict[self.name]['realX']
            self.realY = self.positionDict[self.name]['realY']
        self.distanceToOther = self.GetDistanceTo()
        self.classrooms = []
        if self.name != 'MAXSIZE':
            self.GetClassroom()

    def GetDistanceTo(self):
        distanceToOther = {}
        for building, buildingInfo in self.positionDict.items():
            if building == 'MAXSIZE':
                continue
            if self.name == building:
                distanceToOther[building] = 0
                continue
            disX = self.x-buildingInfo['x']
            disY = self.y-buildingInfo['y']
            distanceToOther[building] = math.sqrt(
                math.pow(disX, 2)+math.pow(disY, 2))
            if 'realX' in self.positionDict[self.name].keys():
                disX = self.realX - self.x
                disY = self.realY - self.y
                distanceToOther[building] += math.sqrt(
                    math.pow(disX, 2)+math.pow(disY, 2))
            if 'realX' in self.positionDict[building].keys():
                disX = buildingInfo['x'] - buildingInfo['realX']
                disY = buildingInfo['y'] - buildingInfo['realY']
                distanceToOther[building] += math.sqrt(
                    math.pow(disX, 2)+math.pow(disY, 2))
            distanceToOther[building] = round(distanceToOther[building])
        return sorted(
            distanceToOther.items(), key=lambda x: x[1], reverse=False)

    def GetClassroom(self):
        df = pd.read_csv('res/classroomInBuilding.csv')  # 現有資料
        df = df[df['building'] == self.name]
        df = df.reset_index(drop=True)
        classrooms = []
        for index, row in df.iterrows():
            if not isinstance(row['classroom'], str):
                break
            self.classrooms.append(Classroom(self.name, row['classroom']))
