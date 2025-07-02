# gui_app.py
import os, json, calendar
from datetime import date, timedelta, datetime
from pathlib import Path
from PIL import Image
import sys
from io import BytesIO


import customtkinter as ctk
from customtkinter import CTkImage, CTkFont
from CTkMessagebox import CTkMessagebox
from Logic import GymManager, Member, WorkoutPlan
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk
import tkinter as tk

os.chdir(os.path.dirname(__file__))

# --- Settings ---
APP_WIDTH, APP_HEIGHT = 1200, 760
ICON_DIR = "assets"
DATA_FILE = "gym_data.json"
BACKGROUND = "#e3f2fd"
NAV_TEXT = "#0d47a1"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Backend
manager = GymManager()
if Path(DATA_FILE).exists():
    manager.load_from_file()

# Icon loader
def load_icon(name, sz=(32,32)):
    p = Path(ICON_DIR) / f"{name}.png"
    return CTkImage(Image.open(p), size=sz) if p.exists() else None
icons = {
    'dashboard_icon': load_icon('dashboard', sz=(24,24)),             # small nav icon
    'dashboard_banner': load_icon('dashboard_banner', sz=(APP_WIDTH-40,180)),   
    'members': load_icon('members'),
    'workouts': load_icon('workouts'),
    'attendance': load_icon('attendance'),
    'payments': load_icon('payments'),
    'save': load_icon('save'),
    'exit': load_icon('exit'),
    'paid': load_icon('paid'),
    'unpaid': load_icon('unpaid'),
}

class GymApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ProTrack GMS")
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.configure(fg_color=BACKGROUND)
        self.report_callback_exception = lambda exc, val, tb: None

        # Convert icons to Tkinter PhotoImage after root exists
        self.tk_images = {}
        for key in ['paid', 'unpaid']:
            ctk_img = icons[key]
            if ctk_img:
                pil_img = ctk_img._light_image
                buf = BytesIO()
                pil_img.save(buf, format="PNG")
                self.tk_images[key] = tk.PhotoImage(master=self, data=buf.getvalue())
            else:
                self.tk_images[key] = None

        self._build_nav()
        self.main = ctk.CTkFrame(self, fg_color=BACKGROUND)
        self.main.pack(fill="both", expand=True)
        self.show_dashboard()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_nav(self):
        nav = ctk.CTkFrame(self, fg_color="white", height=50)
        nav.pack(fill="x")
        for txt, cmd, key in [
            ("Dashboard", self.show_dashboard, 'dashboard_icon'),
            ("Members",   self.show_members,   'members'),
            ("Workouts",  self.show_workouts,  'workouts'),
            ("Attendance",self.show_attendance,'attendance'),
            ("Payments",  self.show_payments,  'payments'),
            ("Save",      self._save_all,      'save'),
            ("Exit",      self.destroy,        'exit'),
        ]:
            b = ctk.CTkButton(
                nav, text=txt, image=icons[key], compound="left",
                fg_color="transparent", hover_color="#bbdefb",
                text_color=NAV_TEXT, font=CTkFont("Arial", 12, "bold"),
                command=cmd
            )
            b.pack(side="left", padx=8, pady=5)

    def clear(self):
        for w in self.main.winfo_children():
            w.destroy()

    def _save_all(self):
        manager.save_to_file(DATA_FILE)
        CTkMessagebox(message="Data saved!")

    def on_close(self):
        self._save_all()
        self.destroy()

    # --- Dashboard ---
    def show_dashboard(self):
        self.clear()

        # 5. Intro summary row
        summary = ("Welcome to ProTrack GMS: "
                   "Use the tabs above to Create, Read, Update or Delete info from your gym's database!"
                   " All data persists once saved.")
        ctk.CTkLabel(self.main, text=summary, wraplength=APP_WIDTH-40,
                     font=CTkFont("Arial", 12)).pack(pady=(10,5), padx=20)

        # Banner (point 1)
        banner = icons['dashboard_banner']
        if banner:
            ctk.CTkLabel(self.main, image=banner, text="").pack(pady=(5,20))

        stats = manager.get_summary_report()
        y,m = date.today().year, date.today().month
        last = calendar.monthrange(y,m)[1]
        cutoff = f"{y}-{m:02d}-{last}"
        ctk.CTkLabel(self.main, text=f"Monthly Cutoff: {cutoff}",
                     font=CTkFont("Arial", 14)).pack(pady=(0,10))

        # Stats cards
        tally = {}
        for mbr in manager.members.values():
            pid = mbr.workout_plan.plan_id if mbr.workout_plan else None
            if pid:
                tally[pid] = tally.get(pid,0) + 1
        popular = max(tally.keys(), key=lambda k: tally[k]) if tally else "N/A"
        paid_month = sum(1 for mbr in manager.members.values()
                         if mbr.payment_log and mbr.payment_log[-1][0].startswith(date.today().strftime("%Y-%m")))

        cards = [
            ("Members",        stats['total_members']),
            ("Plans",          len(manager.workout_plans)),
            ("Popular Plan",   popular),
            ("Today Attend",   stats['active_today']),
            ("Paid This Month",paid_month),
            ("Overdue",        stats['unpaid_members']),
        ]
        grid = ctk.CTkFrame(self.main, fg_color=BACKGROUND)
        grid.pack(padx=20, pady=10, fill="x")
        for col in range(3):
            grid.grid_columnconfigure(col, weight=1)
        for idx,(lbl,val) in enumerate(cards):
            c = ctk.CTkFrame(grid, fg_color="white", corner_radius=8)
            c.grid(row=idx//3, column=idx%3, padx=10, pady=10, sticky="nsew")
            ctk.CTkLabel(c, text=lbl, font=CTkFont(size=14)).pack(pady=(8,2))
            ctk.CTkLabel(c, text=str(val), font=CTkFont(size=20, weight="bold"),
                         text_color="#2d7fff").pack(pady=(0,8))

        # Attendance chart
        fig,ax = plt.subplots(figsize=(7,2))
        days = [(date.today() - timedelta(i)).strftime("%a") for i in range(6,-1,-1)]
        vals = [sum(1 for mbr in manager.members.values()
                   if (date.today()-timedelta(i)).isoformat() in mbr.attendance_log)
                for i in range(6,-1,-1)]
        ax.bar(days, vals, color="#2d7fff")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        canvas = FigureCanvasTkAgg(fig, self.main)
        canvas.get_tk_widget().pack(fill="x", padx=20, pady=(10,20))

    # --- MEMBERS TAB (FULL CRUD + Intuitive UI) ---

    def show_members(self):
        self.clear()
        frm = ctk.CTkFrame(self.main, fg_color=BACKGROUND)
        frm.pack(fill="both", expand=True, padx=20, pady=20)

        # ── Register New Member ──
        reg = ctk.CTkFrame(frm, fg_color="white", corner_radius=8)
        reg.pack(fill="x", pady=(0,15))
        ctk.CTkLabel(reg, text="Register New Member",
                     font=CTkFont(size=16, weight="bold")
                    ).pack(anchor="w", padx=10, pady=(10,5))

        self.reg_entries = {}
        for fld in ("Member ID","Name","Age"):
            row = ctk.CTkFrame(reg, fg_color="#f7f7f7", corner_radius=6)
            row.pack(fill="x", padx=10, pady=3)
            ctk.CTkLabel(row, text=fld, width=100).pack(side="left", padx=5)
            ent = ctk.CTkEntry(row, placeholder_text=fld)
            ent.pack(side="left", fill="x", expand=True, padx=5)
            self.reg_entries[fld] = ent

        ctk.CTkButton(reg, text="Register Member", fg_color="#2d7fff",
                      command=self._register_member).pack(pady=10)

        # ── Manage Existing Member ──
        upd = ctk.CTkFrame(frm, fg_color="white", corner_radius=8)
        upd.pack(fill="x", pady=(0,15))
        ctk.CTkLabel(upd, text="Manage Existing Member",
                     font=CTkFont(size=16, weight="bold")
                    ).grid(row=0, column=0, columnspan=4, sticky="w", padx=10, pady=(10,5))

        # Configure grid columns to expand
        for c in range(6):
            upd.grid_columnconfigure(c, weight=1, uniform="mgr")

        # Row 1: labels and controls
        member_ids = list(manager.members.keys()) or [""]
        self.sel_member = ctk.StringVar(value=member_ids[0])
        ctk.CTkLabel(upd, text="Member:").grid(row=1, column=0, sticky="e", padx=5)
        ctk.CTkOptionMenu(upd, values=member_ids, variable=self.sel_member
                         ).grid(row=1, column=1, sticky="we", padx=5)

        ctk.CTkButton(upd, text="🗑 Delete",
                      fg_color="#d9534f", command=self._delete_member
                     ).grid(row=1, column=2, sticky="we", padx=5)

        plan_ids = ["N/A"] + list(manager.workout_plans.keys())
        self.sel_plan = ctk.StringVar(value="N/A")
        ctk.CTkLabel(upd, text="Plan:").grid(row=1, column=3, sticky="e", padx=5)
        ctk.CTkOptionMenu(upd, values=plan_ids, variable=self.sel_plan
                         ).grid(row=1, column=4, sticky="we", padx=5)

        ctk.CTkButton(upd, text="Update Plan", fg_color="#2d7fff",
                      command=self._update_member_plan
                     ).grid(row=1, column=5, sticky="we", padx=5)

        # ── Members Table ──
        cols = ("ID", "Name", "Age", "Plan")
        tree = self._make_table(frm, cols)
        for mbr in manager.members.values():
            pid = mbr.workout_plan.plan_id if mbr.workout_plan else "N/A"
            tree.insert("", "end",
                        values=(mbr.member_id, mbr.name, mbr.age, pid))

    def _register_member(self):
        mid = self.reg_entries["Member ID"].get().strip()
        name = self.reg_entries["Name"].get().strip()
        age = self.reg_entries["Age"].get().strip()
        if not (mid and name and age.isdigit()):
            return CTkMessagebox(title="Error",
                                 message="Please fill out all fields correctly.")
        msg = manager.register_member(Member(mid, name, int(age),
                                             date.today().isoformat()))
        manager.save_to_file(DATA_FILE)
        CTkMessagebox(message=msg)
        self.show_members()

    def _delete_member(self):
        mid = self.sel_member.get()
        if not mid:
            return CTkMessagebox(title="Error", message="No member selected.")
        if mid in manager.members:
            manager.members.pop(mid)
            manager.save_to_file(DATA_FILE)
            CTkMessagebox(message=f"Member {mid} deleted.")
        self.show_members()

    def _update_member_plan(self):
        mid = self.sel_member.get()
        plan = self.sel_plan.get()
        if not mid:
            return CTkMessagebox(title="Error", message="No member selected.")
        # Unassign or assign
        if plan == "N/A":
            manager.unassign_workoutplan(plan_id=None, member_id=mid)
        else:
            manager.assign_workoutplan(plan, mid)
        manager.save_to_file(DATA_FILE)
        CTkMessagebox(
            message=f"Member {mid}'s plan updated to {plan}.")
        self.show_members()

    # --- Workouts CRUD ---
    def show_workouts(self):
        self.clear()
        frm = ctk.CTkFrame(self.main, fg_color=BACKGROUND)
        frm.pack(fill="both", expand=True, padx=20, pady=20)

        # New plan form
        form = ctk.CTkFrame(frm, fg_color="white", corner_radius=8)
        form.pack(fill="x", pady=5)
        self.wf = {}
        for fld in ("Plan ID","Name","Focus","Exercises"):
            r = ctk.CTkFrame(form, fg_color="#f7f7f7", corner_radius=6)
            r.pack(fill="x", padx=5, pady=3)
            ctk.CTkLabel(r, text=fld, width=100).pack(side="left", padx=5)
            e = ctk.CTkEntry(r, placeholder_text=fld)
            e.pack(side="left", fill="x", expand=True, padx=5)
            self.wf[fld] = e
        ctk.CTkButton(form, text="Create Plan", fg_color="#2d7fff",
                      command=self._create_plan).pack(side="left", padx=5)
        ctk.CTkButton(form, text="🗑 Remove Plan", fg_color="#d9534f",
                      command=self._delete_plan).pack(side="right", padx=5)

        # Table with Assigned count
        cols = ("ID","Name","Focus","Assigned")
        tree = self._make_table(frm, cols)
        for p in manager.workout_plans.values():
            cnt = sum(1 for m in manager.members.values()
                      if m.workout_plan and m.workout_plan.plan_id == p.plan_id)
            tree.insert("", "end", values=(p.plan_id, p.name, p.focus_area, cnt or "0"))

    def _create_plan(self):
        e, ex = self.wf, []
        if e["Exercises"].get():
            ex = [x.strip() for x in e["Exercises"].get().split(",") if x.strip()]
        pid, nm, fc = e["Plan ID"].get().strip(), e["Name"].get().strip(), e["Focus"].get().strip()
        if not(pid and nm and fc and ex):
            return CTkMessagebox(message="Invalid plan data")
        manager.add_workoutplan(WorkoutPlan(pid, nm, fc, ex))
        manager.save_to_file(DATA_FILE)
        CTkMessagebox(message="Plan created!")
        self.show_workouts()

    def _delete_plan(self):
        pid = self.wf["Plan ID"].get().strip()
        if pid in manager.workout_plans:
            # unassign from members
            for m in manager.members.values():
                if m.workout_plan and m.workout_plan.plan_id == pid:
                    m.workout_plan = None
            manager.remove_workoutplan(pid)
            manager.save_to_file(DATA_FILE)
            CTkMessagebox(message=f"Plan {pid} removed.")
        self.show_workouts()

    # --- Attendance (point 2) ---
    def show_attendance(self):
        self.clear()
        frm = ctk.CTkFrame(self.main, fg_color=BACKGROUND)
        frm.pack(fill="both", expand=True, padx=20, pady=20)

        row = ctk.CTkFrame(frm, fg_color="white", corner_radius=8)
        row.pack(fill="x", pady=5)
        self.at_mid = ctk.CTkEntry(row, placeholder_text="Member ID")
        self.at_mid.pack(side="left", fill="x", expand=True, padx=5)
        self.at_date = DateEntry(row, date_pattern="yyyy-MM-dd")
        self.at_date.pack(side="left", padx=5)
        ctk.CTkButton(row, text="Log Attendance", fg_color="#2d7fff",
                      command=self._log_att).pack(side="left", padx=5)

        # Top attendees this week
        week = [(date.today()-timedelta(i)).isoformat() for i in range(7)]
        ranked = sorted(manager.members.values(),
                        key=lambda m: sum(d in m.attendance_log for d in week),
                        reverse=True)[:5]
        text = "Top This Week: " + ", ".join(f"{m.name} ({sum(d in m.attendance_log for d in week)})"
                                            for m in ranked)
        ctk.CTkLabel(frm, text=text, wraplength=APP_WIDTH-40).pack(pady=10)

    def _log_att(self):
        mid = self.at_mid.get().strip()
        dt  = self.at_date.get_date().isoformat()
        if not mid:
            return CTkMessagebox(message="Enter Member ID")
        manager.log_attendance(dt, mid)
        manager.save_to_file(DATA_FILE)
        CTkMessagebox(message="Attendance logged.")

    # --- Payments ---
    def show_payments(self):
        self.clear()
        frm = ctk.CTkFrame(self.main, fg_color=BACKGROUND)
        frm.pack(fill="both", expand=True, padx=20, pady=20)

    # Payment entry row 
        prow = ctk.CTkFrame(frm, fg_color="white", corner_radius=8)
        prow.pack(fill="x", pady=5)
        # Payment form fields
        self.pm_mid = ctk.CTkEntry(prow, placeholder_text="Member ID")
        self.pm_mid.pack(side="left", padx=5, fill="x", expand=True)
        self.pm_amt = ctk.CTkEntry(prow, placeholder_text="Amount")
        self.pm_amt.pack(side="left", padx=5, fill="x", expand=True)
        self.pm_date = DateEntry(prow, date_pattern="yyyy-MM-dd")
        self.pm_date.pack(side="left", padx=5)
        ctk.CTkButton(prow, text="Log Payment", fg_color="#2d7fff",
                      command=self._log_pay).pack(side="left", padx=5)


    # Rebuild table without images:
        cols = ("ID","Name","Last Payment","Status")
        tree = self._make_table(frm, cols)
        for mbr in manager.members.values():
            last = mbr.payment_log[-1][0] if mbr.payment_log else "None"
            paid_this_month = last.startswith(date.today().strftime("%Y-%m"))
            status = "Paid" if paid_this_month else "Overdue"
            tree.insert("", "end",
                        values=(mbr.member_id, mbr.name, last, status))

    def _log_pay(self):
        mid = self.pm_mid.get().strip()
        amt = self.pm_amt.get().strip()
        dt  = self.pm_date.get_date().isoformat()
        if not(mid and amt.replace('.','',1).isdigit()):
            return CTkMessagebox(message="Invalid input")
        manager.members[mid].add_payment(dt, float(amt))
        manager.save_to_file(DATA_FILE)
        CTkMessagebox(message="Payment logged.")
        self.show_payments()

    # --- Utility Table ---
    def _make_table(self, parent, cols):
        frm = ctk.CTkFrame(parent, fg_color=BACKGROUND)
        frm.pack(fill="both", expand=True, padx=5, pady=5)
        tree = ttk.Treeview(frm, columns=cols, show="headings", height=8)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center", width=int((APP_WIDTH-100)/len(cols)))
        sb = ttk.Scrollbar(frm, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        return tree
    
    def on_close(self):
        # Manually destroy any DateEntry widgets to cancel their after‑jobs
        # Walk through all children and if it’s a DateEntry, destroy it before quitting
        def _destroy_date_entries(widget):
            for child in widget.winfo_children():
                if isinstance(child, DateEntry):
                    try:
                        child._top_cal.after_cancel(child._validate_after_id)
                    except Exception:
                        pass
                    child.destroy()
                _destroy_date_entries(child)
        _destroy_date_entries(self)
        # Save everything before exit
        manager.save_to_file(DATA_FILE)  # Directly save using the manager
        # Stop the mainloop cleanly
        try:
            self.quit()
        except Exception:
            pass
        # Destroy the window and exit the process
        self.destroy()
        sys.exit(0)

if __name__ == '__main__':
    app = GymApp()
    app.mainloop()
    sys.exit(0)