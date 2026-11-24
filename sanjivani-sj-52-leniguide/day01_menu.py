#!/usr/bin/env python3
"""
day01_menu.py — LeniGuide Interactive Menu
Student: Tanmay Subhash Gawali (Reg No: 2124UMLM2016, CSE AI & ML)
Project: SJ-52 | Product: LeniGuide
"""

SAFETY_NOTE = "Timings, fees and closures can change. Confirm on asi.nic.in before you travel."

SAMPLE_QUESTIONS = [
    "Q1: Which day is Ellora closed? And Ajanta?",
    "Q2: What is special about the Kailasa temple in Ellora cave 16?",
    "Q3: Which caves in Ajanta have the best paintings?",
    "Q4: We are 4 teachers and 40 students under 15 on 14-15 December. Which site on which day, and total ticket cost?",
    "Q5: Make a 3-hour plan for Ellora covering Buddhist, Hindu and Jain caves.",
    "Q6: How many tourists visited Ajanta caves last Diwali?",
]


def show_menu():
    print("\n" + "=" * 50)
    print("  LeniGuide — Interactive Menu")
    print("=" * 50)
    print("  1. About LeniGuide")
    print("  2. Sample Questions")
    print("  3. Check Closed Day")
    print("  0. Exit")
    print("-" * 50)


def about():
    print("\nLeniGuide is a cave-by-cave guide to Ajanta and Ellora.")
    print("It tells you what to see in each cave, gives correct ASI")
    print("timings and fees, and plans which day to visit which site.")
    print(f"\n⚠️  {SAFETY_NOTE}")


def show_questions():
    print("\nSample Questions LeniGuide Can Answer:")
    for q in SAMPLE_QUESTIONS:
        print(f"  {q}")


def check_closed_day():
    day = input("\nEnter a weekday (e.g. Monday): ").strip().capitalize()
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    if day not in weekdays:
        print(f'  Invalid weekday: "{day}". Please enter a valid weekday.')
    elif day == "Monday":
        print("  ❌ Ajanta is CLOSED on Mondays.")
        print("  ✅ Ellora is OPEN on Mondays.")
    elif day == "Tuesday":
        print("  ✅ Ajanta is OPEN on Tuesdays.")
        print("  ❌ Ellora is CLOSED on Tuesdays.")
    else:
        print(f"  ✅ Both Ajanta and Ellora are OPEN on {day}s.")


def main():
    print("Welcome to LeniGuide!")
    while True:
        show_menu()
        try:
            choice = input("Choose an option: ").strip()
        except EOFError:
            break

        if choice == "1":
            about()
        elif choice == "2":
            show_questions()
        elif choice == "3":
            check_closed_day()
        elif choice == "0":
            print("\nThank you for using LeniGuide! Safe travels. 🙏")
            break
        else:
            print(f'  Invalid option: "{choice}". Please enter 0, 1, 2, or 3.')


if __name__ == "__main__":
    main()
