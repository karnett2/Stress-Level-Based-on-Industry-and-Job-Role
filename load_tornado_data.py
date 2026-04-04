import pandas as pd
import plotly.express as px

# Load the tornado dataset into a DataFrame
df = pd.read_csv('Tornados-US-2011-2022.csv')

# (Optional) Display the first few rows to verify it loaded correctly
print(df.head())

# Create the scatter plot using the dataset you just loaded
fig = px.scatter(df, 
                 x="loss", 
                 y="fat", 
                 size="fat", 
                 color="st",
                 hover_name="st", 
                 log_x=True, 
                 size_max=60)

fig.show()

# --- SECOND VISUALIZATION USING AI: US Choropleth Map ---
# Prompt Inputted: import plotly.express as px
# df = px.data.gapminder()
#fig = px.choropleth(df, locations="iso_alpha", color="lifeExp", hover_name="country", animation_frame="year", range_color=[20,80])
#fig.show(). 
# Can you make a similar graph using my tornado date with the United States and frequency of tornadoes?
#This Code worked on the first attempt, I did not do any modifications to the code provided by the AI.

# 1. Group the data by Year ('yr') and State ('st') and count the number of tornadoes
freq_df = df.groupby(['yr', 'st']).size().reset_index(name='Tornado Frequency')
# 2. Create the animated choropleth map
fig2 = px.choropleth(
    freq_df, 
    locations="st",             # The column with the State abbreviations
    locationmode="USA-states",  # Tell Plotly we are using US state abbreviations
    color="Tornado Frequency",  # What to color the states by
    scope="usa",                # Restrict the map scale to the USA only
    hover_name="st",            # Show the state abbreviation on hover
    animation_frame="yr",       # Animate the map by the Year column
    color_continuous_scale="Reds", # Use a red color scale
    title="Tornado Frequency by State (2011-2022)"
)
# Show the new map
fig2.show()

