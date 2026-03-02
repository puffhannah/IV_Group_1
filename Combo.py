import pandas as pd
import altair as alt

alt.data_transformers.disable_max_rows()

df = pd.read_csv("medical_clean_final.csv")

df["age"] = pd.to_numeric(df["age"], errors="coerce")
df["blood_pressure"] = pd.to_numeric(df["blood_pressure"], errors="coerce")
df["glucose_levels"] = pd.to_numeric(df["glucose_levels"], errors="coerce")
df["gender"] = df["gender"].astype(str).str.strip().str.lower()
df = df.dropna(subset=["age", "gender", "blood_pressure", "glucose_levels"]).copy()

#  Measure dropdown
measure_dropdown = alt.binding_select(
    options=["blood_pressure", "glucose_levels"],
    labels=["Blood Pressure", "Glucose Levels"],
    name="Measure: "
)
measure = alt.param(name="measure", value="blood_pressure", bind=measure_dropdown)


# Base: mean per age per gender 
base = (
    alt.Chart(df)
    .add_params(measure)
    .transform_calculate(
        age_int="toNumber(round(datum.age))",
        selected_value="toNumber(datum[measure])"
    )
    .transform_aggregate(
        mean_value="mean(selected_value)",
        groupby=["age_int", "gender"]
    )
)

# LOESS smooth -> smooth_value 
smooth_base = base.transform_loess(
    "age_int", "mean_value",
    groupby=["gender"],
    bandwidth=0.35,
    as_=["age_int", "smooth_value"]
)

smooth = smooth_base.mark_line(strokeWidth=4).encode(
    x="age_int:Q",
    y="smooth_value:Q"
)

faint_points = base.mark_circle(size=30, opacity=0.18).encode(
    x="age_int:Q",
    y="mean_value:Q"
)


panzoom = alt.selection_interval(bind="scales")


hover = alt.selection_point(
    fields=["age_int"],
    nearest=True,
    on="mousemove",
    empty=False,
    clear="mouseout"
)


selectors = (
    smooth_base.mark_point(opacity=0)
    .encode(x="age_int:Q", y="smooth_value:Q")
    .add_params(hover)
)


rule = (
    alt.Chart(df)
    .transform_calculate(age_int="toNumber(round(datum.age))")
    .mark_rule(color="red", strokeWidth=2)
    .encode(x="age_int:Q")
    .transform_filter(hover)
)


highlight = (
    smooth_base.mark_circle(size=120)
    .encode(
        x="age_int:Q",
        y="smooth_value:Q",
        tooltip=[
            alt.Tooltip("age_int:Q", title="Age"),
            alt.Tooltip("gender:N", title="Gender"),
            alt.Tooltip("smooth_value:Q", title="On-line value", format=".2f"),
        ]
    )
    .transform_filter(hover)
)


labels = (
    smooth_base.mark_text(dx=8, dy=-10, fontSize=13)
    .encode(
        x="age_int:Q",
        y="smooth_value:Q",
        text=alt.Text("smooth_value:Q", format=".2f")
    )
    .transform_filter(hover)
)

chart = (
    (smooth + faint_points + selectors + rule + highlight + labels)
    .add_params(panzoom)  
    .encode(
        x=alt.X(
            "age_int:Q",
            title="age",
            axis=alt.Axis(grid=True, tickMinStep=1)
        ),
        y=alt.Y("smooth_value:Q", title=None, scale=alt.Scale(zero=False)),
        color=alt.Color(
            "gender:N",
            title="gender",
            sort=["female", "male"],
            scale=alt.Scale(domain=["female", "male"], range=["#ff5ca8", "#3a78b2"]),
            legend=alt.Legend(orient="right")
        )
    )
    .properties(
        width=900,
        height=500,
        title={
            "text": "Glucose Levels and Blood Pressure trends",
            "subtitle": "Lines are means",
            "anchor": "middle"
        },
        padding={"top": 30, "left": 10, "right": 10, "bottom": 60}
    )
    .configure(background="white")
    .configure_view(stroke=None)
    .configure_axis(gridColor="#d9d9d9", domainColor="#888", tickColor="#888")
)

chart.save("combo_line.html", embed_options={"actions": True})
print("Saved to combo_line.html")