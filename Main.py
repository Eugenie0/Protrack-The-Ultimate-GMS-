from datetime import date
from Logic import Member,GymManager,WorkoutPlan
import os

manager = GymManager()

if os.path.exists('gym_data.json'):
    manager.load_from_file()
    print('Gym data has been loaded successfully!')
else:
    print('No saved data found. Starting with an empty gym.')

def register_member():
    print('\n--- Register New Member ---')
    member_id = input('Enter Member ID: ')
    name = input('Enter name: ')
    try:
        age = int(input('Enter age: '))
    except ValueError:
        print('The age must be a number.')
        return
    join_date = date.today().isoformat()
    member = Member(member_id,name,age,join_date)
    print(manager.register_member(member))

def remove_member():
    print('\n--- Remove Current Member ---')
    member_id = input("Enter the Member's ID: ")
    verification = input('Are you sure you want to remove this member? [Y/N]: ').lower()
    if verification == 'y':
        print(manager.remove_member(member_id))
    elif verification == 'n':
        print('You have chosen not to remove the member.')
    else:
        print('Invalid input. Please enter Y or N')
        return

def create_workoutplan():
    print('\n--- Create a Workout Plan ---')
    plan_id = input('Enter Plan ID: ')
    name = input('Enter name: ')
    focus_area = input('Enter the focus area (Legs, Upper-body e.g): ')
    exercises = input('Enter the exercises (Separate with commas): ').split(',')
    exercises = [ex.strip() for ex in exercises]
    workout_plan = WorkoutPlan(plan_id,name,focus_area,exercises)
    print(manager.add_workoutplan(workout_plan))

def remove_workoutplan():
    print('\n--- Remove a Workout Plan ---')
    plan_id = input('Enter the Plan ID: ')
    verification = input('Are you sure you want to remove this workout plan? [Y/N]: ').lower()
    if verification == 'y':
        print(manager.remove_workoutplan(plan_id))
    elif verification == 'n':
        print('You have chosen not to remove the workout plan.')
    else:
        print('Invalid input. Please enter Y or N')
        return

def assign_plan():
    print('\n--- Assign a Workout Plan ---')
    plan_id = input('Enter the Plan ID: ')
    member_id = input("Enter the Member's ID: ")
    print(manager.assign_workoutplan(plan_id,member_id))

def unassign_plan():
    print('\n--- Unassign a Workout Plan ---')
    member_id = input("Enter the Member's ID: ")
    plan_id = input('Enter the Plan ID: ')
    print(manager.unassign_workoutplan(plan_id,member_id))

def log_attendance():
    print("\n--- Log Attendance ---")
    member_id = input("Enter the Member's ID: ")
    use_today = input("Do you want to use today's date? [Y/N]: ").lower
    if use_today == 'y':
        today = date.today().isoformat()
        print(manager.log_attendance(today,member_id))
    else:
        attendance_date = input('Enter date (YYYY-MM-DD): ')
    print(manager.log_attendance(attendance_date,member_id))

def member_attendance_report():
    print('\n--- Member Attendance Report ---')
    member_id = input("Enter the Member's ID: ")
    print(manager.get_member_attendance_report(member_id))

def record_payment():
    print('\n--- Record Payment ---')
    member_id = input("Enter the Member's ID: ")
    try:
       amount = float(input('Enter the payment amount: '))
    except ValueError:
        print('Invalid input. Please try again.')
        return
    use_today = input("Do you want to use today's date? [Y/N]: ").lower
    if use_today == 'y':
        today = date.today().isoformat()
        print(manager.members[member_id].add_payment(today,amount))
    else:
       payment_date = input('Enter date (YYYY-MM-DD): ')
    print(manager.members[member_id].add_payment(payment_date,amount)) 

def get_payment_logs():
    print('\n--- Payment Logs ---')
    print(manager.get_payment_logs())

def get_unpaid_members():
    print('\n--- Unpaid Members ---')
    cutoff = input('Enter the due date for membership or leave blank if its today (YYYY-MM-DD): ')
    if not cutoff:
        cutoff = date.today().isoformat()
    unpaid_members = manager.get_unpaid_members(cutoff)
    print(unpaid_members)

def view_member_info():
    print('\n--- View Member Info ---')
    member_id = input("Enter the Member's ID: ")
    member = manager.get_members_info(member_id)
    if member:
        print(f"Name: {member.name}")
        print(f"Age: {member.age}")
        print(f"Join Date: {member.join_date}")
        print(f"Workout Plan: {member.workout_plan.name if member.workout_plan else 'None'}")
        print(f"Attendance Log: {member.attendance_log}")
        print(f"Payment History: {member.payment_log}")
    else:
        print('Member is not found.')
    
def view_workout_plans():
    print('\n--- View Workout Plan Details ---')
    plan_id = input('Enter the Plan ID: ')
    plan = manager.get_workoutplans_info(plan_id)
    if plan:
        print(f'Name: {plan.name}')
        print(f'Focus Area: {plan.focus_area}')
        print(f'Exercises: {plan.exercises}')

def view_summary_report():
    print('\n--- Summary Report ---')
    report = manager.get_summary_report()
    print(f'Total Members: {report['total_members']}')
    print(f"Member's active today: {report['active_today']}")
    print(f'Unpaid Members: {report['unpaid_members']}')

def save_data():
    manager.save_to_file()
    print('Data successfully saved.')

def menu():
    while True:
        print("\n=== Gym Manager Menu ===")
        print("1. Register Member")
        print("2. Remove a Member")
        print("3. Create Workout Plan")
        print("4. Remove Workout Plan")
        print("5. Assign Plan to Member")
        print("6. Unassign Plan from Member")
        print("7. Log Member Attendance")
        print("8. View Member Attendance Report")
        print("9. Record Payment")
        print("10. View All Payment Logs")
        print("11. View Unpaid Members")
        print("12. View Member Info")
        print("13. View Workout Plan Info")
        print("14. View Summary Report")
        print("15. Save Data")
        print("16. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            register_member()
        elif choice == "2":
            remove_member()
        elif choice == "3":
            create_workoutplan()
        elif choice == "4":
            remove_workoutplan()
        elif choice == "5":
            assign_plan()
        elif choice == "6":
            unassign_plan()
        elif choice == "7":
            log_attendance()
        elif choice == "8":
            member_attendance_report()
        elif choice == "9":
            record_payment()
        elif choice == "10":
            get_payment_logs()
        elif choice == "11":
            get_unpaid_members()
        elif choice == "12":
            view_member_info()
        elif choice == "13":
            view_workout_plans()
        elif choice == "14":
            view_summary_report()
        elif choice == "15":
            save_data()
        elif choice == "16":
            print("👋 Exiting program. Goodbye!")
            break
        else:
            print("❌ Invalid option. Try again.")

if __name__ == "__main__":
    menu()

