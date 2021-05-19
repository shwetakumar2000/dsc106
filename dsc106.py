
"""
Created on Mon May 17 13:29:38 2021
@author: Shweta Kumar and Ray Zhao
"""

import streamlit as st
import altair as alt
import data

st.cache(persist=True)

us = data.geoshapes()
counties = data.counties()
state_map = data.state_map(counties)
states = data.states(state_map)
hes = data.hesitancy(state_map)
demos = data.demographics()

#Title and Header
st.title('💉 United States COVID-19 Vaccine Distributions')
st.sidebar.markdown('💉 United States COVID-19 Vaccine 💉')
st.sidebar.markdown(''' 
This app was designed to provide visualizations to different factors of the vaccine distribution in the United States. 

\n

The data comes from **The CDC** and **Our World in Data**\n

Select which state you would like to visualize \n

All the Charts are interactive. \n

Scroll the mouse over the Charts to feel the interactive features like Tool tip, Zoom, Pan\n
                    
Designed by: 
**Shweta Kumar and Ray Zhao**  ''')


#By Entire Country
st.header("Percentage Vaccinated Per Week by County")
select_week = alt.selection_single(
    name='selected', fields=['week'], init={'week': 2},
    bind=alt.binding_range(min=states.min_week, max=states.max_week, step=1)
)

# STATE VACCINATION CHOROPLETH
c1a = alt.Chart(us.states).mark_geoshape(
    stroke='black',
    strokeWidth=0.05
).project(
    type='albersUsa'
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(states.wide, 'sfips', ['statename'] + states.columns)
).transform_fold(
    states.columns, as_=['week', 'pct']
).transform_calculate(
    week='parseInt(datum.week)',
    pct='isValid(datum.pct) ? datum.pct : -1'  
).encode(
    color=alt.condition(
        'datum.pct > 0',
        alt.Color('pct:Q', legend=alt.Legend(title="% Population Vaccinated"), scale=alt.Scale(scheme='yellowgreenblue', domain=(0, 100))),
        alt.value('#DBE9F6')
    ),
    # opacity=alt.condition(click, alt.value(1), alt.value(0)),
    tooltip=['pct:Q', 'statename:N']
).add_selection(
    select_week,
    # click
).properties(
    width=700,
    height=400
).transform_filter(
    select_week
)


# CLICK STATE SELECTOR
click = alt.selection_multi(fields=['statename'])

# COUNTY VACCINATION CHOROPLETH
c1b = alt.Chart(us.counties).mark_geoshape(
    stroke='black',
    strokeWidth=0.1,
).project(
    type='albersUsa'
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(counties, 'fips', ['statename', 'pct', 'label'])
).encode(
    color=alt.condition(
        'isValid(datum.pct)',
        alt.Color('pct:Q', legend=alt.Legend(title="% Population Vaccinated"), scale=alt.Scale(scheme='yellowgreenblue', domain=(0, 100))),
        alt.value('#DBE9F6')
    ),
    opacity=alt.condition(click, alt.value(1), alt.value(0)),
    tooltip=['label:N', 'pct:N']
).add_selection(
    click
).properties(
    width=700,
    height=400
)

# SEX VACCINATION BAR CHART
c3a = alt.Chart(demos.sex).mark_bar().encode(
    x=alt.X('group:N', axis=alt.Axis(title='Sex')),
    y=alt.Y('pct:Q',  axis=alt.Axis(title='% Vaccinated'), scale=alt.Scale(domain=(0, 100))),
    color=alt.Color('group:N', legend=alt.Legend(title="Sex"))
).add_selection(
    select_week
).transform_filter(
    select_week
)



# ETHNICITY VACCINATION BAR CHART
c3b = alt.Chart(demos.eth).mark_bar().encode(
    x=alt.X('group:N', axis=alt.Axis(title='Ethnicity')),
    y=alt.Y('pct:Q',  axis=alt.Axis(title='% Vaccinated'), scale=alt.Scale(domain=(0, 100))),
    color=alt.Color('group:N', legend=alt.Legend(title="Ethnicity"))
).add_selection(
    select_week
).transform_filter(
    select_week
)

c3 = alt.hconcat(
    c3a, c3b
).resolve_scale(
    color='independent'
)

C = (c1a + c1b)
st.altair_chart(C)

st.header("Select States to Compare Vaccine Distribution Trends")
options = st.multiselect("Select state",states.wide["statename"])
c2 = alt.Chart(states.long[states.long["statename"].isin(options)],width=500,height=300).mark_line().encode(
    x=alt.X('week', axis=alt.Axis(title='Week')),
    y=alt.Y('pct', axis=alt.Axis(title='Percentage Vaccinated')),
    color=alt.Color('statename', scale=alt.Scale(domain=click)),
    # opacity=alt.condition(click, alt.value(1), alt.value(0.02)),
).add_selection(
    click
).interactive().properties(
    width=1000,
    height=400
)
st.altair_chart(c2)

st.header("Compare Weekly Percent Vaccinated by Demographics")
op = st.radio("Select the option",('Race', 'Gender'))

if op == 'Gender':
    st.altair_chart(c3a)
elif op == 'Race':
    st.altair_chart(c3b)


st.header("Percent of Population Hesitant Towards Vaccine")
"Hesitancy rates estimated by CDC using the U.S. Census Bureau’s Household Pulse Survey (HPS)" 
"** Data derived from April 14-26, 2021**"

# HESITANCY COUNTY CHOROPLETH
c4a = alt.Chart(us.states).mark_geoshape(
    stroke='black',
    strokeWidth=0.05
).project(
    type='albersUsa'
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(hes.states, 'sfips', ['statename', 'pct'])
).encode(
    color=alt.Color('pct:Q', legend=alt.Legend(title="% Hesitancy"), scale=alt.Scale(scheme='yellowgreenblue', domain=(0, 100))),
    tooltip=['pct:Q', 'statename:N']
).properties(
    width=700,
    height=400
)

# HESITANCY STATE CHOROPLETH
c4b = alt.Chart(us.counties).mark_geoshape(
    stroke='black',
    strokeWidth=0.1,
).project(
    type='albersUsa'
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(hes.county, 'fips', ['statename', 'county', 'pct'])
).encode(
    color=alt.Color('pct:Q', legend=alt.Legend(title="% Hesitancy"), scale=alt.Scale(scheme='yellowgreenblue', domain=(0, 100))),
    opacity=alt.condition(click, alt.value(1), alt.value(0)),
    tooltip=['county:N', 'pct:N']
).add_selection(
    click
).properties(
    width=700,
    height=400
)

# Highest Percentage Hesitancy
top5 = hes.states.sort_values("pct",ascending=False)[["statename","pct"]].head()
top5.reset_index(inplace = True,drop = True)

bar1 = alt.Chart(top5,title="Top 5 Hesitancy").mark_bar().encode(
    x=alt.X('statename', axis=alt.Axis(title='State')),
    y=alt.Y('pct', axis=alt.Axis(title='% Hesitancy')),
    color=alt.Color("statename",legend=None),
    tooltip = "pct"
).interactive()

# HESISTANCY CHOROPLETH
C2 = (c4a + c4b) | bar1
st.altair_chart(C2)
