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
chart =alt.Chart(df).mark_point(size=60, opacity=1, filled=True).encode(
    x= alt.X('blood_pressure', scale=alt.Scale(domain= [70,200])),
    y= alt.Y('glucose_levels', scale= alt.Scale(domain=[70,200])),
    color= alt.condition(select_condition,'condition',alt.value('black')),
    shape= alt.Shape('gender', scale= alt.Scale(domain=['female','male'], range=['square','circle'])),
    tooltip=['condition', 'blood_pressure', 'glucose_levels', 'gender'],
).transform_filter(select_condition
).transform_filter(select_gender
).properties(width=500,height=500
).add_params(select_condition, select_gender
).transform_calculate(jitter = 'random()').interactive()
chart.show()
chart.save("first_vis_drop.html")
print(df['gender'].unique())

#alt.Chart(df).mar