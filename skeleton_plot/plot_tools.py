import pandas as pd
import numpy as np
from meshparty import skeleton, meshwork
from . import utils

from matplotlib.collections import LineCollection



def plot_verts(ax, vertices, edges, radii = None, skeleton_colors = None, 
                color = 'darkslategray', title = '', line_width = 1,
                x = 'x', y = 'y',  plot_soma = False, soma_node = 0,
                soma_size = 120, invert_y = False, 
                skel_color_map = {3: "firebrick", 4: "salmon", 2: "steelblue", 1: "olive"},
                x_min_max = None, y_min_max = None, capstyle = 'round', joinstyle = 'round'
                ):
    """plots skeleton vertices and edges with various options 

    Args:
        ax (matplotlib.axes._subplots.AxesSubplot): axis on which to plot the skeleton
        vertices (np.array, nx2+): vertices to plot. nx2+. If nx3, possible to specify 
            which of the three axes are plotted in x and y arguments.
        edges (np.array, nx2): edges between specified vertices
        radii (iterable, optional): radius of each vertex. Defaults to None.
        line_width (int, optional): if no radii passed, line_width will be the width 
            of every node in the plot. if radii are passed, those values will be 
            multiplied by line_width. Defaults to 1.
        skeleton_colors (iterable, optional): map of numbers that indicate 
            color for each vertex recorded in skel_color_map. 
            Overwrites color argument. Defaults to None.
        skel_color_map (dict, optional): map of skeleton_colors values->colors. 
            Defaults to {3: "firebrick", 4: "salmon", 2: "steelblue", 1: "olive"}.
        color (str, optional): color of all vertices. Defaults to 'darkslategray'.
        title (str, optional): title to display on plot. Defaults to ''.
        x (str, optional): which dimension to plot in x. x y or z. Defaults to 'x'.
        y (str, optional): which dimension to plot in y. x y or z. Defaults to 'y'.
        plot_soma (bool, optional): whether or not to plot the soma. Defaults to False.
        soma_node (int, optional): which node in the skeleton represents the soma. 
            Defaults to 0.
        soma_size (int, optional): what size the some should be on graph. 
            Defaults to 120.
        invert_y (bool, optional): whether or not to invert the y axis. 
            Defaults to False.
        x_min_max (tuple, optional): manually specified x min and x max. 
            Defaults to None, which will set x min and max to the limits of the vertices.
        y_min_max (tuple, optional): manually specified y min and x max. 
            Defaults to None, which will set y min and max to the limits of the vertices.
        capstyle (str, optional): shape of the endpoints. Defaults to 'round'.
        joinstyle (str, optional): shape of the points between linecollection pieces. 
            Defaults to 'round'.

    """    
    
    


    sk=skeleton.Skeleton(vertices, edges, vertex_properties={'radius':pd.Series(radii), 
                                            'compartment':pd.Series(skeleton_colors)}, root=soma_node,
                                            remove_zero_length_edges=False)

    if skeleton_colors is not None: 
        if len(skeleton_colors) != len(vertices):
            raise ValueError('length of skeleton_colors must match len of vertices')
    if radii is not None:
        if len(radii) != len(vertices):
            raise ValueError('length of radii must match len of vertices')

    if invert_y:    
        ax.invert_yaxis()

    axis_dict = {'x': 0, 'y': 1, 'z': 2}
    x, y = axis_dict[x], axis_dict[y]

    for cover_path in sk.cover_paths_with_parent():
        
        if skeleton_colors is None:
            colors = [color]*len(cover_path)
        else:
            colors = [skel_color_map[x] for x in sk.vertex_properties['compartment'][cover_path].values]
        if radii is None:
            linewidths  = pd.Series([line_width]*len(cover_path))
        else:
            linewidths = (sk.vertex_properties['radius'][cover_path])*line_width

        path_verts = sk.vertices[cover_path][:,[x, y]]

        segments = np.concatenate([path_verts[:-1], path_verts[0:-1], path_verts[1:]], axis=1).reshape(len(path_verts)-1,3,2)
        lc = LineCollection(segments, linewidths=linewidths, color=colors, capstyle = capstyle, joinstyle = joinstyle)
        ax.add_collection(lc)

    ax.set_aspect("equal")

    if plot_soma:
        if skeleton_colors is not None:
            soma_color = skel_color_map[1]
        else:
            soma_color = color
        print(sk.root_position[x], sk.root_position[y])
        ax.scatter(sk.root_position[x], sk.root_position[y], s = soma_size, c = soma_color, zorder = 2)

    if x_min_max:
        ax.set_xlim(x_min_max[0], x_min_max[1])
    if x_min_max and invert_y:
        ax.set_ylim(y_min_max[1], y_min_max[0])
    elif x_min_max:
        ax.set_ylim(y_min_max[0], y_min_max[1])
    elif x_min_max is None and y_min_max is None:
        verts = sk.vertices
        if invert_y:
            ax.set_ylim(max(verts[:,y]), min(verts[:,y]))
        else:
            ax.set_ylim(min(verts[:,y]), max(verts[:,y]))
        ax.set_xlim(min(verts[:,x]), max(verts[:,x]))

    
    ax.set_title(title)
        

