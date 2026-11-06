# Day 1: Menu Loop & Domain Rule Check
# Student: Tanmay Subhash Gawali (SJ-52)
# Project: LeniGuide

while True:
    print("\n===== LENIGUIDE MENU =====")
    print("1. About LeniGuide")
    print("2. Sample Questions")
    print("3. Check Day & Closing Rule")
    print("0. Exit")
    print("==========================")
    
    choice = input("Enter your choice (0-3): ").strip()
    
    if choice == "1":
        print("\n--- About LeniGuide ---")
        print("LeniGuide is an AI travel assistant for Ajanta and Ellora caves.")
        print("It provides verified cave details, official ASI timings, and fees.")
        print("Built by Tanmay Gawali for Sanjivani AI Training.")
        
    elif choice == "2":
        print("\n--- Sample Questions ---")
        print("1. Which day is Ellora closed? And Ajanta?")
        print("2. What is special about Kailasa temple in Cave 16?")
        print("3. Which caves have the best paintings in Ajanta?")
        print("4. How much will tickets cost for 4 teachers and 40 students?")
        print("5. Make a 3-hour plan covering Buddhist, Hindu, and Jain caves.")
        
    elif choice == "3":
        print("\n--- Site Open / Closed Check ---")
        site = input("Enter site (Ajanta / Ellora): ").strip().lower()
        day = input("Enter day of the week (e.g. Monday, Tuesday, Sunday): ").strip().lower()
        
        # Domain rule: Ajanta is closed on Mondays, Ellora on Tuesdays
        if site == "ajanta":
            if day == "monday":
                print("-> Result: Ajanta is CLOSED on Mondays!")
            else:
                print(f"-> Result: Ajanta is OPEN on {day.capitalize()} (9 AM to 5 PM).")
        elif site == "ellora":
            if day == "tuesday":
                print("-> Result: Ellora is CLOSED on Tuesdays!")
            else:
                print(f"-> Result: Ellora is OPEN on {day.capitalize()} (Sunrise to Sunset).")
        else:
            print("-> Invalid site! Please type either 'Ajanta' or 'Ellora'.")
            
    elif choice == "0":
        print("\nThank you for using LeniGuide. Bye!")
        
    else:
        print("\nInvalid option! Please choose 0, 1, 2, or 3.")