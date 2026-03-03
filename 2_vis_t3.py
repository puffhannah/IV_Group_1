
import pandas as pd
import altair as alt

df = pd.read_csv("medical_clean_final.csv")

#made a dropdown bar so users can look at each condition separately.
dropdown_condition = alt.binding_select(
    options=[None, 'Diabetic', 'Cancer', 'Pneumonia'],
    labels=['All', 'Diabetic', 'Cancer', 'Pneumonia'],
    name='Conditions'
)
select_condition = alt.selection_point(
    fields=['condition'], bind=dropdown_condition, value=[{'condition': 'Diabetic'}]
)
#made radio buttons to switch data to focus on female, male and both
gender_radio = alt.binding_radio(

    options=[None,'female', 'male'], 
    labels=[ 'Both','female', 'male'],
    name='Gender:'
)
select_gender = alt.selection_point(
    fields=['gender'],
    bind=gender_radio

)
#age slider tool to have a range from 0-80 year old. it will be filtered to both facets.
age_slider = alt.binding_range(min=0, max=80, step=1, name="age scale")
select_age = alt.param(value=60, bind=age_slider)


# making a vertical line to show blood pressure threshold
bp_threshold = alt.Chart(df).mark_rule(
    color='red', strokeDash=[6, 3], size=2
).encode(
    x=alt.X('threshold:Q', scale=alt.Scale(domain=[70, 200])),
    tooltip=[alt.Tooltip('threshold:Q', title='High Blood Pressure')]
).transform_calculate(
    threshold='140'   
)
#scattor plot to show the data through colors and shapes
scatter = alt.Chart(df).mark_point(size=60,opacity=1.0, filled=True).encode(
    x=alt.X('blood_pressure:Q', scale=alt.Scale(domain=[70, 200])), #x-axis is blood pressure
    y=alt.Y('glucose_levels:Q', scale=alt.Scale(domain=[70, 200])),# y-axis is glucose levels both with range 70 to 200
    color=alt.condition(select_condition, alt.Color('condition:N'), alt.value('lightgray')),# having different colors associate with the conditions

    shape=alt.Shape('gender:N', scale=alt.Scale(domain=['female', 'male'], range=['square', 'circle'])),# shape associsated with gender
    tooltip=['condition', 'blood_pressure', 'glucose_levels', 'gender', 'age'],# all the values when hovering over point
).transform_filter(select_condition #tying my dropdown of conditions to plot
).transform_filter(select_gender #tying my radio buttons to scatter plot
).transform_filter(alt.datum.age >= select_age)#for my age slider

#combining my line threshold with my scatter plot
chart2 = alt.layer(
    scatter,
    bp_threshold,
).properties(width=500, height=500
).facet( #allowed me to show smoking and non-smoking sideby side.
    facet=alt.Facet('smoking_status:N', sort=['Non-Smoker', 'Smoker'], title='Smoking Status'),
    columns=2,
    title=alt.TitleParams(# my extra information labeled
        text='Blood Pressure vs Glucose Levels by Smoking Status',
        subtitle='* Elderly is defined as age 60+ | Red line = Hypertension (140)',
        subtitleColor='gray',
        subtitleFontSize=12,
        anchor='middle')
).add_params(select_gender, select_age, select_condition
).interactive()

chart2.show()
chart2.save('3_vis.html')