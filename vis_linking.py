# import pandas as pd
# import altair as alt
# from altair.datasets import data
# df= pd.read_csv("medical_clean_final.csv")



# dropdown_condition = alt.binding_select(
#     options=[None, 'Diabetic', 'Cancer', 'Pneumonia'],
#     labels=['All', 'Diabetic', 'Cancer', 'Pneumonia'],
#     name='Conditions:'
# )
# select_condition = alt.selection_point(
#     fields=['condition'],
#     bind=dropdown_condition


# chart4 = alt.Chart(df).mark_point(opacity=1, filled=True).encode(
#     x=alt.X('age:Q', scale=alt.Scale(zero=False)),
#     y=alt.Y('blood_pressure:Q', scale=alt.Scale(zero=False)),
#     color=alt.Color('condition:N'),
#     shape=alt.Shape('gender:N', scale=alt.Scale(
#         domain=['female', 'male'],
#         range=['square', 'circle']
#     )),
#     tooltip=['condition', 'age', 'blood_pressure', 'gender']
# ).transform_filter(select_condition,)

# # TREND LINE
# trend = alt.Chart(df).mark_line(
#     color='red', strokeDash=[5, 3]
# ).encode(
#     x=alt.X('age:Q'),
#     y=alt.Y('mean(glucose_levels):Q')
# ).transform_filter(select_condition)

# # ← LAYER FIRST, THEN FACET
# detail_chart = alt.layer(
#     chart4, trend      # ← layer points and trend together
# ).properties(
#     width=250,
#     height=250
# ).facet(
#     facet=alt.Facet('smoking_status:N',
#         sort=['Non-Smoker', 'Smoker'],
#         title='Smoking Status'
#     ),
#     columns=2
# ).transform_calculate()

# detail_chart.show()
# detail_chart.save("t1_t2_t3_linked.html")

# # The key fix is the order:
# # ```
# # layer(points + trend)   ← layer FIRST
# #     .properties()       ← then properties
# #     .facet()            ← then facet LAST

# # DOES NOT WORK

import pandas as pd
import altair as alt
from altair.datasets import data
df= pd.read_csv("medical_clean_final.csv")

#hover = alt.selection_point(on='mouseover')

# #select_conditions= alt.selection_point(
#     fields=['blood_pressure','glucose_levels'],
    
#     bind=alt.binding_radio(
#     options=['blood_pressure','glucose_levels'],
#     name='Lab work'

bar_chart=alt.Chart(df).mark_point(opacity=0.7).encode(
    alt.X('glucose_levels:Q', bin=True, title='Glucose Levels'),
    alt.Y('count(age):Q', title='Count'),
    color= alt.Color('age:Q', scale=alt.Scale(domainMin=0,range=["#cfe2f3", "#08306b"])),
    tooltip=[
        alt.Tooltip('glucose_levels:Q', bin=True, title='Glucose Level'),
        alt.Tooltip('count(age):Q', title= 'Count'),
        alt.Tooltip('average(age):Q', title='avergae age'),
        #alt.Tooltip('blood_pressure:Q', title='Blood Pressure')
    ]

).properties(width= 450, height= 450
#).transform_filter(select_condition )#.add_params
).interactive()

bar_chart.show()
bar_chart.save('Age_vs_Glucose.html')


# radio = alt.selection_point(
#     fields=['metric'],
#     bind=alt.binding_radio(
#         options=['glucose_levels', 'blood_pressure'],
#         name='Select: '
#     ),
#     value=[{'metric': 'glucose_levels'}]
# )

# bar_chart = alt.Chart(df).transform_fold(
#     ['glucose_levels', 'blood_pressure'],
#     as_=['metric', 'value']
# ).transform_filter(
#     radio
# ).mark_circle(opacity=0.7).encode(
#     alt.X('value:Q', title='Value'),
#     alt.Y('count(age):Q', title='Count'),
#     color=alt.Color('age:Q', scale=alt.Scale(domainMin=0, range=["#cfe2f3", "#08306b"])),
#     tooltip=[
#         alt.Tooltip('value:Q', title='Value'),
#         alt.Tooltip('count(age):Q', title='Count'),
#         alt.Tooltip('average(age):Q', title='Average Age'),
#         alt.Tooltip('metric:N', title='Metric')
#     ]
# ).properties(
#     width=450,
#     height=450
# ).add_params(radio).interactive()

# bar_chart.show()
# bar_chart.save('Age_vs_Glucose_vs_bp.html')