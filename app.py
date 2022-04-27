from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json
from flask_cors import CORS, cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request
import pandas as pd

from sqlalchemy import text

from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token, create_refresh_token)

##sonuççç
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = '*****'
# app.config['SQLALCHEMY_DATABASE_URI'] = '****'

app.secret_key = 'super secret key'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
jwt = JWTManager(app)
cors = CORS(app)

db = SQLAlchemy(app)


class Student(db.Model):
    studentNumber = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    departmentID = db.Column(db.Integer, db.ForeignKey("department.ID"))
    enrollments = db.relationship("Enrollment")
    mail = db.Column(db.Unicode)
    Active_Passive = db.Column(db.Unicode)

    def __init__(self, name, departmentID, Active_Passive, mail, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.departmentID = departmentID
        self.mail = mail
        self.Active_Passive = Active_Passive


# k
class Classroom(db.Model):
    classroomID = db.Column(db.Integer, primary_key=True)
    capacity = db.Column(db.Integer)
    lab = db.Column(db.Boolean)
    location = db.Column(db.Unicode)
    name = db.Column(db.Unicode)
    people_number = db.Column(db.Integer)

    sections = db.relationship('Section', backref='Classroom')
    sensorses = db.relationship('Sensors', backref='Classroom')

    def __init__(self, capacity, lab, location, people_number, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.capacity = capacity
        self.lab = lab
        self.location = location
        self.name = name
        self.people_number = people_number


class Courses(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    courseCode = db.Column(db.Unicode)
    credit = db.Column(db.Integer)
    name = db.Column(db.Unicode)
    departmentID = db.Column(db.Integer, db.ForeignKey("department.ID"))
    sections = db.relationship('Section', backref='Courses')

    def __init__(self, courseCode, credit, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.courseCode = courseCode
        self.credit = credit
        self.name = name


class Department(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    facultyID = db.Column(db.Integer, db.ForeignKey("faculty.ID"))
    instructors = db.relationship('Instructor', backref='Department')
    courses = db.relationship('Courses', backref='Department')
    students = db.relationship('Student', backref='Department')

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name


class Enrollment(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    studentID = db.Column(db.Integer, db.ForeignKey("student.studentNumber"))
    sectionID = db.Column(db.Integer, db.ForeignKey("section.ID"))


class Faculty(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    departments = db.relationship('Department', backref='Faculty')

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name


class Instructor(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    departmentID = db.Column(db.Integer, db.ForeignKey("department.ID"))
    sections = db.relationship('Section', backref='Instructor')
    mail = db.Column(db.Unicode)
    Active_Passive = db.Column(db.Unicode)

    def __init__(self, departmentID, Active_Passive, name, mail, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.departmentID = departmentID
        self.name = name
        self.mail = mail
        self.Active_Passive = Active_Passive


class Section(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.Integer)
    time = db.Column(db.Unicode)
    instructorID = db.Column(db.Integer, db.ForeignKey("instructor.ID"))
    courseID = db.Column(db.Integer, db.ForeignKey("courses.ID"))
    classroomID = db.Column(db.Integer, db.ForeignKey("classroom.classroomID"))
    enrollments = db.relationship("Enrollment", backref="Section")

    def __init__(self, section, time, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.section = section
        self.time = time


class Sensors(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    tempature = db.Column(db.Integer)
    humidity = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    classroomID = db.Column(db.Integer, db.ForeignKey("classroom.classroomID"))

    def __init__(self, tempature, humidity, date, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tempature = tempature
        self.humidity = humidity
        self.date = date


class People_count(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Unicode)
    number_of_people = db.Column(db.Integer)
    camera = db.Column(db.Unicode)

    def __init__(self, date, number_of_people, camera, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.date = date
        self.number_of_people = number_of_people
        self.camera = camera


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.Unicode)
    email = db.Column(db.Unicode)
    role = db.Column(db.Unicode)


@cross_origin()
@app.route('/', methods=['GET', 'POST'])
##Welcome Page
def welcome():
    studentName = Student.query.filter_by(mail="tufekciy@mef.edu.tr").first()

    return str(studentName.studentNumber)


@app.route('/people_count', methods=['GET', 'POST'])
##Welcome Page
def get_people_count():
    number_of_people2 = People_count.query.order_by(text('-id')).first()
    d = [{
        'Date': number_of_people2.date,
        'Number_of_people': number_of_people2.number_of_people,
        'Camera': number_of_people2.camera,

    }]
    d2 = json.dumps(d)

    return d2


@app.route('/people_count/<camera_name>', methods=['GET', 'POST'])
##Welcome Page
def get_people_count_with_camera(camera_name):
    people_count_camera = People_count.query.filter_by(camera=camera_name).all()

    if people_count_camera == None:
        return 400
    else:
        people_count_camera_last = people_count_camera[-1]

        d = [{
            'Date': people_count_camera_last.date,
            'Number_of_people': people_count_camera_last.number_of_people,
            'Camera': people_count_camera_last.camera,

        }]
        d2 = json.dumps(d)

        return d2


@app.route('/api/classrooms/<id>', methods=['GET'])
def get_sensor_info(id):
    classroom = Classroom.query.filter_by(classroomID=id).first()

    if classroom == None:
        return 400

    else:
        Sensor = Sensors.query.filter_by(classroomID=classroom.classroomID).first()
        print(Sensor)
        print(classroom.classroomID)
        d = [{
            'Classroom ID': classroom.classroomID,
            'Temperature': Sensor.tempature,
            'Humidity': Sensor.humidity,
            'PeopleClass': classroom.people_number,
        }]

        d2 = json.dumps(d)
    return d2


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(force=True)
    email = data["email"]
    password = data["password"]
    role = data["role"]

    user = User.query.filter_by(
        email=email).first()  # if this returns a user, then the email already exists in database

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        return "Hata mesaji", 400

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, role=role, password=generate_password_hash(password, method='sha256'))
    access_token = create_access_token(identity=data['email'])
    refresh_token = create_refresh_token(identity=data['email'])
    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    d = [{
        'status': "ok message",
        'access_token': access_token,
        'refresh_token': refresh_token

    }]

    d2 = json.dumps(d)

    return d2


@app.route('/login', methods=['POST'])
def login_post():
    data = request.get_json(force=True)
    email = data["email"]
    password = data["password"]

    user = User.query.filter_by(email=email).first()
    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        return "giris basarisiz", 401

    access_token = create_access_token(identity=data['email'])
    refresh_token = create_refresh_token(identity=data['email'])
    # if the user doesn't exist or password is wrong, reload the page
    role = user.role

    d = [{
        'role': role,
        'access_token': access_token,
        'refresh_token': refresh_token

    }]

    d2 = json.dumps(d)

    # if the above check passes, then we know the user has the right credentials
    return d2


@app.route('/api/users/<id>', methods=['GET', 'POST'])
def home(id):
    studentName = Student.query.filter_by(studentNumber=id).first()  ##Eğer verilen öğrenci yoksa 400 dönüyor
    if studentName == None:
        return 400

    else:
        departmentName = Department.query.filter_by(
            ID=studentName.departmentID).first()  # Verilen öğrenci numarasından departman
        facultyName = Faculty.query.filter_by(ID=departmentName.facultyID).first()  # Departmandan fakülteyi buluyoruz
        enrollmentID = Enrollment.query.filter_by(
            studentID=id).first()  ## verilen öğrenci numarasından enrollemntları buluyor.
        sectionID = enrollmentID.sectionID  ##Enrolmentlardan section ıdleri çekiyoruz
        sectionSS = Section.query.filter_by(ID=sectionID).first()  ## setion idlerden section bilgilerine ulaşıyoruz
        sectionTime = sectionSS.time  ## section zamanı

        instructorSS = Instructor.query.filter_by(ID=sectionSS.instructorID).first()  # seçilen sectionun instructorı
        instructorName = instructorSS.name  ##instructor id'den istructor name
        courseSS = Courses.query.filter_by(ID=sectionSS.courseID).first()  ## Course idyi sectiondan buluyoruz
        courseCode = courseSS.courseCode  ##Course id'yi bulduktan sonra o id'den course hakkındahi herşeye ulaşıyoruz
        courseCredit = courseSS.credit
        courseName = courseSS.name
        ## En sonunda İstenilen tüm değerler
        d = [{
            'Department': departmentName.name,
            'Faculty': facultyName.name,
            'StudentName': studentName.name,
            'Instructor': instructorName,
            'CourseCode': courseCode,
            'CourseCredit': courseCredit,
            'CourseName': courseName,
            'SectionTime': sectionTime

        }]
        d2 = json.dumps(d)

    return d2


@app.route('/lectures/<email>', methods=['GET', 'POST'])
def get_lectures1(email):  ##Mailden öğrenci ders programı için
    studentName = Student.query.filter_by(mail=email).first()
    studentID = studentName.studentNumber
    student = Enrollment.query.filter_by(studentID=studentID).all()
    sectionID = []
    for i in range(0, len(student)):
        sectionID.append(student[i].sectionID)
    print(sectionID)

    courses_ID = []
    instructor = []
    sectionTime = []

    courseName = []
    courseCode = []
    courseCredit = []
    section2 = []

    for i in range(0, len(sectionID)):
        section = Section.query.filter_by(ID=sectionID[i]).first()
        sectionTime.append(section.time)
        section2.append(section.section)

        instructors = Instructor.query.filter_by(ID=section.instructorID).first()
        instructor.append(instructors.name)

        coursess = Courses.query.filter_by(ID=section.courseID).first()
        courseName.append(coursess.name)
        courseCode.append(coursess.courseCode)
        courseCredit.append(coursess.credit)
    department = Department.query.filter_by(ID=studentName.departmentID).first()
    departmentName = department.name
    ###studentName = Enrollment.query.filter_by(email="tufekciy@mef.edu.tr").first()

    d = [{
        'CourseCode': courseCode,
        'CourseCredit': courseCredit,
        'CourseName': courseName,
        'SectionTime': sectionTime,
        'Instructor': instructor,
        'section': section2,
        'department': departmentName,

    }]
    d2 = json.dumps(d, ensure_ascii=False)

    return d2


@app.route('/upload', methods=['GET', 'POST'])
def get_excel():
    if request.method == "POST":
        f = request.files['file']
        xls = pd.ExcelFile(f)
        course = pd.read_excel(xls, 'Course')

        instructor = pd.read_excel(xls, 'Instructor')

        student = pd.read_excel(xls, 'Student')

        faculty = pd.read_excel(xls, 'Faculty')

        department = pd.read_excel(xls, 'Department')

        section = pd.read_excel(xls, 'Section')

        classroom = pd.read_excel(xls, 'Classroom')

        enrollment = pd.read_excel(xls, 'Enrollment')

        for i in range(len(faculty)):
            new_faculty = Faculty(name=faculty["Name"][i])
            db.session.add(new_faculty)
            db.session.commit()

        for i in range(len(department)):
            faculty2 = Faculty.query.filter_by(name=department["Faculty"][i]).first()
            print(faculty2.ID)

            new_department = Department(name=department["Name"][i], facultyID=faculty2.ID)
            db.session.add(new_department)
            db.session.commit()

        for i in range(len(student)):
            department = Department.query.filter_by(name=student["Department"][i]).first()

            new_student = Student(studentNumber=student["Student_Number"][i], name=student["Name"][i],
                                  mail=student["mail"][i], departmentID=department.ID,
                                  Active_Passive=student["Active_Passive"][i])
            db.session.add(new_student)
            db.session.commit()

        for i in range(len(instructor)):
            department = Department.query.filter_by(name=instructor["Department"][i]).first()

            new_instructor = Instructor(name=instructor["Name"][i], mail=instructor["mail"][i],
                                        departmentID=department.ID, Active_Passive=instructor["Active_Passive"][i])
            db.session.add(new_instructor)
            db.session.commit()

        for i in range(len(classroom)):
            new_classroom = Classroom(capacity=classroom["Capacity"][i], lab=classroom["Lab"][i],
                                      location=classroom["Location"][i], name=classroom["name"][i],
                                      people_number=classroom["people_number"][i])
            db.session.add(new_classroom)
            db.session.commit()

        for i in range(len(course)):
            department = Department.query.filter_by(name=course["Department"][i]).first()

            new_course = Courses(courseCode=course["Course Code"][i], credit=course["credit"][i],
                                 name=course["name"][i], departmentID=department.ID)
            db.session.add(new_course)
            db.session.commit()

        for i in range(len(section)):
            course2 = Courses.query.filter_by(name=section["Course"][i]).first()
            classroom = Classroom.query.filter_by(name=section["Classroom"][i]).first()
            instructor = Instructor.query.filter_by(name=section["instructor"][i]).first()

            new_section = Section(section=section["Section"][i], time=section["time"][i], courseID=course2.ID,
                                  classroomID=classroom.classroomID, instructorID=instructor.ID)
            db.session.add(new_section)
            db.session.commit()

        for i in range(len(enrollment)):

            course = Courses.query.filter_by(name=enrollment["Course"][i]).first()
            section_number = enrollment["Section"][i]

            section = Section.query.filter_by(courseID=course.ID).all()
            for sectionss in section:
                if sectionss.section == section_number:
                    real_section = sectionss.ID
                else:
                    real_section = None

            if real_section is not None:
                enrollement1 = Enrollment(studentID=enrollment["Student_Number"][i], sectionID=real_section)

            db.session.add(enrollement1)
            db.session.commit()
        return "200"
    else:
        return "401"


@app.route('/upload/file', methods=['GET', 'POST'])
def get_excel2():
    if request.method == "POST":
        if request.files is not None:
            return "200"
        else:
            return "400"


@app.route('/instructor/<email>', methods=['GET', 'POST'])
def get_lectures2(email):  ##instructor ders programı için
    instructorName = Instructor.query.filter_by(mail=email).first()
    studentID = instructorName.ID
    student = Section.query.filter_by(instructorID=studentID).all()
    sectionID = []

    for i in range(0, len(student)):
        sectionID.append(student[i].ID)
    print(sectionID)
    courses_ID = []
    instructor = []
    sectionTime = []

    courseName = []
    courseCode = []
    courseCredit = []
    section2 = []

    for i in range(0, len(sectionID)):
        section = Section.query.filter_by(ID=sectionID[i]).first()
        sectionTime.append(section.time)
        section2.append(section.section)

        coursess = Courses.query.filter_by(ID=section.courseID).first()
        courseName.append(coursess.name)
        courseCode.append(coursess.courseCode)
        courseCredit.append(coursess.credit)
    department = Department.query.filter_by(ID=instructorName.departmentID).first()
    departmentName = department.name
    ###studentName = Enrollment.query.filter_by(email="tufekciy@mef.edu.tr").first()

    d = [{
        'CourseCode': courseCode,
        'CourseCredit': courseCredit,
        'CourseName': courseName,
        'SectionTime': sectionTime,
        'section': section2,
        'department': departmentName,

    }]
    d2 = json.dumps(d, ensure_ascii=False)

    return d2


if __name__ == '__main__':
    app.run()
