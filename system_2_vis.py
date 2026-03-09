import pandas as pd
import altair as alt
import json

alt.data_transformers.disable_max_rows()
df = pd.read_csv("medical_clean_final.csv")

# ── Shared pre-processing ─────────────────────────────────────────────
df["age"]            = pd.to_numeric(df["age"],            errors="coerce")
df["blood_pressure"] = pd.to_numeric(df["blood_pressure"], errors="coerce")
df["glucose_levels"] = pd.to_numeric(df["glucose_levels"], errors="coerce")
df["gender"]         = df["gender"].astype(str).str.strip().str.lower()

# ── CHART 1: Heatmap ──────────────────────────────────────────────────
df_heat = df.dropna(subset=["age", "gender", "smoking_status"]).copy()

def make_age_group(a):
    if a < 30:   return "under30"
    elif a < 60: return "30-59"
    elif a < 80: return "60-79"
    else:        return "80+"

df_heat["age_group"] = df_heat["age"].apply(make_age_group)
AGE_ORDER = ["under30", "30-59", "60-79", "80+"]

s = (df_heat["smoking_status"].astype(str).str.strip().str.lower()
     .str.replace("-", "", regex=False).str.replace(" ", "", regex=False))

def map_smoking(x):
    if x in {"smoker","current","currentsmoker"}:
        return "smoker"
    if x in {"nonsmoker","nonsmoking","never","neversmoker","neversmoked",
             "never_smoked","former","formersmoker","exsmoker","ex"}:
        return "non-smoker"
    return "other"

df_heat["smoking_filter"] = s.apply(map_smoking)

smoking_param = alt.param(
    name="Smoking", value="all",
    bind=alt.binding_select(options=["all","smoker","non-smoker"], name="Smoking Status: ")
)

base_heat = (
    alt.Chart(df_heat)
    .transform_filter("Smoking == 'all' || datum.smoking_filter == Smoking")
    .transform_aggregate(count="count()", groupby=["age_group","gender"])
    .transform_joinaggregate(total_in_age="sum(count)", groupby=["age_group"])
    .transform_calculate(percent="datum.total_in_age > 0 ? datum.count / datum.total_in_age : 0")
)
text_base_heat = base_heat.transform_joinaggregate(max_count="max(count)")

heatmap = base_heat.mark_rect().encode(
    x=alt.X("age_group:N", title="Age Group", sort=AGE_ORDER,
            axis=alt.Axis(labelAngle=0,
                          labelExpr="datum.label == 'under30' ? 'under 30' : datum.label")),
    y=alt.Y("gender:N", title="Gender", sort=["female","male"]),
    color=alt.Color("count:Q", title="Count",
                    scale=alt.Scale(domainMin=0, range=["#cfe2f3","#08306b"])),
    tooltip=[
        alt.Tooltip("age_group:N", title="Age Group"),
        alt.Tooltip("gender:N",    title="Gender"),
        alt.Tooltip("count:Q",     title="Count"),
        alt.Tooltip("percent:Q",   title="Percent within Age Group", format=".1%")
    ]
)

text_heat = text_base_heat.mark_text(baseline="middle").encode(
    x=alt.X("age_group:N", sort=AGE_ORDER,
            axis=alt.Axis(labelAngle=0, labelFontSize=14,
                          labelExpr="datum.label == 'under30' ? 'under 30' : datum.label")),
    y=alt.Y("gender:N", sort=["female","male"], axis=alt.Axis(labelFontSize=13)),
    text=alt.Text("percent:Q", format=".1%"),
    color=alt.condition(
        "datum.max_count > 0 && datum.count / datum.max_count >= 0.55",
        alt.value("white"), alt.value("black")
    )
)

chart1 = (
    (heatmap + text_heat)
    .add_params(smoking_param)
    .properties(title="Participant Distribution by Age Group x Gender", width=900, height=500)
)

# ── CHART 2: Combo Line
df_combo = df.dropna(subset=["age","gender","blood_pressure","glucose_levels"]).copy()

measure = alt.param(name="measure", value="blood_pressure",
    bind=alt.binding_select(options=["blood_pressure","glucose_levels"],
                             labels=["Blood Pressure","Glucose Levels"], name="Measure: "))

base_combo = (
    alt.Chart(df_combo).add_params(measure)
    .transform_calculate(age_int="toNumber(round(datum.age))",
                         selected_value="toNumber(datum[measure])")
    .transform_aggregate(mean_value="mean(selected_value)", groupby=["age_int","gender"])
)

smooth_base = base_combo.transform_loess(
    "age_int","mean_value", groupby=["gender"], bandwidth=0.35, as_=["age_int","smooth_value"])

smooth       = smooth_base.mark_line(strokeWidth=4).encode(x="age_int:Q", y="smooth_value:Q")
faint_points = base_combo.mark_circle(size=30, opacity=0.18).encode(x="age_int:Q", y="mean_value:Q")

panzoom = alt.selection_interval(bind="scales")
hover   = alt.selection_point(fields=["age_int"], nearest=True,
                               on="mousemove", empty=False, clear="mouseout")

selectors = (smooth_base.mark_point(opacity=0)
             .encode(x="age_int:Q", y="smooth_value:Q").add_params(hover))
