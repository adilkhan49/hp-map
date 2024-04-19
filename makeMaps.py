# more icons at https://fontawesome.com/search?o=r&m=free

import pandas as pd
import folium
from folium.plugins import GroupedLayerControl
import duckdb

# Read data with locations
data_file = 'Pop Sheet - Pops.csv'
filterby = 'Upcoming'


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


pops_df = pd.read_csv(data_file)
# pops_df["assembly_date"] = pd.to_datetime(pops_df["Assembly Date"],errors='coerce')
# locations_df = locations_df[locations_df.Latitude.notna()]
# locations_df['Topic'] = locations_df['Topic'].fillna('Not Defined')

pop_agg = duckdb.query(
"""
    create or replace table pops as                   
        select 
            "Local / Collaboration" as name,
            "Topic" topic,
            "Status" status,
            "Latitude" latitude,
            "Longitude" longitude,
            "Local contact" contact_name,
            "Local Contact Email" contact_email,   
            "Assembly Date" assembly_date,
            try_strptime("Assembly Date", '%d-%b-%Y') as "ass_date",
            "Status" as status,
            "Venue Address" as address,
            "Description for Interactive Map" description,
            "Link to Action Network Site" as link,
            "Assembly Start Time" start_time,
        from pops_df
        where "Status" in ('Warm','Completed');

    create or replace table all_topics as
        select 
            name,
            list(distinct case when topic is null then 'Not Defined' else topic end order by topic) topics,
        from pops
        group by 1              
;           


    create or replace table loc as 
        select
            name,
            latitude,
            longitude, 
        from pops
        where latitude is not null and longitude is not null
        qualify row_number() over (partition by name order by ass_date desc) = 1
    ;

    create or replace table address as 
        select
            name,
            address,
        from pops
        where address is not null
        qualify row_number() over (partition by name order by status desc, ass_date desc) = 1
    ;

    
    create or replace table description as 
        select
            name,
            description,
        from pops
        where description is not null
        qualify row_number() over (partition by name order by status desc, ass_date desc) = 1
    ;
                          
                      
    create or replace table last_pop as
        select 
            name,
            topic,
            strftime(ass_date,'%-d %B %Y') as assembly_date,
        from pops
        where status = 'Completed'
        qualify row_number() over (partition by name order by ass_date desc) = 1

;
    create or replace table next_pop as
        select 
            name,
            topic,
            ass_date,
            description,
            link,
            start_time,
            case when ass_date is not null then strftime(ass_date,'%-d %B %Y') else assembly_date end as assembly_date,
        from pops
        where status = 'Warm'
        qualify row_number() over (partition by name order by ass_date ) = 1
    ;

    create or replace table past_pops as
        select 
            name,
            count(*)::int num,
        from pops
        where status = 'Completed'
        group by 1              
;           

create or replace table pop_agg as 
    select 
        all_topics.name,
        coalesce(past_pops.num,0) as num_past_pops,
        coalesce(last_pop.topic,next_pop.topic,'Not Defined') as topic,
        all_topics.topics as all_topics,
        loc.Latitude,
        loc.longitude,
        next_pop.topic as next_topic,
        next_pop.ass_date,
        next_pop.assembly_date next_assembly_date,
        next_pop.start_time,
        next_pop.link,
        case when next_pop.name is not null then 'Yes' else 'No' end as "Upcoming",
        last_pop.assembly_date as last_assembly_date,
        address.address,
        description.description,
    from all_topics
    left join past_pops on all_topics.name = past_pops.name
    left join last_pop on all_topics.name = last_pop.name
    left join next_pop on all_topics.name = next_pop.name
    left join loc on all_topics.name = loc.name
    left join address on all_topics.name = address.name
    left join description on all_topics.name = description.name

;
                      
select * from pop_agg where latitude is not null
;


 """).to_df()


# print(duckdb.query("select * from pop_agg where name like 'South Norwood'"))


topics = pop_agg.topic.unique()

# Initialize the map
m = folium.Map(location=[54.103, -2.912], zoom_start=6,min_zoom=6)

# Set the bounds for the map
uk_bounds = [[48, -7.57216793459], [60, 1.68153079591]]  # Coordinates for the bounding box covering the UK
m.fit_bounds(uk_bounds)

# Create a FeatureGroup for each type

type_groups = {}
for type_ in pop_agg[filterby].unique():
    type_groups[type_] = folium.FeatureGroup(name=type_,show=True)


