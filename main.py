import controller.initFunction as initFunction
import pandas as pd
from flask import Flask, render_template, request, session, jsonify
import json

app = Flask(__name__)
app.jinja_env.variable_start_string = '[['
app.jinja_env.variable_end_string = ']]'
app.config['SECRET_KEY'] = b'\x17(\xe7`p\x178\xfcv\x9f\xcf\x86\t\xdfl{'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['SESSION_TYPE'] = 'filesystem'


def init():
    initFunction.InitDataset()
    initFunction.InitCourseCSV()
    initFunction.InitClassroomInBuildingCSV()

    buildingList = initFunction.SortedBuildingByDistanceToOther()
    courseDict = initFunction.InitCourse()
    studentList = initFunction.InitStudent(courseDict)

    return [buildingList, courseDict, studentList]


def IntegrateCourseContinuously(studentList):
    tempDict = {}
    for student in studentList:
        for academicYearSemester in student.courseContinuously.keys():
            if academicYearSemester not in tempDict.keys():
                tempDict[academicYearSemester] = {}
        for academicYearSemester, values in student.courseContinuously.items():
            for key, value in values.items():
                if key in tempDict[academicYearSemester].keys():
                    tempDict[academicYearSemester][key]['Count'] += value['Count']
                else:
                    tempDict[academicYearSemester][key] = {
                        'Count': value['Count'], 'Period': value['Period']}
    courseContinuouslyDict = {}
    for academicYearSemester, values in tempDict.items():
        courseContinuouslyDict[academicYearSemester] = []
        for key, value in values.items():
            courseContinuouslyDict[academicYearSemester].append(
                [key, value['Period'], value['Count']])
    for academicYearSemester in courseContinuouslyDict.keys():
        courseContinuouslyDict[academicYearSemester] = sorted(
            courseContinuouslyDict[academicYearSemester], key=lambda x: x[2], reverse=True)
    sortedCourseContinuouslyDict = {}
    for academicYearSemester in courseContinuouslyDict.keys():
        sortedCourseContinuouslyDict[academicYearSemester] = []
        for element in courseContinuouslyDict[academicYearSemester]:
            sortedCourseContinuouslyDict[academicYearSemester].append(
                element[:2])
    return sortedCourseContinuouslyDict


def CheckClassroom(classroom, course):
    times = course['Period'].split('　')
    for time in times:
        weekday = time.split('：')[0]
        nodes = time.split('：')[1].split(', ')
        for node in nodes:
            if classroom.isUse[weekday][node]:
                return False
    return True


def EnableClassroom(classroom, course):
    times = course['Period'].split('　')
    for time in times:
        weekday = time.split('：')[0]
        nodes = time.split('：')[1].split(', ')
        for node in nodes:
            classroom.isUse[weekday][node] = True
            classroom.usingCourse[weekday][node] = course['CourseID']


def AssignClassroom(courseContinuouslyDict, courseDict, buildingList):
    buildingList, courseDict = initFunction.PreAssigned(
        buildingList, courseDict)
    for _, courseContinuously in courseContinuouslyDict.items():
        for element in courseContinuously:
            isFindA = False
            isFindB = False
            courseA = element[0].split('_')[0]
            courseB = element[0].split('_')[1]
            if 'Classroom' not in courseDict[int(courseA)].keys():
                for building in buildingList:
                    for classroom in building.classrooms:
                        if 'Classroom' in courseDict[int(courseB)].keys():
                            if CheckClassroom(courseDict[int(courseB)]['Classroom'],
                                              courseDict[int(courseA)]):
                                courseDict[int(courseA)]['Classroom'] = courseDict[int(
                                    courseB)]['Classroom']
                                EnableClassroom(courseDict[int(courseA)]['Classroom'],
                                                courseDict[int(courseA)])
                                isFindA = True
                                break
                        if CheckClassroom(classroom, courseDict[int(courseA)]):
                            courseDict[int(courseA)]['Classroom'] = classroom
                            EnableClassroom(courseDict[int(courseA)]['Classroom'],
                                            courseDict[int(courseA)])
                            isFindA = True
                        if isFindA:
                            break
                    if isFindA:
                        break
            if 'Classroom' not in courseDict[int(courseB)].keys():
                for building in buildingList:
                    for classroom in building.classrooms:
                        if CheckClassroom(courseDict[int(courseA)]['Classroom'],
                                          courseDict[int(courseB)]):
                            courseDict[int(courseB)]['Classroom'] = courseDict[int(
                                courseA)]['Classroom']
                            EnableClassroom(courseDict[int(courseB)]['Classroom'],
                                            courseDict[int(courseB)])
                            isFindB = True
                        elif CheckClassroom(classroom, courseDict[int(courseB)]):
                            courseDict[int(courseB)
                                       ]['Classroom'] = classroom
                            EnableClassroom(courseDict[int(courseB)]['Classroom'],
                                            courseDict[int(courseB)])
                            isFindB = True
                        if isFindB:
                            break
                    if isFindB:
                        break

    for course in courseDict.values():
        isFind = False
        if 'Classroom' in course.keys():
            continue
        elif course['Period'] == None:
            course['Classroom'] = None
            continue
        for building in buildingList:
            for classroom in building.classrooms:
                if CheckClassroom(classroom, course):
                    course['Classroom'] = classroom
                    EnableClassroom(classroom, course)
                    isFind = True
                if isFind:
                    break
            if isFindB:
                break
    return courseDict, buildingList


