# ProTrack GMS

ProTrack GMS is a desktop Gym Management System built with Python, CustomTkinter, and tkcalendar. It provides gym owners and trainers with an intuitive, all‑in‑one solution for managing memberships, workout plans, attendance tracking, and payments—no web server required.

---

## 🚀 Why ProTrack GMS?

As an actuarial science student learning Python and OOP, I wanted a capstone project that:

1. **Reinforced** core concepts of classes, file I/O, and error handling.  
2. **Practically benefited** a real business—my friend’s gym—by automating manual spreadsheets.  
3. **Explored GUI development**, designing a clean, mobile‑style interface with CustomTkinter.  
4. **Bridged** data tracking (attendance, payments) with simple analytics (popular plans, top attendees).

After weeks of Python practice, this project let me level‑up from console scripts to a feature‑rich desktop app—while delivering genuine value to my client.

---

## ⚙️ Key Features

### Dashboard
- **Monthly Cutoff** display: automatically shows the last day of the current month.  
- **High‑level stats**: total members, workout plans, today’s attendance, paid vs. overdue counts.  
- **Popular Plan** overview & **weekly attendance** bar chart.  

### Members
- **Create**, **Read**, **Update**, **Delete** members (CRUD).  
- **Assign/unassign** workout plans via dropdown—no retyping required.  
- **Live table** view of all members and their current plan.

### Workout Plans
- Full CRUD for plans, including exercise lists and focus areas.  
- At‑a‑glance count of how many members are assigned to each plan.

### Attendance
- **Calendar picker** for manual entry or “today” auto‑fill.  
- **Top 5 attendees** leaderboard for the past 7 days.

### Payments
- **Calendar picker** + amount entry to log member payments.  
- Table shows each member’s last payment date and “Paid” vs. “Overdue” status for the current month.

### Persistence & UX
- All data saved in a single `gym_data.json` file.   
- One‑click Save/Exit in the nav bar—no command‑line.

---
