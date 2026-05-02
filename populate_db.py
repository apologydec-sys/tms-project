import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tms_project.settings')
django.setup()

from core.models import Department, Subject

def populate():
    departments = [
        "IT",
        "Plumbing",
        "Automechanics",
        "Building and Construction",
        "Catering",
        "Electricals",
        "Mechanical Engineering",
        "Fashion"
    ]
    
    # Ghanaian technical high school base subjects mapped to generic departments or core subjects
    subjects_data = {
        "IT": ["Information Technology", "Computer Networking", "Database Administration", "Core Math", "English Language"],
        "Plumbing": ["Pipe Fitting", "Water Supply Systems", "Sanitary Appliances", "Core Math", "English Language"],
        "Automechanics": ["Engine Repair", "Vehicle Diagnostics", "Automotive Electricity", "Core Math", "Integrated Science"],
        "Building and Construction": ["Block Laying", "Carpentry", "Site Management", "Core Math", "Integrated Science"],
        "Catering": ["Food preparation", "Food and Beverage Service", "Nutrition", "English Language", "Social Studies"],
        "Electricals": ["Electrical Wiring", "Circuit Design", "Power Systems", "Core Math", "Integrated Science"],
        "Mechanical Engineering": ["Machine Design", "Thermodynamics", "Manufacturing Processes", "Core Math", "Integrated Science"],
        "Fashion": ["Garment Construction", "Fashion Design", "Textiles", "Pattern Drafting", "Core Math", "English Language"]
    }

    for dept_name in departments:
        dept, created = Department.objects.get_or_create(name=dept_name)
        if created:
            print(f"Created department: {dept_name}")
        
        if dept_name in subjects_data:
            for subj_name in subjects_data[dept_name]:
                subj, subj_created = Subject.objects.get_or_create(name=subj_name, department=dept)
                if subj_created:
                    print(f"  Created subject: {subj_name} for {dept_name}")

if __name__ == '__main__':
    populate()
    print("Database populated successfully!")
