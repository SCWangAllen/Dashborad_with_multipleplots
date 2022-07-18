import plotly.express as px

df = px.data.gapminder().query("continent=='Oceania'")
df
