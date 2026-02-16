import pandas as pd
import altair as alt
from altair.datasets import data
df= pd.read_csv("medical_clean_final.csv")

chart =alt.Chart(df).mark_circle(size=60).encode(
    x='blood_pressure',
    y='glucose_levels',
    color='condition',
    shape= 'gender',
    tooltip=['condition', 'blood_pressure', 'glucose_levels', 'gender']
).interactive()
#chart.show()
chart.save("first_vis.html")
