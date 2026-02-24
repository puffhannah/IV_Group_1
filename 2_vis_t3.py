
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
age_slider= alt.binding_range(
    min= 0,
    max= 80,
    step=1,
    name= "age scale",
)
select_age= alt.param(
    value=60,
    bind=age_slider
)
chart2 =alt.Chart(df).mark_point(size=60, opacity=1, filled=True).encode(
    x= alt.X('blood_pressure', scale=alt.Scale(domain= [70,200])),
    y= alt.Y('glucose_levels', scale= alt.Scale(domain=[70,200])),
    color= alt.condition(select_condition,'condition',alt.value('black')),
    shape= alt.Shape('gender', scale= alt.Scale(domain=['female','male'], range=['square','circle'])),
    tooltip=['condition', 'blood_pressure', 'glucose_levels', 'gender','age'],
).transform_filter(select_condition
).transform_filter(select_gender
).transform_filter( alt.datum.age >=select_age
).properties(width=500,height=500
).facet(
    facet= alt.Facet('smoking_status',
    sort=['Non-Smoker','Smoker'],
    title='Smoking_status'),
    columns= 2,
    title=alt.TitleParams(
        text='Blood Pressure vs Glucose Levels by Smoking Status',
        subtitle='* Elderly is defined as age 60+',  
        subtitleColor='gray',
        subtitleFontSize=12,
        anchor='end')
).add_params(select_condition, select_gender, select_age
).transform_calculate(jitter = 'random()').interactive()
chart2.show()
chart2.save("3_vis_drop.html")
print(df['gender'].unique())
