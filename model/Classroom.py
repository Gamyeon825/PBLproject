
class Classroom:
    def __init__(self, buildingName, name):
        self.buildingName = buildingName
        self.name = name
        self.isUse = {}
        self.usingCourse = {}
        self.initUseStatus()

    def initUseStatus(self):
        weekday = ['日', '一', '二', '三', '四', '五', '六']
        time = ['1', '2', '3', '4', 'N', '5', '6',
                '7', '8', '9', 'A', 'B', 'C', 'D']
        for day in weekday:
            tempDict1 = {}
            tempDict2 = {}
            for t in time:
                tempDict1[t] = False
                tempDict2[t] = ''
            self.isUse[day] = tempDict1
            self.usingCourse[day] = tempDict2
