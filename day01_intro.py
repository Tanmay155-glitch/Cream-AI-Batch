"""
Day 1 - Introduction to LeniGuide
Displays project information and interacts with the user.
"""

# Project information
project_id = "SJ-52"
student_name = "Tanmay Subhash Gawali"
reg_no = "2124UMLM2016"
product_name = "LeniGuide"
product_desc = "A cave-by-cave guide to Ajanta and Ellora UNESCO World Heritage Sites"
target_user = "School history teacher planning study tours for Class 9 students"

# Display project card
print("=" * 70)
print(f"PROJECT: {product_name}")
print("=" * 70)
print(f"Project ID: {project_id}")
print(f"Student: {student_name} ({reg_no})")
print(f"Course: Sanjivani AI Training - 15 Days Course")
print(f"Theme: Travel & Culture")
print()
print(f"Product: {product_desc}")
print(f"Target User: {target_user}")
print()
print("Data Sources:")
print("  - ASI Ajanta: https://asi.nic.in/pages/WorldHeritageAjantaCaves")
print("  - ASI Ellora: https://asi.nic.in/pages/WorldHeritageElloraCaves")
print()
print("⚠️  SAFETY NOTE: Timings, fees and closures can change.")
print("   Confirm on asi.nic.in before you travel.")
print("=" * 70)
print()

# Interactive section
user_name = input("What is your name? ")
print(f"\nHello, {user_name}! Welcome to LeniGuide.")
print()

user_question = input("What would you like to know about Ajanta or Ellora caves? ")
print()
print(f"You asked: \"{user_question}\"")
print(f"\n{user_name}, LeniGuide will help you find answers from official ASI sources.")
print("This system is under development. Stay tuned!")
