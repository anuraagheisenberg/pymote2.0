
# built-in packages
import time
import sys
import datetime

# external packages
import scipy as sp
import numpy as np
from em import expectation_maximization
from numpy import sign, sqrt, array, pi, sin, cos
from numpy.random import rand,seed
import networkx as nx
from networkx.algorithms import approximation as approx

# internal packages
from pymote import *
from pymote.conf import global_settings
from toplogies import Topology
from pymote import propagation
from pymote.utils import plotter
from pymote.utils.filing import get_path, date2str,\
     DATA_DIR, TOPOLOGY_DIR, CHART_DIR, DATETIME_DIR


# Network/Environment setup
seed(123)  # to get same random sequence for each run so that simulation can be reproduce

# Network/Environment setup
global_settings.ENVIRONMENT2D_SHAPE = (500, 500) # desired network size for simulation
global_settings.COMM_RANGE = 43.857

net = Network()
h, w = net.environment.im.shape
propagation.PropagationModel.P_TX = 0.0144  # Node Tx Power

max_n = 100  # max no. of nodes
clusters = 10
x_radius = 0.9*global_settings.COMM_RANGE
y_radius = 0.9*global_settings.COMM_RANGE

n_power = []
t_power = []
n_range = np.arange(20, max_n+1, 10)
start_time = time.time()
methods = ['EM', 'K-means']
methods2 = ['EM new', 'EM']
folder = DATETIME_DIR+ "-" + "Experiment 1"
energy = np.zeros((2, 9))
eff = np.zeros((2, 9))
kk=0
for n in n_range:
    # network topology setup
    Node.cid = 1
    net_gen = Topology(n_count=n, connected=True)
    #net  = net_gen.generate_cluster_network(name="",
    #           x_radius=x_radius, y_radius=y_radius,  sector=0.7,
    #           cluster_divide=4, randomness=4.8)
    net = net_gen.generate_gaussian_network(name='', randomness=1)
    #net = net_gen.generate_grid_network(name="Randomized Grid", randomness=0.7, p_anchors=None)

    for m in range(2):
        method = methods[m]
        net, p_nk = net_gen.get_clusters(net, clusters=clusters, method=method)

        net.name = "Energy Efficient Clustering-%s\nN=%s, K=%s" \
                %(methods2[m], n, clusters)


        filename = net.name.replace("\n", "-")
        # saving topology as PNG image
        net.savefig(fname=get_path(folder, filename),   title=net.name,
                    xlabel="X-coordinate (m)", ylabel="Y-coordinate (m)",
                    show_labels=True, format="pdf")
        print net.__len__(), len(net)
        # tn = net.neighbors(net.nodes()[1])
        # print len(tn), tn
        # bfs = list(nx.bfs_tree(net, net.nodes()[1]))
        # print bfs, len(bfs)
        # print net.nodes()[34].commRange
        p=nx.shortest_path_length(net)
        print len(p), p
        total=1e-3
        nn = len(net)-clusters
        print len(p_nk), p_nk[0][0]
        for i in range(nn):
            for k in range(clusters):
                if net.nodes()[i] in p and net.nodes()[nn + k] in p[net.nodes()[i]]:
                    #print list(nx.shortest_simple_paths(net, net.nodes()[i], net.nodes()[nn + k]))[0]
                    for h in range(p[net.nodes()[i]][net.nodes()[nn + k]]):
                        p1 = net.pos[net.nodes()[i]]
                        p2 = net.pos[net.nodes()[nn + k]]
                        d = sqrt(sum(pow(p1 - p2, 2)))
                        total += p_nk[i][k] * d * d
                        #total += 6 * p_nk[i][k]*net.nodes()[k].commRange * net.nodes()[k].commRange

        e_req = []
        for c in np.arange(0.2,1.1,0.2):
            e_req.append(clusters * nn * net.nodes()[1].commRange * net.nodes()[1].commRange * c)

        n_power.append((n, total, len(p)/total, e_req[0], e_req[1],e_req[2], e_req[3], e_req[4]))
        energy[m, kk] = total
        eff[m, kk] = len(p)/total
        print n_power
        net.reset()
    kk += 1

# save data to text file for further analysis
end_time = time.time() - start_time
print("Execution time:  %s seconds ---" % round(end_time,2) )
print net_gen.name
sp.savetxt(get_path(folder, "Energy Consumption.csv"),
           n_power,
           delimiter="\t", fmt="%s",
           header="Nodes\tEnergy(m^2)\tefficeincy",
           comments='')

# plotter.plots(n_range, [e[1]/10e6 for e in n_power],
#               get_path(folder, "Energy"),
#               title="Energy Consumption",
#               more_plots=[[e[3]/10e6 for e in n_power], [e[6]/10e6 for e in n_power]],
#               labels=["Edat","Ereq(0.2)","Ereq(0.8)"],
#               xlabel="Number of nodes", ylabel="Energy ($10^6 m^2$)")

print np.array(list(energy[0,:]))
print n_range
plotter.plots(n_range, np.array(energy[0,:]/1e6),
              get_path(folder, "Energy"),
              title="Energy Consumption",
              more_plots=[np.array(energy[1,:])/1e6],
              labels=["Edat (new EM)","Edat (EM)"],
              xlabel="Number of nodes", ylabel="Energy ($10^6 m^2$)")

plotter.plots(n_range, np.array(eff[0,:]/1e-4),
              get_path(folder, "Efficiency"),
              more_plots=[np.array(eff[1,:])/1e-4],
              title="Efficiency",
              labels=["Efficeincy (new EM)","Efficeincy (EM)"],
              xlabel="Number of Nodes", ylabel="Efficiency ($10^{-4}$)")
