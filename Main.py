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

def create_workoutplan():
    print('\n--- Create a Workout Plan ---')
    plan_id = input('Enter Plan ID: ')
    name = input('Enter name: ')
    focus_area = input('Enter the focus area (Legs, Upper-body e.g): ')
    exercises = input('Enter the exercises (Separate with commas): ').split(',')
    exercises = [ex.strip() for ex in exercises]
    workout_plan = WorkoutPlan(plan_id,name,focus_area,exercises)
    print(manager.add_workoutplan(workout_plan))

def assi

