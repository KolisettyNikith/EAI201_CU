print("Welcome to student grading aI assistant")

student_name = input("Enter the student's name: ")


num_subjects = int(input("Enter number of subjects: "))

subjects = []
marks = []


for i in range(num_subjects):
    subject = input(f"Enter name of subject {i+1}: ")
    mark = float(input(f"Enter marks obtained in {subject}: "))
    subjects.append(subject)
    marks.append(mark)


total_marks = sum(marks)
max_marks = num_subjects * 100  
percentage = (total_marks / max_marks) * 100


if percentage >= 90:
    grade = "A+"
elif percentage >= 80:
    grade = "A"
elif percentage >= 70:
    grade = "B+"
elif percentage >= 60:
    grade = "B"
elif percentage >= 50:
    grade = "C"
else:
    grade = "F"


print("\n--- Student Report ---")
print(f"Name: {student_name}")
for i in range(num_subjects):
    print(f"{subjects[i]}: {marks[i]} / 100")
print(f"Total Marks: {total_marks} / {max_marks}")
print(f"Percentage: {percentage:.2f}%")
print(f"Grade: {grade}")
