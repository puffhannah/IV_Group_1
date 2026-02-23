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
chart =alt.Chart(df).mark_point(size=10, opacity=0.8).encode(
    x= alt.X('blood_pressure'), #scale=alt.Scale(zero= False)),
    y= alt.Y('glucose_levels'), #scale= alt.Scale(zero= False)),
    color= alt.condition(select_condition,'condition',alt.value('lightgray')),
    shape= alt.Shape('gender', scale= alt.Scale(domain=['female','male'], range=['square','circle'])),
    tooltip=['condition', 'blood_pressure', 'glucose_levels', 'gender'],
    opacity=alt.condition(select_condition, alt.value(0.7), alt.value(0.05))
).add_params(select_condition
).transform_calculate(jitter = 'random()').interactive()
chart.show()
chart.save("first_vis_drop.html")
print(df['gender'].unique())
