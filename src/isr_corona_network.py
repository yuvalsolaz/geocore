import requests
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt

# data source urls
folded_url = 'http://coronadata.webiks.com/folded_data.json'
normal_url = 'http://coronadata.webiks.com/data.json'

# Drawing parameters
node_color_map = {'חולה מאומת': 'red',
                  'חולה מאומת - מקור לא ידוע': 'purple',
                  'טיסה': 'yellow',
                  'תחנה': 'blue',
                  'מקום': 'green'}
draw_func = nx.draw_kamada_kawai #  nx.draw_spring
draw_options = {'node_size': 10,'font_size': 10,'with_labels': True}


def draw(G, nodes_color, fig_num,node_labels=None):
    fig_size = (15, 15)
    fig = plt.figure(fig_num, figsize=fig_size)
    ax = fig.add_subplot(1,1,1)

    draw_options['node_color'] = nodes_color
    if node_labels is None:
        draw_func(G, ax=ax, **draw_options)
    else:
        draw_options['labels'] = node_labels
        draw_options['with_labels'] = True
        draw_func(G, ax=ax,**draw_options)
        for label in node_color_map:
            ax.plot([0], [0], color=node_color_map[label], label=label[::-1])
    plt.legend()
    plt.show()


def create_network(data):
    G = nx.Graph()
    # Nodes reside in 'data' key of data
    # Each node contains id, type, label and additional properties
    # For each node map id to node, id to label and color by type
    nodes_data = {}
    nodes_color = []
    node_labels = {}
    for node in data['data']['nodes']:
        nodes_data[node['id']] = node
        if 'label' in node:
            node_labels[node['id']] = node['label'][::-1]
        nodes_color.append(node_color_map[node['type']])
        G.add_node(node['id'], **node)

    # Edges reside in 'data' key of data
    # Each node contains source, target and additional properties
    for edge in data['data']['edges']:
        G.add_edge(edge['source'], edge['target'], **edge)

    return G, nodes_color, node_labels


def load_data(url):
    r = requests.get(url)
    data = r.json()
    updateTime = datetime.fromtimestamp(data['lastUpdateDate'] / 1000)
    print(f'latst update date: {updateTime.isoformat()}')
    return create_network(data)


if __name__ == '__main__':
    G, nodes_color, node_labels = load_data(normal_url)
    draw(G,nodes_color,1,node_labels=None) # node_labels)


