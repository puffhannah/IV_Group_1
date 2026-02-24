import os
import pandas as pd
import altair as alt

alt.data_transformers.disable_max_rows()

df = pd.read_csv("medical_clean_final.csv")

df["age"] = pd.to_numeric(df["age"], errors="coerce")
df = df.dropna(subset=["age", "gender", "smoking_status"]).copy()
df["gender"] = df["gender"].astype(str).str.strip().str.lower()

# =========================
# NEW: Age groups (4 bins)
# Under 30, 30-59, 60-79, 80+
# =========================
def make_age_group(a):
    if a < 30:
        return "under30"
    elif a < 60:
        return "30-59"
    elif a < 80:
        return "60-79"
    else:
        return "80+"

df["age_group"] = df["age"].apply(make_age_group)

AGE_ORDER = ["under30", "30-59", "60-79", "80+"]

# =========================
# Smoking status filter (All / Smoking / Non-Smoking)
# =========================
s = (
    df["smoking_status"]
    .astype(str)
    .str.strip()
    .str.lower()
    .str.replace("-", "", regex=False)
    .str.replace(" ", "", regex=False)
)

def map_smoking(x: str) -> str:
    if x in {"smoker", "current", "currentsmoker"}:
        return "smoker"
    if x in {"nonsmoker", "nonsmoking", "never", "neversmoker", "neversmoked", "never_smoked"}:
        return "non-smoker"
    if x in {"former", "formersmoker", "exsmoker", "ex"}:
        return "non-smoker"
    return "other"

df["smoking_filter"] = s.apply(map_smoking)

# -----------------------------
# Param 
# -----------------------------
smoking_param = alt.param(
    name="Smoking",
    value="all",
    bind=alt.binding_select(
        options=["all", "smoker", "non-smoker"],
        name="Smoking Status: "
    )
)

# -----------------------------
#  Base pipeline:
#    filter -> aggregate(count) -> percent within age_group
# -----------------------------
base = (
    alt.Chart(df)
    .transform_filter("Smoking == 'all' || datum.smoking_filter == Smoking")
    .transform_aggregate(
        count="count()",
        groupby=["age_group", "gender"]
    )
    .transform_joinaggregate(
        total_in_age="sum(count)",
        groupby=["age_group"]
    )
    .transform_calculate(
        percent="datum.total_in_age > 0 ? datum.count / datum.total_in_age : 0"
    )
)
text_base = base.transform_joinaggregate(
    max_count="max(count)"
)

heatmap = base.mark_rect().encode(
    x=alt.X(
        "age_group:N",
        title="Age Group",
        sort=AGE_ORDER,
        axis=alt.Axis(
            labelAngle=0,
            labelExpr=(
                "datum.label == 'under30' ? 'under 30' : datum.label"
            )
        )
    ),
    y=alt.Y(
        "gender:N",
        title="Gender",
        sort=["female", "male"]
    ),
    color=alt.Color(
        "count:Q",
        title="Count",
        scale=alt.Scale(domainMin=0)
    ),
    tooltip=[
        alt.Tooltip("age_group:N", title="Age Group"),
        alt.Tooltip("gender:N", title="Gender"),
        alt.Tooltip("count:Q", title="Count"),
        alt.Tooltip("percent:Q", title="Percent within Age Group", format=".1%")
    ]
)


text = text_base.mark_text(baseline="middle").encode(
    x=alt.X(
        "age_group:N",
        sort=AGE_ORDER,
        axis=alt.Axis(
            labelAngle=0,
            labelFontSize=14,
            labelExpr="datum.label == 'under30' ? 'under 30' : datum.label"
        )
    ),
    y=alt.Y(
        "gender:N",
        sort=["female", "male"],
        axis=alt.Axis(
            labelFontSize=13
        )
    ),
    text=alt.Text("percent:Q", format=".1%"),
    color=alt.condition(
        "datum.max_count > 0 && datum.count / datum.max_count >= 0.55",
        alt.value("white"),
        alt.value("black")
    )
)


chart = (
    (heatmap + text)
    .add_params(smoking_param)
    .properties(
        title="Participant Distribution by Age Group × Gender (Filter by Smoking Status)",
        width=1100,
        height=500
    )
)

chart.save("heatmap.html")
print("saved to heatmap.html")