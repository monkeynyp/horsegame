import requests
from bs4 import BeautifulSoup
from itertools import combinations
import networkx as nx
import matplotlib.pyplot as plt

# Specify a font that supports Chinese characters
font_name = 'Arial Unicode MS'  # This is a common font that supports Chinese characters

# Set the font to the specified font
plt.rcParams['font.sans-serif'] = [font_name]

no_of_race = input("Input Number of Race: ")
race_date= input("Race Date YYYY/MM/DD :")

for race_no in range(1,int(no_of_race)+1):
    # URL of the page containing the table
    url = 'https://racing.hkjc.com/racing/information/Chinese/Racing/FormLine.aspx?RaceDate='+race_date+'&RaceNo='+str(race_no)
    print(url)
    # Send a GET request to the URL
    response = requests.get(url)
    #with open('Graphical/data.html', 'r') as file:
        #html = file.read()
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    #soup = BeautifulSoup(html, 'html.parser')

    # Find the table containing the race information
    table = soup.find('table', {'id': 'formlinelist'})
    #


    #print(table)
    # Parse the table rows and group the data by date
    grouped_data = {}
    current_date = None

    for row in table.find_all('tr'):
        class_list = row.get('class', [])
        if all(class_name in class_list for class_name in ['bg_blue', 'color_w', 'font_wb']):
            # Extract the date from the first cell in the row
            current_date = row.find('a').text.strip()
            grouped_data[current_date] = []

        # Skip the row with class "bg_e6caae f_tac f_fs14 font_wb"
        if all(class_name in class_list for class_name in ['bg_e6caae', 'f_tac', 'f_fs14', 'font_wb']):
            continue

        if current_date:
            # Extract horse name from the first cell in the row
            horse_name = row.find('td').text.strip()
            if horse_name != current_date:
                grouped_data[current_date].append(horse_name)

    # Generate pairs of horses within each group
    pairs_data = {}
    for date, horses in grouped_data.items():
        pairs_data[date] = []
        if len(horses) >= 2:
            pairs = list(combinations(horses, 2))
            pairs_data[date].extend(pairs)

    #print(pairs_data)

    # Create a directed graph
    G = nx.DiGraph()

    # Add edges to the graph
    for date, pairs in pairs_data.items():
        for pair in pairs:
            horse1, horse2 = pair
            G.add_edge(horse1, horse2)

    print("Nodes:", G.nodes())
    print("Edges:", G.edges())
    # Calculate the out-degree of each node
    out_degrees = dict(G.out_degree())

    # Adjust the node size based on the out-degree
    node_sizes = [out_degrees[node] * 2500+500 for node in G.nodes()]
    # Draw the graph
    node_colors = ['orangered' if out_degrees[node]>=6 else 'Coral' if out_degrees[node] >=4 else 'lightsalmon' if out_degrees[node] == 3 else 'moccasin' if out_degrees[node] == 2 else 'lightgreen' if out_degrees[node] == 1 else 'lavender' for node in G.nodes()]

    pos = nx.shell_layout(G)
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_size=node_sizes, node_color=node_colors, font_size=10, font_weight='bold', edge_color='gray', arrowsize=20, node_shape='o')

    plt.text(0.5, 0.5, 'Copyright MonkeyForecast http://nyp.pythonanywhere.com', fontsize=12, color='gray', alpha=0.5, ha='center', va='center', transform=plt.gca().transAxes)

    #plt.title('Horse Relationship Diagram', pad=20)
    #plt.axis('off')
    # Save the chart as a PNG file
    plt.savefig('./static/horse_relationship'+str(race_no)+'.png')

    # Draw the graph

    #plt.figure(figsize=(6, 4))  # Adjust the figure size for mobile screens
    #nx.draw(G, with_labels=True, font_size=8, font_family='Arial Unicode MS')  # Adjust font size

# Save the chart as a PNG file
#plt.savefig('horse_relationship_mobile.png')

# Display the chart
#plt.show()