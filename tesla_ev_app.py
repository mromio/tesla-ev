# Streamlit App for Tesla Supercharger Network Exploration
import streamlit as st
import pandas as pd
import networkx as nx
import json
import math
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the Haversine distance between two geographic points.
    """
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


@st.cache_data
def load_data():
    """
    Load Tesla Supercharger data from cache if available,
    otherwise load from CSV and create the cache.
    """
    try:
        with open("cache_superchargers.json", "r") as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        df = pd.read_csv("merged_ev_supercharger_data.csv")
        data = df.to_dict(orient="records")
        with open("cache_superchargers.json", "w") as f:
            json.dump(data, f, indent=2)
        return data


@st.cache_data
def build_graph(data, threshold=100):
    """
    Build a graph of Supercharger stations. Nodes represent stations,
    and edges connect stations within a given distance threshold.
    """
    G = nx.Graph()
    coords = {}

    for row in data:
        name = row.get("Supercharger") or f"Station_{row.get('Zip', 'unknown')}"
        try:
            lat = float(row["Latitude"])
            lon = float(row["Longitude"])
        except:
            continue
        coords[name] = (lat, lon)
        G.add_node(name, pos=(lon, lat), state=row.get("State", "Unknown"))

    names = list(coords.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            lat1, lon1 = coords[names[i]]
            lat2, lon2 = coords[names[j]]
            dist = haversine(lat1, lon1, lat2, lon2)
            if dist <= threshold:
                G.add_edge(names[i], names[j], weight=dist)

    return G, coords


data = load_data()
G, coords = build_graph(data)

st.title("Tesla Supercharger Network Explorer")
st.write(f"**Total Stations:** {len(G.nodes)}  |  **Total Connections:** {len(G.edges)}")

# Shortest path finder
st.header("Find Shortest Path Between Two Stations")
stations = list(G.nodes)
start = st.selectbox("Start Station", stations)
end = st.selectbox("End Station", stations, index=1)

if st.button("Find Shortest Path"):
    if start in G and end in G:
        try:
            path = nx.shortest_path(G, source=start, target=end, weight="weight")
            st.success(f"Shortest path from {start} to {end} ({len(path) - 1} steps)")
            st.markdown(" → ".join(path))
        except nx.NetworkXNoPath:
            st.error("No path found between selected stations.")

# Nearby station search
st.header("Find Nearby Stations")
query_station = st.selectbox("Choose Station", stations, key="nearby")
dist_limit = st.slider("Search Radius (miles)", min_value=10, max_value=300, value=100)

if st.button("Show Nearby Stations"):
    if query_station in coords:
        lat1, lon1 = coords[query_station]
        result = []
        for name, (lat2, lon2) in coords.items():
            if name != query_station:
                d = haversine(lat1, lon1, lat2, lon2)
                if d <= dist_limit:
                    result.append((name, round(d, 1)))
        result.sort(key=lambda x: x[1])
        st.write(f"Found {len(result)} stations within {dist_limit} miles:")
        for name, dist in result:
            st.markdown(f"- **{name}** ({dist} mi)")
    else:
        st.error("Station not found.")

# Display top 5 most connected stations
st.header("Top 5 Most Connected Stations")
degrees = sorted(G.degree, key=lambda x: x[1], reverse=True)[:5]
for name, degree in degrees:
    st.markdown(f"**{name}**: {degree} connections")

# Count chargers per state
st.header("Number of Chargers per State")
state_counts = {}
for _, data_node in G.nodes(data=True):
    state = data_node.get("state")
    if state:
        state_counts[state] = state_counts.get(state, 0) + 1

state_df = pd.DataFrame(state_counts.items(), columns=["State", "Charger Count"])
st.dataframe(state_df.sort_values("Charger Count", ascending=False))

# Compute charger-to-EV ratio
st.header("Charger to EV Ratio by State")
ratios = []
for state in state_counts:
    ev_count = 0
    for row in data:
        if row.get("State") == state:
            try:
                ev_count = int(row.get("Registration_Count", 0))
                break
            except:
                continue
    charger_count = state_counts[state]
    if ev_count > 0:
        ratio = round(charger_count / ev_count * 1000, 2)
        ratios.append((state, charger_count, ev_count, ratio))

ratio_df = pd.DataFrame(ratios, columns=["State", "Chargers", "EVs", "Chargers per 1000 EVs"])
st.dataframe(ratio_df.sort_values("Chargers per 1000 EVs", ascending=False))

# Graph visualization
st.header("Network Visualization")
if st.button("Show Full Network Graph"):
    pos = nx.get_node_attributes(G, 'pos')
    fig, ax = plt.subplots(figsize=(12, 8))
    nx.draw(G, pos, node_size=20, with_labels=False, ax=ax)
    st.pyplot(fig)
