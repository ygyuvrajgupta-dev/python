class Person:
    def set_person_details(self, name, age):
        self.name = name
        self.age = age

    def display_person_details(self):
        print(f"Name: {self.name}")
        print(f"Age: {self.age}")

class Student(Person):
    def set_student_details(self, roll_no, marks):
        self.roll_no = roll_no
        self.marks = marks

    def display_student_details(self):
        self.display_person_details()
        print(f"Roll No: {self.roll_no}")
        print(f"Marks: {self.marks}")

s = Student()

s.set_person_details("yuvraj", 18)
s.set_student_details("086", 18)
s.display_student_details()''' 