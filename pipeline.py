import pandas as pd
import requests
import numpy as np
import sqlite3
import matplotlib.pyplot as plt

df = pd.read_csv('fig_9.1.11 - fig_9.1.11.csv')

# pivot from long to wide
df_wide = df.pivot(index='Country', columns='Category', values='% of respondents').reset_index()
df_wide.columns.name = None
print(df_wide.head())
print(df_wide.shape)

# Step 2 — fetch subregions from REST Countries API
try:
    response = requests.get("https://restcountries.com/v3.1/all?fields=name,subregion", timeout=10)
    response.raise_for_status()
    countries_data = response.json()
except requests.exceptions.ConnectionError:
    print("No internet connection")
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e}")
except Exception as e:
    print(f"Something went wrong: {e}")

# Step 3 — extract name and subregion
subregions = []
for c in countries_data:
    subregions.append({
        'Country': c['name']['common'],
        'subregion': c.get('subregion', 'Unknown')
    })

df_subregions = pd.DataFrame(subregions)

# Step 4 — merge
df_merged = df_wide.merge(df_subregions, on='Country', how='left')
print(df_merged.head())
print(df_merged.shape)
print(df_merged['subregion'].value_counts())

# Step 5 — rename columns for easier use
df_merged = df_merged.rename(columns={
    'AI strategy and culture': 'ai_strategy',
    'Support for AI literacy': 'ai_literacy',
    'Responsible AI governance': 'ai_governance'
})

# Step 6 — NumPy: compute composite score (average of 3 metrics)
scores = df_merged[['ai_strategy', 'ai_literacy', 'ai_governance']].values
df_merged['composite_score'] = np.round(np.mean(scores, axis=1), 3)

# Step 7 — store in SQLite
conn = sqlite3.connect('ai_governance.db')
df_merged.to_sql('countries', conn, if_exists='replace', index=False)
print("Saved to SQLite")

# Step 8 — Query 1: average scores by subregion
query1 = """
SELECT subregion,
    ROUND(AVG(ai_strategy), 3) as avg_ai_strategy,
    ROUND(AVG(ai_literacy), 3) as avg_ai_literacy,
    ROUND(AVG(ai_governance), 3) as avg_ai_governance,
    ROUND(AVG(composite_score), 3) as avg_composite
FROM countries
GROUP BY subregion
ORDER BY avg_composite DESC
"""
result1 = pd.read_sql(query1, conn)
print("\nAverage scores by subregion:")
print(result1)

# Step 9 — Query 2: top country per subregion for AI governance
query2 = """
SELECT subregion, Country, ai_governance
FROM countries
WHERE ai_governance = (
    SELECT MAX(ai_governance) 
    FROM countries c2 
    WHERE c2.subregion = countries.subregion
)
ORDER BY ai_governance DESC
"""
result2 = pd.read_sql(query2, conn)
print("\nTop country per subregion for AI governance:")
print(result2)

# Step 10 — Query 3: literacy vs governance gap
query3 = """
SELECT Country, subregion,
    ROUND(ai_literacy - ai_governance, 3) as literacy_governance_gap
FROM countries
ORDER BY literacy_governance_gap DESC
LIMIT 10
"""
result3 = pd.read_sql(query3, conn)
print("\nBiggest literacy vs governance gap:")
print(result3)

# Step 11 — export results
result1.to_csv('subregion_scores.csv', index=False)
result2.to_csv('top_countries.csv', index=False)
result3.to_csv('literacy_governance_gap.csv', index=False)
print("\nCSVs exported")

conn.close()

# drop NaN subregion
result1_clean = result1.dropna(subset=['subregion'])

# set up the chart
fig, ax = plt.subplots(figsize=(12, 8))

x = range(len(result1_clean))
width = 0.25

bars1 = ax.barh([i + width for i in x], result1_clean['avg_ai_strategy'], width, label='AI Strategy & Culture', color='#534AB7')
bars2 = ax.barh([i for i in x], result1_clean['avg_ai_literacy'], width, label='Support for AI Literacy', color='#1D9E75')
bars3 = ax.barh([i - width for i in x], result1_clean['avg_ai_governance'], width, label='Responsible AI Governance', color='#D85A30')

ax.set_yticks(list(x))
ax.set_yticklabels(result1_clean['subregion'], fontsize=9)
ax.set_xlabel('% of Respondents')
ax.set_title('AI Readiness by Subregion — Stanford HAI 2026', fontsize=13)
ax.legend()
ax.set_xlim(0, 1)
ax.invert_yaxis()
plt.tight_layout()
plt.savefig('subregion_chart.png', dpi=150)
plt.show()
print("Chart saved")

# Filter just Northern and Western Europe
europe_df = df_merged[df_merged['subregion'].isin(['Northern Europe', 'Western Europe'])]

# sort by composite score
europe_df = europe_df.sort_values('composite_score', ascending=True)

fig, ax = plt.subplots(figsize=(10, 8))

x = range(len(europe_df))
width = 0.25

ax.barh([i + width for i in x], europe_df['ai_strategy'], width, label='AI Strategy & Culture', color='#534AB7')
ax.barh([i for i in x], europe_df['ai_literacy'], width, label='Support for AI Literacy', color='#1D9E75')
ax.barh([i - width for i in x], europe_df['ai_governance'], width, label='Responsible AI Governance', color='#D85A30')

ax.set_yticks(list(x))
ax.set_yticklabels(europe_df['Country'], fontsize=9)
ax.set_xlabel('% of Respondents')
ax.set_title('Northern & Western Europe — AI Readiness Breakdown', fontsize=13)
ax.legend()
ax.set_xlim(0, 1)
plt.tight_layout()
plt.savefig('europe_chart.png', dpi=150)
plt.show()
print("Europe chart saved")