def plot_skel(ax, sk: skeleton, title='', x = 'x', y = 'y', pull_radius = False, radii = None, 
                    line_width = 1, plot_soma = False, soma_size = 120, soma_node = 0, 
                    invert_y = False, skeleton_colors = None, 
                    pull_compartment_colors = False, color = 'darkslategray',
                    skel_color_map = {3: "firebrick", 4: "salmon", 2: "steelblue", 1: "olive"},
                    x_min_max = None, y_min_max = None, capstyle = 'round', joinstyle = 'round'):
    """plots a skeleton object. attempts to pull out arguments from skeleton and plot with plot_verts

    Args:
        ax (matplotlib.axes): axis on which to plot the skeleton
        sk (skeleton): (meshparty.skeleton.Skeleton): skeleton to be plotted 
        title (str, optional): title to display on plot. Defaults to ''.
        x (str, optional): which dimension to plot in x. x y or z. Defaults to 'x'.
        y (str, optional): which dimension to plot in y. x y or z. Defaults to 'y'.
        pull_radius (bool, optional): whether or not to pull and plot the radius from 
            sk.vertex_properties['radius']. Defaults to False.
        radii (iterable, optional): radius of each vertex. overwritten if pull_radius.
            Defaults to None.
        plot_soma (bool, optional): whether or not to plot the soma. Defaults to False.
        soma_size (int, optional): size of soma node to display. Defaults to 120.
        soma_node (int, optional): the index of the soma node in sk.vertices. Defaults to 0.
        invert_y (bool, optional): whether or not to invert the y axis. Defaults to False.
        pull_compartment_colors (bool, optional): whether to pull and plot the compartments in 
            sk.vertex_properties['compartment']. Defaults to False.
        skeleton_colors (iterable, optional): map of numbers that indicate 
            color for each vertex recorded in skel_color_map. 
            Overwrites color argument. Defaults to None.
        skel_color_map (dict, optional): map of skeleton_colors values->colors. 
            Defaults to {3: "firebrick", 4: "salmon", 2: "steelblue", 1: "olive"}.
        color (str, optional): color of all vertices. Defaults to 'darkslategray'.
        x_min_max (tuple, optional): manually specified x min and x max. 
            Defaults to None, which will set x min and max to the limits of the vertices.
        y_min_max (tuple, optional): manually specified y min and x max. 
            Defaults to None, which will set y min and max to the limits of the vertices.
        capstyle (str, optional): shape of the endpoints. Defaults to 'round'.
        joinstyle (str, optional): shape of the points between linecollection pieces. 
            Defaults to 'round'.
    """    
    

    if skeleton_colors is None:
        if pull_compartment_colors:
            skeleton_colors = sk.vertex_properties['compartment']

    if pull_radius:
        radii = sk.vertex_properties['radius']
    else:
        radii = None

    plot_verts(ax, sk.vertices, sk.edges, radii = radii, 
                skeleton_colors = skeleton_colors, title = title, 
                line_width = line_width, x = x, y = y,  plot_soma = plot_soma, soma_node = soma_node,
                color = color, soma_size = soma_size, invert_y = invert_y, 
                skel_color_map = skel_color_map, x_min_max = x_min_max, 
                y_min_max = y_min_max, capstyle = capstyle, joinstyle = joinstyle
                )

def plot_mw_skel(ax, mw: meshwork, plot_presyn = False, plot_postsyn = False, presyn_color = 'deepskyblue', 
                    postsyn_color = 'violet', presyn_size = 5, postsyn_size = 5, presyn_alpha = 1, postsyn_alpha = 1,
                    title='', line_width = 1, x = 'x', y = 'y', radii = None, pull_radius = False, 
                    radius_anno = 'segment_properties', basal_anno = 'basal_mesh_labels', apical_anno = 'apical_mesh_labels', 
                    axon_anno = 'is_axon', plot_soma = False, soma_node = None, soma_size = 120, 
                    invert_y = False, skel_colors = None, pull_compartment_colors = False,  color = 'darkslategray',
                    skel_color_map = {3: "firebrick", 4: "salmon", 2: "steelblue", 1: "olive"},
                    x_min_max = None, y_min_max = None, capstyle = 'round', joinstyle = 'round',
                    ):

    # pull out radius, compartments, soma node
    if skel_colors is None:
        if pull_compartment_colors:
            skel_colors = utils.pull_mw_skel_colors(mw, basal_anno, apical_anno, axon_anno)

    
    if radii is None:
        if pull_radius:
            radii = utils.pull_mw_rad(mw, radius_anno)


    sk = mw.skeleton

    if plot_soma and soma_node is None:
        soma_node = sk.root

    
    # use that information to plot verts 
    plot_verts(ax, sk.vertices, sk.edges, radii = radii,
                skeleton_colors = skel_colors, title = title, 
                line_width = line_width, x = x, y = y,  plot_soma = plot_soma, soma_node = soma_node,
                color = color, soma_size = soma_size, invert_y = invert_y, 
                skel_color_map = skel_color_map, x_min_max = x_min_max, 
                y_min_max = y_min_max, capstyle = capstyle, joinstyle = joinstyle
                )

    # add synapses
    if plot_presyn:
        presyns = np.array([np.array(x) for x in (mw.anno.pre_syn['pre_pt_position']).values])
        ax.scatter(presyns[:,0]*4, presyns[:,1]*4, s = presyn_size, c = presyn_color, alpha = presyn_alpha)
    if plot_postsyn:
        postsyns = np.array([np.array(x) for x in (mw.anno.post_syn['post_pt_position']).values])
        ax.scatter(postsyns[:,0]*4, postsyns[:,1]*4, s = postsyn_size, c = postsyn_color, alpha = postsyn_alpha)





