import os
import pandas as pd
import controller.crawler as crawler
import json
from model.Building import Building
from model.Student import Student


def InitCourseCSV():
    # 初始化course.csv
    if not os.path.isfile('res/course.csv'):
        headerList = ['CourseCode', 'AcademicYear',
                      'Semester', 'Period']
        courseDF = pd.DataFrame(columns=headerList)
        courseDF.to_csv('res/course.csv', index=False)
    InsertCourseToCSV()


def InsertCourseToCSV():
    # 從dataset.csv匯入資料到course.csv
    courseDF = pd.read_csv('res/course.csv')  # 現有資料
    df = pd.read_csv('res/dataset.csv')  # 新增資料
    df = df.loc[:, ['CourseCode', 'CourseID',
                    'AcademicYear', 'Semester', 'CourseName']]
    df.drop_duplicates(subset=['CourseID'], inplace=True)  # 刪除新資料內重複row
    # 刪除與現有資料相同課號的row
    df.reset_index(drop=True, inplace=True)
    df = pd.concat([df, courseDF], ignore_index=True)
    df.drop_duplicates(subset=["CourseID"], keep=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['Period'] = crawler.FindPeriodOfCourse(df)
    courseDF = pd.concat([df, courseDF], ignore_index=True)
    courseDF.drop_duplicates(
        subset=['CourseCode', 'CourseID'], keep='last', inplace=True)
    courseDF.sort_values(['CourseID'],
                         ascending=True, inplace=True)
    courseDF.to_csv('res/course.csv', index=False)


def InputData():
    # 匯入座標
    result = {}
    jsonFile = open(
        'res/building.json', 'r', encoding='utf-8')
    f = json.load(jsonFile)
    for i in f:
        result[i] = {'x': f[i]['x'],
                     'y': f[i]['y']}
        if 'key' in f[i].keys():
            result[i]['key'] = f[i]['key']
            if 'realX' in f[i].keys():
                result[i]['realX'] = f[i]['realX']
                result[i]['realY'] = f[i]['realY']
    return result


def SortedBuildingByDistanceToOther():
    # 依照所有建築的彼此距離總和排序建築由小到大
    # 回傳List
    positionDict = InputData()
    tempDistanceList = []
    for building in positionDict.keys():
        tempBuilding = Building(positionDict, building)
        tempDistance = 0
        for element in tempBuilding.distanceToOther:
            tempDistance += element[1]
        tempDistanceList.append([tempBuilding, tempDistance])
    tempDistanceList = sorted(
        tempDistanceList, key=lambda distance: distance[1])
    sortedBuildingList = []
    for element in tempDistanceList:
        sortedBuildingList.append(element[0])
    return sortedBuildingList


def InitClassroomInBuildingCSV():
    # 初始化classroomInBuilding.csv
    if not os.path.isfile('res/classroomInBuilding.csv'):
        headerList = ['BuildingID', 'Classroom']
        df = pd.DataFrame(columns=headerList)
        df.to_csv('res/classroomInBuilding.csv', index=False)
    df = crawler.FindClassroomInBuilding()
    df.to_csv('res/classroomInBuilding.csv', index=False)


def InitCourse():
    # 初始化Course
    # 回傳List
    courseDict = {}
    courseDF = pd.read_csv('res/course.csv')
    for index, row in courseDF.iterrows():
        courseDict[row['CourseID']] = {'CourseCode': row['CourseCode'],
                                       'CourseID': row['CourseID'],
                                       'AcademicYear': row['AcademicYear'],
                                       'Semester': row['Semester'],
                                       'CourseName': row['CourseName'],
                                       }
        if not isinstance(row['Period'], str):
            courseDict[row['CourseID']]['Period'] = None
            continue
        courseDict[row['CourseID']]['Period'] = row['Period']
    return courseDict


def InitStudent(courseDict):
    df = pd.read_csv('res/dataset.csv')
    df = df.loc[:, ['StudentID', 'CourseID']]
    studentDF = df.loc[:, ['StudentID']]
    studentDF.drop_duplicates(keep='last', inplace=True)
    studentDF.reset_index(drop=True, inplace=True)
    studentIDList = studentDF.values.tolist()
    studentList = []
    for studentID in studentIDList:
        studentID = studentID[0]
        curriculumDF = pd.DataFrame(df[df['StudentID'] == studentID])
        curriculumDF.drop_duplicates(subset=['CourseID'], inplace=True)
        curriculumDF.sort_values(['CourseID'],
                                 ascending=True, inplace=True)
        curriculumDF.reset_index(drop=True, inplace=True)
        curriculum = curriculumDF['CourseID'].tolist()
        tempCurriculumDict = {}
        for courseID in curriculum:
            course = courseDict[courseID]
            academicYearSemester = str(course['AcademicYear']) + \
                '_'+str(course['Semester'])
            tempCurriculumDict[academicYearSemester] = []
        for courseID in curriculum:
            course = courseDict[courseID]
            academicYearSemester = str(course['AcademicYear']) + \
                '_'+str(course['Semester'])
            tempCurriculumDict[academicYearSemester].append(course)
        tempStudent = Student(studentID, tempCurriculumDict)
        studentList.append(tempStudent)

    return studentList


def InitDataset():
    if not os.path.isfile('res/dataset.csv'):
        df = pd.read_csv('res/第二組數據資料集_1211.csv', dtype={'學號_id': int})
        df = df.loc[:, ['學號_id', '修課學年', '修課學期', '課程編碼', '課號', '課程名稱']]
        df.columns = ['StudentID', 'AcademicYear',
                      'Semester', 'CourseCode', 'CourseID', 'CourseName']
        df.drop_duplicates(
            subset=['StudentID', 'CourseID'], keep='last', inplace=True)
        df.sort_values(['StudentID'],
                       ascending=True, inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.to_csv('res/dataset.csv', index=False)


def PreAssigned(buildingList, courseDict):
    # 匯入座標
    result = {}
    jsonFile = open(
        'res/building.json', 'r', encoding='utf-8')
    f = json.load(jsonFile)
    for i in f:
        result[i] = {'x': f[i]['x'],
                     'y': f[i]['y']}
        if 'key' in f[i].keys():
            result[i]['key'] = f[i]['key']
            if 'realX' in f[i].keys():
                result[i]['realX'] = f[i]['realX']
                result[i]['realY'] = f[i]['realY']
    return buildingList, courseDict
