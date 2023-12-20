import requests
import pandas as pd
from bs4 import BeautifulSoup
import controller.initFunction as initFunction
# Find period in week for courses


def FindPeriodOfCourse(df):
    periodList = []
    for _, row in df.iterrows():
        courseCode = row['CourseCode']
        courseID = row['CourseID']
        academicYear = row['AcademicYear']
        semester = row['Semester']
        r = requests.post('https://aps.ntut.edu.tw/course/tw/QueryCourse.jsp', data={'stime': '0',
                                                                                     'year': academicYear,
                                                                                     'matric': "'0','1','4','5','6','7','8','9','A','C','D','E','F'",
                                                                                     'sem': semester,
                                                                                     'unit': '＊',
                                                                                     'cname': '',
                                                                                     'ccode': courseCode,
                                                                                     'tname': '',
                                                                                     'D0': 'ON',
                                                                                     'D1': 'ON',
                                                                                     'D2': 'ON',
                                                                                     'D3': 'ON',
                                                                                     'D4': 'ON',
                                                                                     'D5': 'ON',
                                                                                     'D6': 'ON',
                                                                                     'P1': 'ON',
                                                                                     'P2': 'ON',
                                                                                     'P3': 'ON',
                                                                                     'P4': 'ON',
                                                                                     'PN': 'ON',
                                                                                     'P5': 'ON',
                                                                                     'P6': 'ON',
                                                                                     'P7': 'ON',
                                                                                     'P8': 'ON',
                                                                                     'P9': 'ON',
                                                                                     'P10': 'ON',
                                                                                     'P11': 'ON',
                                                                                     'P12': 'ON',
                                                                                     'P13': 'ON'})
        soup = BeautifulSoup(r.text, 'html5lib')
        header = soup.find('table').find_all('tr')[0]
        row = soup.find('table').find_all('tr')[1:]
        weekday = header.find_all('th')[8:16]
        for element in row:
            if element.find('td').text.strip() == str(courseID):
                target = element.find_all('td')[8:16]
                break
        tempPeriod = ''
        for idx in range(7):
            period = [weekday[idx].text.strip(
            ), target[idx].text.strip().replace(' ', ', ')]
            if period[1] != '':
                tempPeriod += period[0]+'：'+period[1]+'　'
        tempPeriod = tempPeriod[:-1]
        if (tempPeriod == ''):
            periodList.append(None)
        else:
            periodList.append(tempPeriod)
    return periodList


def FindClassroomInBuilding():
    keyToBuildingNameDict = {}
    classroomInBuilding = {}
    for building, buildingInfo in initFunction.InputData().items():
        classroomInBuilding[building] = []
        if 'key' in buildingInfo.keys():
            for key in buildingInfo['key']:
                keyToBuildingNameDict[key] = building
    for academicYear in range(111, 112):
        for semester in range(1, 3):
            url = f'https://aps.ntut.edu.tw/course/tw/Croom.jsp?format=-2&year={academicYear}&sem={semester}'
            r = requests.post(url)
            soup = BeautifulSoup(r.text, 'html5lib')
            for element in soup.find_all('tr')[2:]:
                classroomName = element.find('td').text.strip()
                if classroomName == '':
                    break
                for key in keyToBuildingNameDict:
                    if key in classroomName:
                        buildingName = keyToBuildingNameDict[key]
                        if classroomName not in classroomInBuilding[buildingName]:
                            classroomInBuilding[buildingName].append(
                                classroomName)
                        continue
    for key in classroomInBuilding.keys():
        classroomInBuilding[key] = sorted(classroomInBuilding[key])
    df = pd.DataFrame(classroomInBuilding.items(), columns=[
                      'building', 'classroom'])

    df = df.explode('classroom')[:-1]
    df.reset_index(drop=True, inplace=True)
    return df
