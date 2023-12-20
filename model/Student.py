import pandas as pd


class Student:
    def __init__(self, studentID, curriculum):
        self.ID = studentID
        self.curriculum = curriculum
        self.courseContinuously = {}
        self.GetCourseContinuously()

    def GetCourseContinuously(self):
        for key in self.curriculum.keys():
            self.courseContinuously[key] = {}
            self.CheckCourseContinuously(key)

    def CheckCourseContinuously(self, academicYearSemester):
        time = ['1', '2', '3', '4', 'N', '5', '6',
                '7', '8', '9', 'A', 'B', 'C', 'D',]
        curriculum = self.curriculum[academicYearSemester]
        for i in range(len(curriculum)):
            courseA = curriculum[i]
            weekdaysA = str(courseA['Period']).split('　')

            if weekdaysA[0] == 'None':
                continue

            for j in range(i+1, len(curriculum)):
                courseB = curriculum[j]
                weekdaysB = str(courseB['Period']).split('　')

                if str(courseA['CourseID']) == str(courseB['CourseID']) or weekdaysB[0] == 'None':
                    continue

                for timeA in weekdaysA:
                    for timeB in weekdaysB:
                        weekdayA = timeA.split('：')[0]
                        classA = timeA.split('：')[1].split(', ')
                        weekdayB = timeB.split('：')[0]
                        classB = timeB.split('：')[1].split(', ')
                        if weekdayA != weekdayB:
                            continue

                        dif1 = time.index(
                            str(classA[-1]))-time.index(str(classB[0]))
                        dif2 = time.index(
                            str(classB[-1]))-time.index(str(classA[0]))

                        if dif1 == -1:
                            if (str(courseA['CourseID']) + '_' + str(courseB['CourseID'])) in self.courseContinuously[academicYearSemester].keys():
                                self.courseContinuously[academicYearSemester][str(courseA['CourseID']) + '_' +
                                                                              str(courseB['CourseID'])]['Count'] += 1
                                self.courseContinuously[academicYearSemester][str(courseA['CourseID']) + '_' +
                                                                              str(courseB['CourseID'])]['Period'].append([[weekdayA, classA], [weekdayB, classB]])
                            else:
                                self.courseContinuously[academicYearSemester][str(courseA['CourseID']) + '_' +
                                                                              str(courseB['CourseID'])] = {'Count': 1}
                                self.courseContinuously[academicYearSemester][str(courseA['CourseID']) + '_' +
                                                                              str(courseB['CourseID'])]['Period'] = [[[weekdayA, classA], [weekdayB, classB]]]
                            continue
                        elif dif2 == -1:
                            if (str(courseB['CourseID']) + '_' + str(courseA['CourseID'])) in self.courseContinuously[academicYearSemester].keys():
                                self.courseContinuously[academicYearSemester][str(courseB['CourseID']) + '_' +
                                                                              str(courseA['CourseID'])]['Count'] += 1
                                self.courseContinuously[academicYearSemester][str(courseB['CourseID']) + '_' +
                                                                              str(courseA['CourseID'])]['Period'].append([[weekdayB, classB], [weekdayA, classA]])
                            else:
                                self.courseContinuously[academicYearSemester][str(courseB['CourseID']) + '_' +
                                                                              str(courseA['CourseID'])] = {'Count': 1}
                                self.courseContinuously[academicYearSemester][str(courseB['CourseID']) + '_' +
                                                                              str(courseA['CourseID'])]['Period'] = [[[weekdayB, classB], [weekdayA, classA]]]
                            continue
                        else:
                            continue
