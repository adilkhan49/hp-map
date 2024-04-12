# more icons at https://fontawesome.com/search?o=r&m=free

import pandas as pd
import folium
from folium.plugins import GroupedLayerControl

# Read data with locations
data_file = 'pops.csv'
filterby = 'Status'


legend = {
    "Community": {
        "colour": "red", 
        "icon": "heart"},
    "Cost of Living": {
        "colour": "gray", 
        "icon": "sterling-sign"},
    "Climate": {
        "colour": "green", 
        "icon": "cloud-bolt"},
    "Disability Rights": {
        "colour": "pink", 
        "icon": "wheelchair"},
    "Youth": {
        "colour": "blue", 
        "icon": "graduation-cap"},
    "Pollution": {
        "colour": "beige", 
        "icon": "skull-crossbones"},
    "Independents": {
        "colour": "orange", 
        "icon": "person"},
    "BIPOC Rights": {
        "colour": "purple", 
        "icon": "rainbow"},
    "Black & Asian": {
        "colour": "darkred", 
        "icon": "hand-back-fist"},
    }


locations_df = pd.read_csv(data_file)
locations_df = locations_df[locations_df.Latitude.notna()]
locations_df['Topic'] = locations_df['Topic'].fillna('Not Defined')

topics = locations_df['Topic'].unique()

# Initialize the map
m = folium.Map(location=[54.103, -2.912], zoom_start=6,min_zoom=6)

# Set the bounds for the map
uk_bounds = [[47.959999905, -7.57216793459], [61, 1.68153079591]]  # Coordinates for the bounding box covering the UK
m.fit_bounds(uk_bounds)

# Create a FeatureGroup for each type

type_groups = {}
for type_ in locations_df[filterby].unique():
    type_groups[type_] = folium.FeatureGroup(name=type_,show=True)


# Add points to the map and group them by type
for index, row in locations_df.iterrows():
    name = row["Local / Collaboration"]
    link = "https://fr.wikipedia.org/wiki/Place_Guillaume_II"
    topic = row["Topic"]
    colour = legend[topic]["colour"] if topic in legend.keys() else 'white'
    if colour not in ['darkpurple', 'white', 'cadetblue', 'red', 'beige', 'purple', 'lightblue', 'lightgray', 'lightgreen', 'green', 'darkblue', 'pink', 'black', 'gray', 'lightred', 'orange', 'darkred', 'darkgreen', 'blue']:
        print(colour)
    icon = legend[topic]["icon"] if topic in legend.keys() else 'blank'
    popup_text = f"""<a href={link} target="_blank">{name}</a><br><br>{topic}<br><br>Contact:<br>{row["Local contact"]}<br>{row["Local Contact Email"]}"""
    marker = folium.Marker(
        [row['Latitude'], row['Longitude']], 
        popup=popup_text,
        tooltip = name,
        icon=folium.Icon(icon=icon, prefix='fa',color=colour)
    )
    marker.add_to(type_groups[row[filterby]])

# Add all FeatureGroups to the map
for type_, group in type_groups.items():
    group.add_to(m)

GroupedLayerControl(
    groups={filterby: type_groups.values()},
    exclusive_groups=False,
    collapsed=False,
).add_to(m)

legend_items = '\n'.join([
         f'<p><span style="background-color: {v['colour']}; border-radius: 50%; padding: 5px; margin-right: 5px; display: inline-block;"></span>{k}</p>'
         for k,v in legend.items()
])
legend_html = f'''
     <div style="position: fixed; bottom: 50px; left: 50px; z-index:9999; font-size: 14px;">
    {legend_items}
     </div>
     '''
m.get_root().html.add_child(folium.Element(legend_html))

# Save the map as an HTML file
m.save('map_v1.html')

