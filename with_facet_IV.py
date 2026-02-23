# import pandas as pd
# import altair as alt
# from altair.datasets import data
# df= pd.read_csv("medical_clean_final.csv")

# chart =alt.Chart(df).mark_circle(size=60).encode(
#     x='blood_pressure',
#     y='glucose_levels',
#     color='condition',
#     shape= 'gender',
#     tooltip=['condition', 'blood_pressure', 'glucose_levels', 'gender']
# ).interactive()
# #chart.show()
# chart.save("first_vis.html")


import pandas as pd
import altair as alt
from altair.datasets import data
df= pd.read_csv("medical_clean_final.csv")

dropdown_condition= alt.binding_select(
    options=[None,'Diabetic','Cancer','Pneumonia'],
    labels=['All','Diabetic','Cancer','Pneumonia'],
    name='Conditions'
)
select_condition= alt.selection_point(
    fields=['condition'], bind=dropdown_condition
)
gender_radio= alt.binding_radio(
    options=['female','male'],
    name='Gender:'
)
select_gender= alt.selection_point(
    fields=['gender'], bind=gender_radio
)
chart =alt.Chart(df).mark_point(size=80, opacity=1, filled=True).transform_calculate(
    age_group=alt.expr.if_(alt.datum.age< 30,'Under 30',alt.expr.if_(alt.datum.age<60,'30-59',alt.expr.if_(alt.datum.age<80,'60-79','80+')))
).encode(
    x= alt.X('blood_pressure', scale=alt.Scale(domain= [70,200])),
    y= alt.Y('glucose_levels', scale= alt.Scale(domain=[70,200])),
    color= alt.condition(select_condition,'condition:N',alt.value('black')),
    shape= alt.Shape('gender', scale= alt.Scale(domain=['female','male'], range=['square','circle'])),
    size= alt.Size('smoking_status:N',scale=alt.Scale(domain=['Non-Smoker','Smoker'], range=[60,150])),
    tooltip=['condition', 'blood_pressure', 'glucose_levels', 'gender','smoking_status'],
).transform_filter(select_condition
).transform_filter(select_gender
).properties(width=400,height=400
).facet(
    facet= alt.Facet('age_group:O',
    sort=['Under 30','30-59','50-79','80+'],
    title='Age Group'),
    columns=2,
    title=alt.TitleParams(
        text='Blood Pressure vs Glucose Levels by Age Group',
        subtitle='* Elderly is defined as age 60+',  
        subtitleColor='gray',
        subtitleFontSize=12,
        anchor='end')
).add_params(select_condition, select_gender
).transform_calculate(jitter = 'random()').interactive()
chart.show()
chart.save("facet_vis.html")
print(df['gender'].unique())



#alt.Chart(df).mar