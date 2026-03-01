
# import pandas as pd
# import altair as alt
# from altair.datasets import data
# df= pd.read_csv("medical_clean_final.csv")

 

# dropdown_condition= alt.binding_select( 
#  options=[None,'Diabetic','Cancer','Pneumonia'], 
#  labels=['All','Diabetic','Cancer','Pneumonia'],
#  name='Conditions' 

# ) 
# select_condition= alt.selection_point( 
# fields=['condition'], bind=dropdown_condition, value=[{'condition':'Diabetic'}]
# ) 

# gender_radio= alt.binding_radio( 
#     options=['female','male'], 
#     labels=['female','male'],
#     name='Gender:' 
# ) 


# linked_selection= alt.selection_point(
#     fields=['condition'],
#     on='click',
#     clear= 'dbclick')




# chart2 = alt.layer(
#     alt.Chart(df).mark_point(size=60, opacity=1, filled=True).encode(
#         x=alt.X('blood_pressure', scale=alt.Scale(domain=[70, 200])),
#         y=alt.Y('glucose_levels', scale=alt.Scale(domain=[70, 200])),
#         color=alt.condition(linked_selection, alt.Color('condition:N'), alt.value('lightgray')),
#         opacity=alt.condition(linked_selection, alt.value(1.0), alt.value(0.15)),
#         size=alt.condition(linked_selection, alt.value(100), alt.value(40)),
#         shape=alt.Shape('gender', scale=alt.Scale(domain=['female', 'male'], range=['square', 'circle'])),
#         tooltip=['condition', 'blood_pressure', 'glucose_levels', 'gender', 'age'],

#     ).transform_filter(select_condition    
#     ).transform_filter(select_gender         
#     ).transform_filter(alt.datum.age >= select_age),  

#     #mean_lines,    
#     #mean_lines_y,
#     bp_threshold, 


# ).properties(width=500, height=500
# ).facet(
#     facet=alt.Facet('smoking_status', sort=['Non-Smoker', 'Smoker'], title='Smoking_status'),
#     columns=2,
#     data= df,
#     title=alt.TitleParams(
#         text='Blood Pressure vs Glucose Levels by Smoking Status',
#         subtitle='* Elderly is defined as age 60+',
#         subtitleColor='gray',
#         subtitleFontSize=12,
#         anchor='end')
# ).add_params(select_gender, select_age, linked_selection,select_condition
# ).transform_calculate(jitter='random()').interactive()

# chart2.show()
# chart2.save('3_vis_drop.html')
# print(df['smoking_status'].value_counts())
# print(df['gender'].value_counts())

import pandas as pd
import altair as alt

df = pd.read_csv("medical_clean_final.csv")

dropdown_condition = alt.binding_select(
    options=[None, 'Diabetic', 'Cancer', 'Pneumonia'],
    labels=['All', 'Diabetic', 'Cancer', 'Pneumonia'],
    name='Conditions'
)
select_condition = alt.selection_point(
    fields=['condition'], bind=dropdown_condition, value=[{'condition': 'Diabetic'}]
)

gender_radio = alt.binding_radio(
    options=['female', 'male'],
    labels=['female', 'male'],
    name='Gender:'
)
select_gender = alt.selection_point(
    fields=['gender'], bind=gender_radio
)

age_slider = alt.binding_range(min=0, max=80, step=1, name="age scale")
select_age = alt.param(value=60, bind=age_slider)

linked_selection = alt.selection_point(
    fields=['condition'], on='click', clear='dblclick'
)

# mean_lines = alt.Chart(df).mark_rule(strokeDash=[4, 4], size=2, color='orange').encode(
#     x=alt.X('mean(blood_pressure):Q'),
#     tooltip=[alt.Tooltip('mean(blood_pressure):Q', title='Mean BP')]
# ).transform_filter(alt.datum.condition == 'Diabetic')

# mean_lines_y = alt.Chart(df).mark_rule(strokeDash=[4, 4], size=2, color='orange').encode(
#     y=alt.Y('mean(glucose_levels):Q'),
#     tooltip=[alt.Tooltip('mean(glucose_levels):Q', title='Mean Glucose')]
# ).transform_filter(alt.datum.condition == 'Diabetic')


bp_threshold = alt.Chart(df).mark_rule(
    color='red', strokeDash=[6, 3], size=2
).encode(
    x=alt.X('threshold:Q', scale=alt.Scale(domain=[70, 200])),
    tooltip=[alt.Tooltip('threshold:Q', title='High Blood Pressure')]
).transform_calculate(
    threshold='140'   
)

scatter = alt.Chart(df).mark_point(size=60, filled=True).encode(
    x=alt.X('blood_pressure:Q', scale=alt.Scale(domain=[70, 200])),
    y=alt.Y('glucose_levels:Q', scale=alt.Scale(domain=[70, 200])),
    color=alt.condition(linked_selection, alt.Color('condition:N'), alt.value('lightgray')),
    opacity=alt.condition(linked_selection, alt.value(1.0), alt.value(0.15)),
    size=alt.condition(linked_selection, alt.value(100), alt.value(40)),
    shape=alt.Shape('gender:N', scale=alt.Scale(domain=['female', 'male'], range=['square', 'circle'])),
    tooltip=['condition', 'blood_pressure', 'glucose_levels', 'gender', 'age'],
).transform_filter(select_condition
).transform_filter(select_gender
).transform_filter(alt.datum.age >= select_age)

chart2 = alt.layer(
    scatter,
    #mean_lines,
    #mean_lines_y,
    bp_threshold,
).properties(width=500, height=500
).facet(
    facet=alt.Facet('smoking_status:N', sort=['Non-Smoker', 'Smoker'], title='Smoking Status'),
    columns=2,
    title=alt.TitleParams(
        text='Blood Pressure vs Glucose Levels by Smoking Status',
        subtitle='* Elderly is defined as age 60+ | Red line = Hypertension (140)',
        subtitleColor='gray',
        subtitleFontSize=12,
        anchor='end')
).add_params(select_gender, select_age, linked_selection, select_condition
).interactive()

chart2.show()
chart2.save('3_vis.html')