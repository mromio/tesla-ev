# Tesla Supercharger Graph Navigator - Maryam Romio SI 507 Final Project

import csv
import json
import math
import networkx as nx
import matplotlib.pyplot as plt


def load_and_cache_csv(csv_file, cache_file):
    """
    Load Tesla data from CSV or cached JSON file.
    """
    try:
        with open(cache_file, 'r') as f:
            data = json.load(f)
            print("[INFO] Loaded data from cache.")
            return data
    except FileNotFoundError:
        data = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)
        print("[INFO] Cached data to JSON.")
        return data


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two points using the Haversine formula.
    """
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def build_graph(data, distance_threshold=100):
    """
    Create a network graph of Tesla Superchargers.
    """
    G = nx.Graph()
    coords = {}

    for row in data:
        name = row.get('Supercharger') or f"Station_{row.get('Zip', 'unknown')}"
        try:
            lat = float(row.get('Latitude', 0))
            lon = float(row.get('Longitude', 0))
        except ValueError:
            continue
        coords[name] = (lat, lon)
        G.add_node(name, pos=(lon, lat), state=row.get('State', 'Unknown'))

    names = list(coords.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            lat1, lon1 = coords[names[i]]
            lat2, lon2 = coords[names[j]]
            dist = haversine(lat1, lon1, lat2, lon2)
            if dist < distance_threshold:
                G.add_edge(names[i], names[j], weight=dist)

    return G, coords


def draw_graph(G):
    """
    Draw the graph using matplotlib.
    """
    pos = nx.get_node_attributes(G, 'pos')
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, node_size=30, with_labels=False)
    plt.title("Tesla Supercharger Network")
    plt.show()


def most_connected_stations(G, top_n=5):
    """
    Return the top N stations by number of connections.
    """
    degrees = sorted(G.degree, key=lambda x: x[1], reverse=True)
    return degrees[:top_n]


def chargers_per_state(G):
    """
    Count number of chargers per state.
    """
    state_counts = {}
    for _, data in G.nodes(data=True):
        state = data.get('state') or data.get('State')
        if state:
            state_counts[state] = state_counts.get(state, 0) + 1
    return state_counts


def find_shortest_path(G):
    """
    Ask user for two stations and show the shortest path.
    """
    print("\nEnter two Supercharger station names exactly as listed.")
    source = input("Start station: ").strip()
    target = input("End station: ").strip()
    if source in G and target in G:
        try:
            path = nx.shortest_path(G, source=source, target=target, weight='weight')
            print("\nShortest path:")
            for step in path:
                print(" →", step)
            print(f"\nTotal steps: {len(path) - 1}")
        except nx.NetworkXNoPath:
            print("\nNo path found between the selected stations.")
    else:
        print("\nOne or both station names not found in network.")


def find_nearby_stations(G, coords):
    """
    Ask user for a station name and return nearby stations within a distance.
    """
    query = input("\nEnter station name to search nearby: ").strip()
    if query not in coords:
        print("Station not found.")
        return
    lat1, lon1 = coords[query]
    radius = float(input("Enter search radius in miles: "))
    print(f"\nStations within {radius} miles of {query}:")
    for name, (lat2, lon2) in coords.items():
        if name != query:
            dist = haversine(lat1, lon1, lat2, lon2)
            if dist <= radius:
                print(f"{name} ({round(dist, 1)} miles)")


def main():
    data = load_and_cache_csv("merged_ev_supercharger_data.csv", "cache_superchargers.json")
    G, coords = build_graph(data)

    while True:
        print("\n--- Tesla Supercharger Network Menu ---")
        print("1. Show total stations and connections")
        print("2. Draw network graph")
        print("3. Show top 5 most connected stations")
        print("4. Show number of chargers per state")
        print("5. Find shortest path between two stations")
        print("6. Find nearby stations within X miles")
        print("7. Exit")

        choice = input("Enter your choice (1-7): ")

        if choice == '1':
            print(f"\nTotal Stations: {len(G.nodes)}")
            print(f"Total Connections: {len(G.edges)}")

        elif choice == '2':
            draw_graph(G)

        elif choice == '3':
            top = most_connected_stations(G)
            for name, degree in top:
                print(f"{name}: {degree} connections")

        elif choice == '4':
            state_counts = chargers_per_state(G)
            for state in sorted(state_counts):
                print(f"{state}: {state_counts[state]} chargers")

        elif choice == '5':
            find_shortest_path(G)

        elif choice == '6':
            find_nearby_stations(G, coords)

        elif choice == '7':
            print("Exiting.")
            break

        else:
            print("Invalid input. Try again.")


if __name__ == "__main__":
    main()
