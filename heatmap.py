import os
import pandas as pd
import altair as alt

alt.data_transformers.disable_max_rows()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "medical_clean_final.csv")

df = pd.read_csv(csv_path)

df["age"] = pd.to_numeric(df["age"], errors="coerce")
df = df.dropna(subset=["age", "gender", "smoking_status"]).copy()

bins = list(range(0, 101, 10)) + [200]
labels = [f"{i}-{i+9}" for i in range(0, 100, 10)] + ["100+"]

df["age_group"] = pd.cut(
    df["age"],
    bins=bins,
    labels=labels,
    right=False,
    include_lowest=True
)

df = df.dropna(subset=["age_group"]).copy()


heatmap = (
    alt.Chart(df)
    .transform_calculate(
        smoking_norm="lower(replace(replace(datum.smoking_status,'-',''),' ',''))"
    )
    .transform_calculate(
        is_nonsmoker="indexof(datum.smoking_norm,'nonsmoker') >= 0 ? 1 : 0"
    )
    .transform_calculate(
        is_smoker="datum.is_nonsmoker == 1 ? 0 : 1"
    )
 
    .transform_aggregate(
        total="count()",
        smoker="sum(is_smoker)",
        groupby=["age_group", "gender"]
    )
    .transform_calculate(
        smoking_rate="datum.total == 0 ? 0 : datum.smoker / datum.total"
    )
  
    .transform_impute(
        impute="smoking_rate",
        key="age_group",
        keyvals=labels,
        groupby=["gender"],
        value=0
    )
    .transform_impute(
        impute="total",
        key="age_group",
        keyvals=labels,
        groupby=["gender"],
        value=0
    )
    .mark_rect()
    .encode(
        x=alt.X("age_group:N", title="Age Group (10-year bins)", sort=labels),
        y=alt.Y("gender:N", title="Gender"),
        color=alt.Color(
            "smoking_rate:Q",
            title="Smoking Rate",
            scale=alt.Scale(domain=[0, 1])
        ),
        tooltip=[
            alt.Tooltip("age_group:N", title="Age Group"),
            alt.Tooltip("gender:N", title="Gender"),
            alt.Tooltip("smoking_rate:Q", title="Smoking Rate", format=".2f"),
            alt.Tooltip("total:Q", title="Number of People")
        ]
    )
    .properties(
        width=900,
        height=350,
        title="Heatmap: Smoking Rate by Age Group × Gender"
    )
)

out = os.path.abspath("heatmap.html")
heatmap.save(out)

print("Saved HTML to:", out)
print("Exists?", os.path.exists(out))