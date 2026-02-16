import pandas as pd
import altair as alt
from altair.datasets import data
df= pd.read_csv("medical_clean_final.csv")

chart =alt.Chart(df).mark_point(size=30, opacity=0.5).encode(
    x= alt.X('blood_pressure', scale=alt.Scale(zero= False)),
    y= alt.Y('glucose_levels', scale= alt.Scale(zero= False)),
    color='condition',
    shape= alt.Shape('gender', scale= alt.Scale(domain=['female','male'], range=['square','circle'])),
    tooltip=['condition', 'blood_pressure', 'glucose_levels', 'gender']
).interactive()
#chart.show()
chart.save("first_vis.html")
print(df['gender'].unique())
