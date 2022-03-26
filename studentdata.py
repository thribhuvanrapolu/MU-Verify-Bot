import pandas as pd



#soe21.csv
#creating dataframe and read the csv file
soe21=pd.read_csv('soe21.csv')
#removes empty columns
soe21.drop(soe21.iloc[:, 5:18], inplace = True, axis = 1)
#creates a new column for branch
soe21['branch'] = soe21.apply(lambda row: str(row.lastname)+"-"+str(row.username[5:8]), axis=1)
#remove last name and id
soe21.drop(soe21.columns[[0,4]],axis=1,inplace= True)

#write for other files in same above format
#soe20.csv

#soe19.csv

#soe18.csv



#combining all csv files data into one dataframe named all_student data
frames=[soe21] #add the above dataframes like frames=[soe21,soe20,soe19.....]
all_student_data=pd.concat(frames)

#extracting branches which doesnt contain duplicate branches
temp_branch=all_student_data['branch'].tolist()
branch=[]
for i in temp_branch:
    if i not in branch:
        branch.append(i)

