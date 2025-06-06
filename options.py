import pandas as pd
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpBinary

# Load your Excel file
df = pd.read_excel(r"C:\Users\philc\OneDrive\Desktop\Exports\Student option choices.xlsx", sheet_name="Option Allocation")

# Reshape to long format
student_rows = []
for idx, row in df.iterrows():
    student = row["Name (first name and surname)"]
    for col in ['A', 'B', 'C']:
        student_rows.append({
            'Student': student,
            'Column': col,
            'First': row[f"{col} 1st"],
            'Reserve': row[f"{col} reserve"]
        })

long_df = pd.DataFrame(student_rows)

# Subject limits
raw_limits = {
    "3D": 20, "Art": 24, "Computing": 30, "Dance": 32,
    "Design & Technology (Product Design)": 20,
    "Design & Technology (Textiles)": 20,
    "Drama": 32, "French": 32, "Geography": 32,
    "Health & Fitness": 50, "History": 32,
    "Hospitality & Catering": 20, "Latin": 32,
    "Music Technology": 14, "RE": 32, "Spanish": 32
}

# Subjects by column
column_subjects = {
    'A': ['Dance', 'Design & Technology (Product Design)', 'Geography', 'History', 'RE', 'Spanish'],
    'B': ['Art', 'Health & Fitness', 'History', 'Hospitality & Catering', 'Latin', 'Music Technology'],
    'C': ['3D', 'Computing', 'Design & Technology (Textiles)', 'Drama', 'French', 'Geography']
}

# Model
model = LpProblem("Student_Option_Assignment", LpMaximize)

# Decision variables
assign_vars = {}
for i, row in long_df.iterrows():
    key_first = (row['Student'], row['Column'], 'first')
    key_reserve = (row['Student'], row['Column'], 'reserve')
    assign_vars[key_first] = LpVariable(f"{row['Student']}_{row['Column']}_first", cat=LpBinary)
    assign_vars[key_reserve] = LpVariable(f"{row['Student']}_{row['Column']}_reserve", cat=LpBinary)

# Objective
model += lpSum([
    2 * assign_vars[(row['Student'], row['Column'], 'first')] +
    1 * assign_vars[(row['Student'], row['Column'], 'reserve')]
    for _, row in long_df.iterrows()
])

# One subject per column
for student in long_df['Student'].unique():
    for col in ['A', 'B', 'C']:
        model += (
            assign_vars.get((student, col, 'first'), 0) +
            assign_vars.get((student, col, 'reserve'), 0) <= 1
        )

# Capacity constraints
for column, subjects in column_subjects.items():
    for subject in subjects:
        cap = raw_limits.get(subject, 999)
        model += lpSum([
            assign_vars[(row['Student'], row['Column'], 'first')]
            for _, row in long_df.iterrows()
            if row['Column'] == column and row['First'] == subject
        ]) + lpSum([
            assign_vars[(row['Student'], row['Column'], 'reserve')]
            for _, row in long_df.iterrows()
            if row['Column'] == column and row['Reserve'] == subject
        ]) <= cap

# Add priority subject constraint
priority_subjects = df.set_index("Name (first name and surname)")["Priority Subject"].to_dict()

for student in long_df['Student'].unique():
    priority = priority_subjects.get(student)
    if priority:
        # Find all possible assignments of that priority subject
        relevant_assignments = []
        for col in ['A', 'B', 'C']:
            row_mask = (long_df['Student'] == student) & (long_df['Column'] == col)
            for i, row in long_df[row_mask].iterrows():
                if row['First'] == priority:
                    relevant_assignments.append(assign_vars[(student, col, 'first')])
                if row['Reserve'] == priority:
                    relevant_assignments.append(assign_vars[(student, col, 'reserve')])
        # Ensure at least one of them is assigned
        if relevant_assignments:
            model += lpSum(relevant_assignments) >= 1

# Conflict constraints
for student in long_df['Student'].unique():
    art_3d = []
    pd_txt = []
    for col in ['A', 'B', 'C']:
        first = df.loc[df["Name (first name and surname)"] == student, f"{col} 1st"].values[0]
        reserve = df.loc[df["Name (first name and surname)"] == student, f"{col} reserve"].values[0]
        if first in ['Art', '3D']:
            art_3d.append(assign_vars[(student, col, 'first')])
        if reserve in ['Art', '3D']:
            art_3d.append(assign_vars[(student, col, 'reserve')])
        if first in ['Design & Technology (Textiles)', 'Design & Technology (Product Design)']:
            pd_txt.append(assign_vars[(student, col, 'first')])
        if reserve in ['Design & Technology (Textiles)', 'Design & Technology (Product Design)']:
            pd_txt.append(assign_vars[(student, col, 'reserve')])
    model += lpSum(art_3d) <= 1
    model += lpSum(pd_txt) <= 1

# No repeated subjects across columns per student
for student in long_df['Student'].unique():
    all_subjects = set(long_df[long_df['Student'] == student]['First']) | set(long_df[long_df['Student'] == student]['Reserve'])
    for subject in all_subjects:
        subject_assignments = []
        for col in ['A', 'B', 'C']:
            row_mask = (long_df['Student'] == student) & (long_df['Column'] == col)
            for i, row in long_df[row_mask].iterrows():
                if row['First'] == subject:
                    subject_assignments.append(assign_vars[(student, col, 'first')])
                if row['Reserve'] == subject:
                    subject_assignments.append(assign_vars[(student, col, 'reserve')])
        if subject_assignments:
            model += lpSum(subject_assignments) <= 1

# Solve
model.solve()

# Results
results = []
for _, row in long_df.iterrows():
    student, column = row['Student'], row['Column']
    first, reserve = row['First'], row['Reserve']
    if assign_vars[(student, column, 'first')].varValue == 1:
        results.append({'Student': student, 'Column': column, 'Assigned': first, 'Type': 'First'})
    elif assign_vars[(student, column, 'reserve')].varValue == 1:
        results.append({'Student': student, 'Column': column, 'Assigned': reserve, 'Type': 'Reserve'})
    else:
        results.append({'Student': student, 'Column': column, 'Assigned': None, 'Type': 'Unassigned'})

assignments_df = pd.DataFrame(results)
assignments_df.to_excel("Option_Assignments_Output.xlsx", index=False)
print("Assignment complete. Results saved to 'Option_Assignments_Output.xlsx'.")