# Add points to the map and group them by type
for index, row in pop_agg.iterrows():
    name = row['name']
    link = "https://fr.wikipedia.org/wiki/Place_Guillaume_II"
    topic = row.topic
    colour = legend[topic]["colour"] if topic in legend.keys() else 'white'
    if colour not in ['darkpurple', 'white', 'cadetblue', 'red', 'beige', 'purple', 'lightblue', 'lightgray', 'lightgreen', 'green', 'darkblue', 'pink', 'black', 'gray', 'lightred', 'orange', 'darkred', 'darkgreen', 'blue']:
        print(colour)
    icon = legend[topic]["icon"] if topic in legend.keys() else 'blank'
    # popup_text = f"""<a href={link} target="_blank">{name}</a><br><br>{topic}<br><br>Contact:<br>{row.contact_name}<br>{row.contact_email}"""
    
    popup_html = f"""
    <head>
        <style>
            td{{padding-right: 10px;}}
            tr{{vertical-align:top;}}
        </style>
    </head>
    <h4>{name}</h4>"""
    popup_html += "<table>"
    popup_html += f"""<tr><td>Topic</td><td>{topic}</td><tr>"""
    if len(row.all_topics)>1:
        other_topics = ', '.join([t for t in row.all_topics if t!=topic])
        popup_html += f"""<tr><td>Other Topics</td><td>{other_topics}</td><tr>"""
    popup_html += f"""<tr><td>Completed</td><td>{int(row.num_past_pops)}</td><tr>"""
    if row.Upcoming != 'No':
        next_date = row.next_assembly_date 
        if row.start_time:
            next_date += ' @ ' + row.start_time
        if row.link:
            next_assembly_date = f"""<a href={row.link} target="_blank">{next_date}</a>"""
        else:
            next_assembly_date = row.next_assembly_date
        popup_html += f"""<tr><td>Next Pop</td><td>{next_assembly_date}</td><tr>"""
    if row.last_assembly_date != None:
        popup_html += f"""<tr><td>Last Pop</td><td>{row.last_assembly_date}</td><tr>"""
    if row.address != None:
        popup_html += f"""<tr><td>Address</td><td>{row.address}</td><tr>"""
    if row.description != None:
        popup_html += f"""<tr><td>Description</td><td>{row.description}</td><tr>"""
        popup_width = 400
    else:
        popup_width= 250
    popup_html += "</table>"
    iframe = folium.IFrame(popup_html)
    popup = folium.Popup(iframe,
                        min_width=popup_width,
                        max_width=popup_width
                        )
    marker = folium.Marker(
        [row.latitude, row.longitude], 
        popup=popup,
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
         f'<div><span style="background-color: {v['colour']}; border-radius: 50%; padding: 5%; margin-right: 10%; display: inline-block; "></span>{k}</div>'
         for k,v in legend.items()
])
legend_html = f'''
     <div style="position: fixed; bottom: 2%; left: 1%; z-index:9999; font-size:2vw; white-space: nowrap; text-overflow: ellipsis; ">
    {legend_items}
     </div>
     '''
m.get_root().html.add_child(folium.Element(legend_html))

totals = duckdb.query("""
with t as (
    select status, count(*) as count from pops group by status
)
SELECT *
FROM (
    PIVOT t
    ON status
    USING max(count)
)
 """).to_df().to_dict('records')[0]
print(totals)

totals_html = f"""
<style>
    .kpi-container {{
        display: block;
        position: fixed; 
        top: 0%; 
        left: 50px; 
        z-index:9999; 
        font-size:2.5vw; 
        padding: 1%; 
        display: flex;
        color: green;
        }}
    .kpi-card {{
        margin: 5px;
        border: 1px solid black;
        background-color: white; 
        padding: 1%; 
        }}
    .card-value {{
        text-align: center;
        display: block;
        font-size: 200%;  
        }}
    .card-text {{
        text-align: center;
        display: block;
        font-size: 100%;
        }}
    .kpi-card:first-child {{
        margin-left: 0;
    }}
    .kpi-card:last-child {{
        margin-right: 0;
    }}
</style>

<div class="kpi-container">
  <div class="kpi-card">
    <div class="card-value">{totals['Completed']}</div>
    <div class="card-text">Complete</div>
  </div>
  <div class="kpi-card">
    <div class="card-value">{totals['Warm']}</div>
    <div class="card-text">Upcoming</div>
  </div>
</div>

"""


m.get_root().html.add_child(folium.Element(totals_html))

# Save the map as an HTML file
m.save('map.html')

