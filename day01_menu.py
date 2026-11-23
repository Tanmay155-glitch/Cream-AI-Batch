"""
Day 1 - Interactive Menu for LeniGuide
Demonstrates loops, conditionals, and user input handling.
"""

def show_about():
    """Display information about LeniGuide"""
    print("\n" + "=" * 70)
    print("ABOUT LENIGUIDE")
    print("=" * 70)
    print("LeniGuide is a cave-by-cave guide to Ajanta and Ellora.")
    print("It helps you plan which caves to visit, when to go, and what to see.")
    print()
    print("Target User: School teachers planning study tours")
    print("Data Sources: Official ASI websites + Wikipedia for reference")
    print()
    print("⚠️  SAFETY NOTE: Timings, fees and closures can change.")
    print("   Confirm on asi.nic.in before you travel.")
    print("=" * 70)

def show_sample_questions():
    """Display the 6 sample test questions"""
    print("\n" + "=" * 70)
    print("SAMPLE QUESTIONS")
    print("=" * 70)
    questions = [
        "1. Which day is Ellora closed? And Ajanta?",
        "2. What is special about the Kailasa temple in Ellora cave 16?",
        "3. Which caves in Ajanta have the best paintings?",
        "4. We are 4 teachers and 40 students under 15 coming on 14–15 December.",
        "   Which site on which day, and total ticket cost?",
        "5. Make a 3-hour plan for Ellora covering Buddhist, Hindu and Jain caves",
        "6. How many tourists visited Ajanta caves last Diwali?"
    ]
    for q in questions:
        print(q)
    print("=" * 70)

def check_site_closure():
    """Domain rule checker: which site is closed on a given day"""
    print("\n" + "=" * 70)
    print("SITE CLOSURE CHECKER")
    print("=" * 70)
    print("Enter a weekday to check which sites are open/closed:")
    print()
    
    weekday = input("Weekday (e.g., Monday, Tuesday, etc.): ").strip().capitalize()
    
    ajanta_closed = "Monday"
    ellora_closed = "Tuesday"
    
    if weekday == ajanta_closed:
        print(f"\n❌ Ajanta is CLOSED on {weekday}")
        print(f"✅ Ellora is OPEN on {weekday}")
    elif weekday == ellora_closed:
        print(f"\n✅ Ajanta is OPEN on {weekday}")
        print(f"❌ Ellora is CLOSED on {weekday}")
    elif weekday in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        print(f"\n✅ Both Ajanta and Ellora are OPEN on {weekday}")
    else:
        print(f"\n⚠️  '{weekday}' is not a valid weekday.")
        print("Please enter a day like Monday, Tuesday, etc.")
    
    print("=" * 70)

def main_menu():
    """Display and handle the main menu loop"""
    while True:
        print("\n" + "=" * 70)
        print("LENIGUIDE - MAIN MENU")
        print("=" * 70)
        print("1. About LeniGuide")
        print("2. Sample Questions")
        print("3. Site Closure Checker (which day is each site closed)")
        print("0. Exit")
        print("=" * 70)
        
        choice = input("Enter your choice (0-3): ").strip()
        
        if choice == "1":
            show_about()
        elif choice == "2":
            show_sample_questions()
        elif choice == "3":
            check_site_closure()
        elif choice == "0":
            print("\nThank you for using LeniGuide!")
            print("⚠️  Remember: Confirm timings and fees on asi.nic.in before you travel.")
            break
        else:
            print("\n⚠️  Invalid choice. Please enter 0, 1, 2, or 3.")

if __name__ == "__main__":
    main_menu()
