import pandas as pd
import plotly.io as pio
import plotly.express as px

# read in the data 
data = pd.read_csv("grades.csv")

# task 3 
modified_data = data
combined_col = []
for _, row in data.iterrows():
    semester = getattr(row, 'Semester')
    section = getattr(row, 'Section')
    new_val = ""
    new_val = new_val + "20" + semester[1:]
    if semester[0:1]=='F':
        new_val += "Fall"
    else:
        new_val += "Spring"
    new_val = new_val + "0" + str(section)
    combined_col.append(new_val)
combined_df = pd.DataFrame(combined_col)
# insert the combined column
modified_data.insert(0, "Class", combined_df)



# task 4
# rescale the score to [0,100]
def re_scale_0_100(attr,data):
    col = data.columns.get_loc(attr)
    new_attr = attr+"_0_100"
    min = data[attr].min()
    max = data[attr].max()
    # rescale the data based on max and min
    rescaled = (data[attr]-min)/(max-min)*100
    # insert the new column after the original column
    data.insert(col+1,new_attr,rescaled)
    return data

# calculate z based on all students
def re_scale_all_z(attr,data):
    col = data.columns.get_loc(attr)
    new_attr = attr+"_all_z"
    mean = data[attr].mean()
    std = data[attr].std()
    # formula used to calculate z
    z = (data[attr]-mean)/std
    # insert the new column after the original column
    data.insert(col+1, new_attr, z)
    return data

# calculate the mean and standard deviation for each semester based on the given attribute
def find_metrics(attr, data):
    metrics = {}
    semesters = ['F16','S17','F17','S18','F18']
    for semester in semesters:
        filtered = data[data['Semester'] == semester]
        mean = filtered[attr].mean()
        std = filtered[attr].std()
        # store the metrics in a dictionary, key = semester, value  is a list with first element as mean and second element as standard deviation.
        metrics[semester] = [mean, std]
    return metrics

# calculate z based on students from the same semester
def re_scale_semester_z(attr,data,metrics):
    col = data.columns.get_loc(attr)
    new_attr = attr+"_semester_z"
    new_col = []
    for _, row in data.iterrows():
        semester = getattr(row, 'Semester') 
        score = getattr(row, attr) 
        mean = metrics[semester][0]
        std = metrics[semester][1]
        z = (score-mean)/std
        new_col.append(z)
    new_col_df = pd.DataFrame(new_col,columns=[new_attr])
    # insert the new column after the original column
    data.insert(col+1, new_attr, new_col_df)
    return data


attributes = ['Homework 1', 'Homework 2', 'Homework 3',
              'Homework 4', 'Homework 5', 'Peer Evaluations',
              'Bonus','Quiz 01','Quiz 02','Quiz 03','Quiz 04',
              'Quiz 05','Quiz 06','Quiz 07','Quiz 08','Quiz 09',
              'Quiz 10', 'Quiz 11', 'Quiz 12','Final Exam', 'Total Score']

for attribute in attributes:
    modified_data = re_scale_0_100(attribute, modified_data)
    modified_data = re_scale_all_z(attribute, modified_data)
    # calculate the mean and standard deviation for each semester 
    metrics = find_metrics(attribute, modified_data)
    modified_data = re_scale_semester_z(attribute, modified_data, metrics)

# export the modified data
modified_data.to_csv('modified_grades.csv', index=False)


# task 5 
all = data
print(all.mean())
print(all.std())
# find 5 number summary
print(all.describe().loc[['min', '25%', '50%', '75%', 'max']].transpose())


# task 6
# three box plots
fig = px.box(data,  x='Homework 1',
             title='Homework 1 distribution')
fig.show()

fig = px.box(data,  x='Homework 2',
             title='Homework 2 distribution')
fig.show()

fig = px.box(data,  x='Homework 3',
             title='Homework 3 distribution')
fig.show()

# three histograms plots
fig = px.histogram(data,  x='Peer Evaluations',
             title='Peer Evaluations distribution')
fig.show()

fig = px.histogram(data,  x='Final Exam',
             title='Final Exam distribution')
fig.show()

fig = px.histogram(data,  x='Letter Grade',
                   title='Letter Grade distribution')
fig.show()

# three scatter plots
fig = px.scatter(data, x="Peer Evaluations", y="Total Score", title='Peer Evaluations vs Total Score')
fig.show()

fig = px.scatter(data, x="Final Exam", y="Total Score",
                 title='Final Exam vs Total Score')
fig.show()

fig = px.scatter(data, x="Semester", y="Total Score",
                 title='Semester vs Total Score')
fig.show()

# one line plot with derived attribute
dfmean = data.groupby('Semester')[
    ['Total Score']].mean().reset_index()
fig = px.line(dfmean, x='Semester', y='Total Score', title='Average Total Score vs Semester')
fig.show()

 
