import csv
import random
import os

# Configuration
NUM_STUDENTS = 50
OUTPUT_FILE = "../data/Students_grading.csv"

# Random Seeds
random.seed(42)

def generate_data():
    data = []
    
    schools = ['GP', 'MS']
    sexes = ['F', 'M']
    addresses = ['U', 'R']
    famsizes = ['LE3', 'GT3']
    pstatuses = ['T', 'A']
    m_jobs = ['teacher', 'health', 'services', 'at_home', 'other']
    f_jobs = ['teacher', 'health', 'services', 'at_home', 'other']
    reasons = ['home', 'reputation', 'course', 'other']
    guardians = ['mother', 'father', 'other']
    yes_no = ['yes', 'no']

    # Header
    header = [
        'id', 'school', 'sex', 'age', 'address', 'famsize', 'Pstatus',
        'Medu', 'Fedu', 'Mjob', 'Fjob', 'guardian',
        'studytime', 'failures', 'schoolsup', 'famsup', 'paid', 'activities',
        'nursery', 'higher', 'internet', 'romantic', 'famrel', 'freetime',
        'goout', 'Dalc', 'Walc', 'health', 'absences', 'participation',
        'Note_Maths_T1', 'Note_Maths_T2', 
        'Note_Physique_T1', 'Note_Physique_T2',
        'Note_Arabe_T1', 'Note_Arabe_T2',
        'G1', 'G2', 'G3'
    ]

    for i in range(NUM_STUDENTS):
        student = {}
        
        # Identity
        student['id'] = i + 1
        student['school'] = random.choice(schools)
        student['sex'] = random.choice(sexes)
        student['age'] = random.randint(15, 22)
        student['address'] = random.choice(addresses)
        student['famsize'] = random.choice(famsizes)
        student['Pstatus'] = random.choice(pstatuses)
        
        # Parents
        student['Medu'] = random.randint(0, 4)
        student['Fedu'] = random.randint(0, 4)
        student['Mjob'] = random.choice(m_jobs)
        student['Fjob'] = random.choice(f_jobs)
        student['guardian'] = random.choice(guardians)
        
        # Social
        student['studytime'] = random.randint(1, 4)
        # Failures: 80% have 0, others 1-3
        student['failures'] = 0 if random.random() > 0.2 else random.randint(1, 3)
        student['schoolsup'] = random.choice(yes_no)
        student['famsup'] = random.choice(yes_no)
        student['paid'] = random.choice(yes_no)
        student['activities'] = random.choice(yes_no)
        student['nursery'] = random.choice(yes_no)
        student['higher'] = random.choice(yes_no)
        student['internet'] = random.choice(yes_no)
        student['romantic'] = random.choice(yes_no)
        student['famrel'] = random.randint(1, 5)
        student['freetime'] = random.randint(1, 5)
        student['goout'] = random.randint(1, 5)
        student['Dalc'] = random.randint(1, 5)
        student['Walc'] = random.randint(1, 5)
        student['health'] = random.randint(1, 5)
        student['absences'] = int(random.expovariate(1/4)) # Poisson-ish
        
        # New Feature: Participation
        student['participation'] = random.randint(1, 5)

        # Grades (Correlated somewhat)
        # Base ability (Normal distribution around 12)
        ability = random.gauss(12, 3)
        
        # Adjust by failures (negative impact)
        ability -= student['failures'] * 2
        
        # Adjust by studytime (positive impact)
        ability += (student['studytime'] - 2) * 0.5
        
        # Generate Subject Grades (Math, Physics, Arabic)
        def get_grade(base_ability, noise=2):
            g = int(random.gauss(base_ability, noise))
            return max(0, min(20, g))

        student['Note_Maths_T1'] = get_grade(ability)
        student['Note_Maths_T2'] = get_grade(ability)
        
        student['Note_Physique_T1'] = get_grade(ability - 1)
        student['Note_Physique_T2'] = get_grade(ability - 1)
        
        student['Note_Arabe_T1'] = get_grade(ability + 1)
        student['Note_Arabe_T2'] = get_grade(ability + 1)
        
        # Calculate Main Grades G1, G2
        # Simple average of the 3 subjects
        student['G1'] = round((student['Note_Maths_T1'] + student['Note_Physique_T1'] + student['Note_Arabe_T1']) / 3, 1)
        student['G2'] = round((student['Note_Maths_T2'] + student['Note_Physique_T2'] + student['Note_Arabe_T2']) / 3, 1)
        
        # Final Grade G3 (highly correlated with G2)
        student['G3'] = get_grade(student['G2'], noise=1.5)
        
        data.append(student)

    # Save to CSV
    if not os.path.exists('data'):
        os.makedirs('data')
        
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=header, delimiter=';')
        writer.writeheader()
        writer.writerows(data)
        
    print(f"✅ Generated {NUM_STUDENTS} students in {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_data()