rule = (alt.Chart(df_combo).transform_calculate(age_int="toNumber(round(datum.age))")
        .mark_rule(color="red", strokeWidth=2).encode(x="age_int:Q").transform_filter(hover))
highlight = (smooth_base.mark_circle(size=120)
             .encode(x="age_int:Q", y="smooth_value:Q",
                     tooltip=[alt.Tooltip("age_int:Q",title="Age"),
                               alt.Tooltip("gender:N",title="Gender"),
                               alt.Tooltip("smooth_value:Q",title="Value",format=".2f")])
             .transform_filter(hover))
labels = (smooth_base.mark_text(dx=8,dy=-10,fontSize=13)
          .encode(x="age_int:Q",y="smooth_value:Q",
                  text=alt.Text("smooth_value:Q",format=".2f")).transform_filter(hover))

chart2 = (
    (smooth + faint_points + selectors + rule + highlight + labels)
    .add_params(panzoom)
    .encode(
        x=alt.X("age_int:Q", title="age", axis=alt.Axis(grid=True, tickMinStep=1)),
        y=alt.Y("smooth_value:Q", title=None, scale=alt.Scale(zero=False)),
        color=alt.Color("gender:N", sort=["female","male"],
                        scale=alt.Scale(domain=["female","male"], range=["#ff5ca8","#3a78b2"]),
                        legend=alt.Legend(orient="right"))
    )
    .properties(width=900, height=500,
                title={"text":"Glucose Levels and Blood Pressure Trends",
                       "subtitle":"Lines are smoothed means","anchor":"middle"},
    )
)

# ── CHART 3: Scatter Facet ────────────────────────────────────────────
df_scatter = df.dropna(subset=["age","gender","blood_pressure","glucose_levels",
                                "condition","smoking_status"]).copy()

select_condition = alt.selection_point(
    fields=["condition"],
    bind=alt.binding_select(options=[None,"Diabetic","Cancer","Pneumonia"],
                             labels=["All","Diabetic","Cancer","Pneumonia"], name="Conditions"),
    value=[{"condition":"Diabetic"}]
)
select_gender = alt.selection_point(
    fields=["gender"],
    bind=alt.binding_radio(options=[None,"female","male"],
                            labels=["Both","female","male"], name="Gender:")
)
select_age = alt.param(value=60,
    bind=alt.binding_range(min=0, max=80, step=1, name="age scale"))
linked_selection = alt.selection_point(fields=["condition"], on="click", clear="dblclick")

bp_threshold = (
    alt.Chart(df_scatter).mark_rule(color="red", strokeDash=[6,3], size=2)
    .encode(x=alt.X("threshold:Q", scale=alt.Scale(domain=[70,200])),
            tooltip=[alt.Tooltip("threshold:Q", title="High Blood Pressure")])
    .transform_calculate(threshold="140")
)

scatter = (
    alt.Chart(df_scatter).mark_point(size=60, opacity=1.0, filled=True)
    .encode(
        x=alt.X("blood_pressure:Q", scale=alt.Scale(domain=[70,200])),
        y=alt.Y("glucose_levels:Q",  scale=alt.Scale(domain=[70,200])),
        color=alt.condition(select_condition, alt.Color("condition:N"), alt.value("lightgray")),
        shape=alt.Shape("gender:N",
                        scale=alt.Scale(domain=["female","male"], range=["square","circle"])),
        tooltip=["condition","blood_pressure","glucose_levels","gender","age"],
    )
    .transform_filter(select_condition)
    .transform_filter(select_gender)
    .transform_filter(alt.datum.age >= select_age)
)

chart3 = (
    alt.layer(scatter, bp_threshold).properties(width=500, height=500)
    .facet(facet=alt.Facet("smoking_status:N", sort=["Non-Smoker","Smoker"], title="Smoking Status"),
           columns=2,
           title=alt.TitleParams(text="Blood Pressure vs Glucose Levels by Smoking Status",
                                  subtitle="* Elderly = age 60+ | Red line = Hypertension (140)",
                                  subtitleColor="gray", subtitleFontSize=12, anchor="middle"))
    .add_params(select_gender, select_age, linked_selection, select_condition)
    .interactive()
)

# Combine 
# combined = alt.vconcat(chart1, chart2, chart3).properties(
#     padding={"top": 30, "left": 10, "right": 10, "bottom": 60}
# )
# combined.save("dashboard.html")

s1 = json.dumps(chart1.to_dict())
s2 = json.dumps(chart2.to_dict())
s3 = json.dumps(chart3.to_dict())

html = f"""<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
</head>
<body> <p style="max-width:800px; color:#555; font-size:16px; margin-bottom:8px;">
T1- Does glucose levels increase with age? 

T2- Are there distinct patterns in these measures among individuals diagnosed with diabetes?  

T3- Find elderly smokers with elevated blood pressure that should have medical interventions?

T4- In different age group, how many male and female will smoke? 

T5 - Are there certain age-gender combinations underrepresented from this study? </p>
  <div id="c1"></div>
  <hr/>
  <div id="c2"></div>
  <hr/>
  <div id="c3"></div>

  <script>
    vegaEmbed("#c1", {s1});
    vegaEmbed("#c2", {s2});
    vegaEmbed("#c3", {s3});
  </script>
</body>
</html>"""

with open("dashboard.html", "w") as f:
    f.write(html)
