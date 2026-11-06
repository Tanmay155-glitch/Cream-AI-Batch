# Day 1: Project Introduction Script
# Student: Tanmay Subhash Gawali (SJ-52)
# Project: LeniGuide

# Project Card details stored in variables
project_id = "SJ-52"
project_name = "LeniGuide"
student_name = "Tanmay Gawali"
theme = "Travel & Culture"

user_persona = "History teacher planning a 2-day school trip for 40 students"
problem = "Conflicting fees and wrong timings online; need verified cave details"
data_source = "ASI official website (asi.nic.in)"

# Printing the project card using f-strings
print("=" * 50)
print(f"Project Name : {project_name}")
print(f"Project ID   : {project_id} ({theme})")
print(f"Created by   : {student_name}")
print("=" * 50)
print(f"Target User  : {user_persona}")
print(f"Problem Solved: {problem}")
print(f"Data Source  : {data_source}")
print("=" * 50)

# Taking input from the user
user_name = input("Enter your name: ")
user_question = input(f"Hi {user_name}, what do you want to ask about Ajanta or Ellora? ")

# Simple output response
print("\n" + "-" * 50)
print(f"Hello {user_name}!")
print(f"Your question was: '{user_question}'")
print(f"LeniGuide is setting up to answer cave-wise queries soon.")
print("-" * 50)