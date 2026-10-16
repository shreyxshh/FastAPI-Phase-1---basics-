import json
import os
from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field

app = FastAPI()
FILE_PATH = 'students.json'

#Json Operations

def load_students() -> list:
    if not os.path.exists(FILE_PATH):
        return []
    with open("students.json", "r") as file:
        return json.load(file)

def save_students(data : list):
    with open('students.json', 'w') as file:
        json.dump(data,file,indent=4)

#Validation models

#request validation
class StudentCreate(BaseModel):
    name : str = Field(min_length=3, max_length=20, description="Enter Student name : ")
    course : str = Field(min_length=3, max_length=20, description="Enrolled course name : ")

#updation validation
class StudentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=50, description="Updated name (optional)")
    course: str | None = Field(default=None, min_length=2, max_length=50, description="Updated course (optional)")

#response validation
class StudentResponse(BaseModel):
    id : int 
    name : str
    course : str

#Endpoints 

@app.get("/test")
def test():
    return 'the server is working'

#getting all students and validates the whole list of students being send as a response 
#applied filteration and pagination 
@app.get("/students",response_model=list[StudentResponse])
def get_students(
    course : str | None = Query(default=None, description="Add filteration based on courses : "),
    search : str | None = Query(default=None, description="Search student with name : "),
    skip : int = Query(default=0, ge=0, description="Number of items to skip : "),
    limit : int = Query(default=10, ge=1, le=100, description="Max amt of items to return : ")
):
    students = load_students()

    #filters students if they matches the course entered 
    if course: 
        students = [s for s in students if s['course'].lower() == course.lower()]

    #filters students if they matches the name 
    if search:
        students = [s for s in students if search.lower() == s['name'].lower()]

    return students[skip : skip + limit]

#getting student with unique id
@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int = Path(ge=0, description="enter the student id to retrieve : ")):
    students = load_students()
    for student in students: 
        if student["id"] == student_id:
            return student
    raise HTTPException(status_code=404, detail="Student not found")

#creating new student
@app.post("/students",status_code=201)
def create_student(new_student: StudentCreate):
    students = load_students()

    newID = 0 
    for student in students:
       newID = max(newID, student['id']) 

    student = {
        "id" : newID + 1,
        "name" : new_student.name,
        "course" : new_student.course
    }
    students.append(student)
    save_students(students)
    return {
        "message" : "Student Created successfully",
        "Student" : student
    }

#updating existing student and validating using studentUpdate
@app.put("/students/{student_id}")
def update_student(updated_data : StudentUpdate, student_id : int= Path(ge=0)):
    
    students = load_students()
    
    for student in students:
        if student["id"] == student_id:
            student["name"] = updated_data["name"]
            student["course"] = updated_data["course"]

            save_students(students)

        return{
            "mesaage" : "Student uploaded successfully!",
            "data" : student
        }
    raise HTTPException(status_code=404, detail="student not found")

#performing minor updates in students 
@app.patch("/students/{student_id}")
def patch_student(student_id: int, student: StudentUpdate):
    students = load_students()
    
    for s in students:
        if student["id"] == student_id:
            # Only update fields that were provided (not None)
            if student.name is not None:
                s["name"] = student.name
            if student.course is not None:
                s["course"] = student.course
                
            save_students(students)
            return {
                "message": "Student updated successfully",
                "student": student
            }
            
    raise HTTPException(status_code=404, detail="Student not found")

#deleting student 
@app.delete("students/{student_id}")
def delete_student(student_id : int = Path(ge=0)):
    students = load_students()

    remaining_students = [s for s in students if s['id'] != student_id]

    if len(students) == len(remaining_students):
        raise HTTPException(status_code=404, detail="student not found")

    save_students(remaining_students)
    return{
        "message" : "Student has been deleted!"
    }
