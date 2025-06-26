from typing import List
import json
from datetime import date

class Member:
    def __init__(self,member_id,name,age,join_date):
        self.member_id = member_id
        self.name = name
        self.age = age
        self.join_date = join_date
        self.workout_plan = None
        self.attendance_log = []
        self.payment_log = []

    def assign_plan(self, workout_plan):
        self.workout_plan = workout_plan
        return f'{workout_plan} has been successfully assigned.'
    
    def attendance(self, date):
        self.attendance_log.append(date)
        return f'{date} has been successfully logged.'

    def add_payment(self, date, amount):
        self.payment_log.append((date, amount))
        return f'Payment made on: {date} has been successfully logged.'
    
    def get_payment_history(self):
        if not self.payment_log:
            return "No payments made"
        return f"Last payment: KES {self.payment_log[-1][0]} on {self.payment_log[-1][1]}"
    
    def get_attendance(self):
        return f'{list(self.attendance_log)}'
    
    def to_dict(self):
        return {
            "member_id": self.member_id,
            "name": self.name,
            "age": self.age,
            "join_date": self.join_date,
            "workout_plan_id": self.workout_plan.plan_id if self.workout_plan else None,
            "payment_history": self.payment_log,
            "attendance_log": self.attendance_log
        }

    @classmethod
    def from_dict(cls, data, workout_plans):
        member = cls(data["member_id"], data["name"], data["age"], data["join_date"])
        member.payment_log = data["payment_history"]  # also fix key name here
        member.attendance_log = data["attendance_log"]
        if data["workout_plan_id"]:
            member.workout_plan = workout_plans.get(data["workout_plan_id"])
        return member


class WorkoutPlan:
    def __init__(self, plan_id,name,focus_area,exercises):
        self.plan_id = plan_id
        self.name = name
        self.focus_area = focus_area
        self.exercises = exercises

    def __str__(self):
        return f'Plan Name: {self.name}, Focus Area: {self.focus_area}, Exercises: {self.exercises}.'
    
    def to_dict(self):
        return {
            'plan_id': self.plan_id,
            'name': self.name,
            'focus_area': self.focus_area,
            'exercises': self.exercises
        }
    
    @classmethod
    def from_dict(cls,data):
         return cls(data["plan_id"], data["name"], data["focus_area"], data["exercises"])


class GymManager:
    def __init__(self):
        self.members = {}         # member_id -> Member object
        self.workout_plans = {}   # plan_id -> WorkoutPlan object
    
    def register_member(self,member):
        if member.member_id in self.members:
            return f'This member is already registered.'
        else:
            self.members[member.member_id] = member
            return f'Member has been successfully registered.'
        
    def remove_member(self,member_id):
        if member_id in self.members:
            self.members.pop(member_id)
            return "This member has been successfully removed from the gym's database."
        else:
            return 'This is person is not a current member of the gym.'
    
    def get_members(self):
        return list(self.members.values())
    
    def get_members_info(self,member_id):
        return self.members.get(member_id)

    def get_payment_logs(self):
        log = []
        for member_id,member in self.members.items():
            log.append(f'{member_id}: {member.get_payment_history()}')
        return '\n'.join(log)
    
    def get_unpaid_members(self, cutoff_date):
        unpaid = []
        for member in self.members.values():
            if not member.payment_log or member.payment_log[-1][1] < cutoff_date:
                unpaid.append(member)
        return unpaid

    def add_workoutplan(self,plan):
        if plan.plan_id in self.workout_plans:
            return 'This workout plan has already been created.'
        else:
            self.workout_plans[plan.plan_id] = plan
            return 'The workout plan has been successfully added to the system.'
    
    def remove_workoutplan(self,plan_id):
        for member in self.members.values():
            if member.workout_plan and member.workout_plan.plan_id == plan_id:
                member.workout_plan = None
        if plan_id in self.workout_plans:
            self.workout_plans.pop(plan_id)
            return f"{plan_id} has been successfully removed from the gym's database."

    def assign_workoutplan(self,plan_id,member_id):
        if member_id in self.members and plan_id in self.workout_plans:
            member = self.members[member_id]
            workout_plan = self.workout_plans[plan_id]
            return member.assign_plan(workout_plan)
        else:
            return 'Invalid member ID or workout plan ID.'
    
    def unassign_workoutplan(self,plan_id,member_id):
        if member_id not in self.members:
            return f"Member ID: {member_id} was not found in the gym's database."
        member = self.members[member_id]
        if member.workout_plan and member.workout_plan.plan_id == plan_id:
            member.workout_plan = None
            return f'{plan_id} has been successfully unassigned from member {member_id}.'
        else:
            return f'{plan_id} is not currently assigned to member {member_id}.'
    
    def get_workplans(self):
        return list(self.workout_plans.values())
    
    def get_workoutplans_info(self,plan_id):
        return self.workout_plans.get(plan_id)
    
    def log_attendance(self, date, member_id):
        if member_id in self.members:
            self.members[member_id].attendance(date)
            return f"{member_id} has successfully been logged in for: {date}."
        else:
            return f'This person is currently not a member at the gym.'

    def save_to_file(self, filename="gym_data.json"):
        data = {
            "workout_plans": [plan.to_dict() for plan in self.workout_plans.values()],
            "members": [member.to_dict() for member in self.members.values()]
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
    
    def load_from_file(self, filename="gym_data.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                # First load plans
                for plan_data in data.get("workout_plans", []):
                    plan = WorkoutPlan.from_dict(plan_data)
                    self.workout_plans[plan.plan_id] = plan
                # Then load members
                for member_data in data.get("members", []):
                    member = Member.from_dict(member_data, self.workout_plans)
                    self.members[member.member_id] = member
        except FileNotFoundError:
            pass

    def get_summary_report(self):
        return {
        "total_members": len(self.members),
        "active_today": sum(1 for m in self.members.values() if date.today().isoformat() in m.attendance_log),
        "unpaid_members": len(self.get_unpaid_members(date.today().isoformat()))
        }