def OutputResult(courseDict):
    csvDict = {
        'CourseCode': [], 'CourseID': [], 'AcademicYear': [],
        'Semester': [], 'CourseName': [], 'Period': [], 'Building': [], 'Classroom': []
    }
    jsonDict = {}
    for course in courseDict.items():
        courseCode = course[1]['CourseCode']
        courseID = course[0]
        academicYear = course[1]['AcademicYear']
        semester = course[1]['Semester']
        courseName = course[1]['CourseName']
        period = course[1]['Period']
        building = None if course[1]['Classroom'] == None else course[1]['Classroom'].buildingName
        classroom = None if course[1]['Classroom'] == None else course[1]['Classroom'].name
        # ToCSV
        csvDict['CourseCode'].append(courseCode)
        csvDict['CourseID'].append(courseID)
        csvDict['AcademicYear'].append(academicYear)
        csvDict['Semester'].append(semester)
        csvDict['CourseName'].append(courseName)
        csvDict['Period'].append(period)
        csvDict['Building'].append(building)
        csvDict['Classroom'].append(classroom)
        if classroom == None:
            continue
        # ToJSON
        jsonDict[courseID] = {'CourseCode': courseCode,
                              'CourseID': courseID,
                              'AcademicYear': academicYear,
                              'Semester': semester,
                              'CourseName': courseName,
                              'Period': period,
                              'Building': building,
                              'Classroom': classroom,
                              }

    df = pd.DataFrame(csvDict)
    df.to_csv('res/result.csv', index=False)
    with open('static/rootData.json', 'w') as fp:
        json.dump(jsonDict, fp)


def main(initialData):
    ###
    # initialData[0] = buildingList
    # initialData[1] = courseDict
    # initialData[2] = studentList

    buildingList = initialData[0]
    courseDict = initialData[1]
    studentList = initialData[2]

    courseContinuouslyDict = IntegrateCourseContinuously(studentList)
    courseDict, buildingList = AssignClassroom(
        courseContinuouslyDict, courseDict, buildingList)
    # for building in buildingList[:1]:
    #     for classroom in building.classrooms:
    #         print(classroom.buildingName)
    #         print(classroom.name)
    #         print(classroom.usingCourse)
    OutputResult(courseDict)


@app.route('/')
def Home():
    try:
        df = pd.read_csv('res/result.csv')
        return render_template('root.html')
    except Exception as e:
        error_message = f"Error fetching lottery numbers: {str(e)}"
        return render_template('error.html', error=error_message)


if __name__ == '__main__':
    initialData = init()
    main(initialData)

    # app.run(debug=True)


# @app.route("/AdminLoginPage")
# def LoginAdmin():
#     if 'userName' in session:
#         user = session['userName']
#         return render_template("adminLogin.html", userName=user)
#     else:
#         user = None
#         return render_template("error.html", userName=user)


# @app.route("/AdminLogin", methods=["GET", "POST"])
# # 從這里定義具體的函式 回傳值均為json格式
# def AdminLogin():
#     # 由于POST、GET獲取資料的方式不同，需要使用if陳述句進行判斷
#     # 從前端拿數據
#     if request.method == "GET":
#         return render_template("login.html")
#     elif request.method == "POST":
#         val = request.get_json()
#         userName = val["userName"]
#         password = val["password"]
#         sql = "SELECT user_name,password FROM administrator"
#         result = ConnectDBHaveResult(sql)
#         for i in range(0, len(result)):
#             if userName == result[i][0] and password == result[i][1]:
#                 session['userName'] = userName
#                 return {'message': "success"}
#             elif userName == result[i][0] and password != result[i][1]:
#                 return {'message': "passwordFail"}
#         return {'message': "userNameFail"}
