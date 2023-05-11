import pandas as pd
import numpy as np
from meshparty import skeleton, meshwork
from . import utils
import matplotlib.pyplot as plt

from matplotlib.collections import LineCollection

axis_dict = {'x': 0, 'y': 1, 'z': 2}

def plot_verts(vertices, edges, radius = None, skel_colors = None, 
                color = 'darkslategray', title = '', line_width = 1,
                x = 'x', y = 'y',  plot_soma = False, soma_node = 0,
                soma_size = 120, invert_y = False, 
                skel_color_map = {3: "firebrick", 4: "salmon", 2: "steelblue", 1: "olive"},
                x_min_max = None, y_min_max = None, capstyle = 'round', joinstyle = 'round',
                ax = None):
    """plots skeleton vertices and edges with various options 

    Args:
        vertices (np.array, nx2+): vertices to plot. nx2+. If nx3, possible to specify 
            which of the three axes are plotted in x and y arguments.
        edges (np.array, nx2): edges between specified vertices
        radius (iterable, optional): radius of each vertex. Defaults to None.
        line_width (int, optional): if no radius passed, line_width will be the width 
            of every node in the plot. if radius are passed, those values will be 
            multiplied by line_width. Defaults to 1.
        skel_colors (iterable, optional): map of numbers that indicate 
            color for each vertex recorded in skel_color_map. 
            Overwrites color argument. Defaults to None.
        skel_color_map (dict, optional): map of skel_colors values->colors. 
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
        ax (matplotlib.axes._subplots.AxesSubplot, optional): axis on which to plot the skeleton.
            If none is given, will find current axis with plt.gca()

    """    
    
    if ax is None:
        ax = plt.gca()


    sk=skeleton.Skeleton(vertices, edges, vertex_properties={'radius':pd.Series(radius), 
                                            'compartment':pd.Series(skel_colors)}, root=soma_node,
                                            remove_zero_length_edges=False)

    if skel_colors is not None: 
        if len(skel_colors) != len(vertices):
            raise ValueError('length of skel_colors must match len of vertices')
    if radius is not None:
        if len(radius) != len(vertices):
            raise ValueError('length of radius must match len of vertices')

    x, y = axis_dict[x], axis_dict[y]

    for cover_path in sk.cover_paths_with_parent():
        
        if skel_colors is None:
            colors = [color]*len(cover_path)
        else:
            colors = [skel_color_map[x] for x in sk.vertex_properties['compartment'][cover_path].values]
        if radius is None:
            linewidths  = pd.Series([line_width]*len(cover_path))
        else:
            linewidths = (sk.vertex_properties['radius'][cover_path])*line_width

        path_verts = sk.vertices[cover_path][:,[x, y]]

        segments = np.concatenate([path_verts[:-1], path_verts[0:-1], path_verts[1:]], axis=1).reshape(len(path_verts)-1,3,2)
        lc = LineCollection(segments, linewidths=linewidths, color=colors, capstyle = capstyle, joinstyle = joinstyle)
        ax.add_collection(lc)

    ax.set_aspect("equal")

    if plot_soma:
        if skel_colors is not None:
            soma_color = skel_color_map[1]
        else:
            soma_color = color
        ax.scatter(sk.root_position[x], sk.root_position[y], s = soma_size, c = soma_color, zorder = 2)

    
    utils._set_xy_lims(ax, verts = sk.vertices, invert_y = invert_y, 
                x_min_max = x_min_max, y_min_max = y_min_max, x = x, y = y)
    
    ax.set_title(title)


        

def plot_skel(sk: skeleton, title='', x = 'x', y = 'y', pull_radius = False, radius = None, 
                    line_width = 1, plot_soma = False, soma_size = 120, soma_node = 0, 
                    invert_y = False, skel_colors = None, 
                    pull_compartment_colors = False, color = 'darkslategray',
                    skel_color_map = {3: "firebrick", 4: "salmon", 2: "steelblue", 1: "olive"},
                    x_min_max = None, y_min_max = None, capstyle = 'round', joinstyle = 'round',
                    ax = None):
    """plots a skeleton object. attempts to pull out arguments from skeleton and plot with plot_verts

    Args:
        sk (skeleton): (meshparty.skeleton.Skeleton): skeleton to be plotted 
        title (str, optional): title to display on plot. Defaults to ''.
        x (str, optional): which dimension to plot in x. x y or z. Defaults to 'x'.
        y (str, optional): which dimension to plot in y. x y or z. Defaults to 'y'.
        pull_radius (bool, optional): whether or not to pull and plot the radius from 
            sk.vertex_properties['radius']. Defaults to False.
        radius (iterable, optional): radius of each vertex. overwritten if pull_radius.
            Defaults to None.
        plot_soma (bool, optional): whether or not to plot the soma. Defaults to False.
        soma_size (int, optional): size of soma node to display. Defaults to 120.
        soma_node (int, optional): the index of the soma node in sk.vertices. Defaults to 0.
        invert_y (bool, optional): whether or not to invert the y axis. Defaults to False.
        pull_compartment_colors (bool, optional): whether to pull and plot the compartments in 
            sk.vertex_properties['compartment']. Defaults to False.
        skel_colors (iterable, optional): map of numbers that indicate 
            color for each vertex recorded in skel_color_map. 
            Overwrites color argument. Defaults to None.
        skel_color_map (dict, optional): map of skel_colors values->colors. 
            Defaults to {3: "firebrick", 4: "salmon", 2: "steelblue", 1: "olive"}.
        color (str, optional): color of all vertices. Defaults to 'darkslategray'.
        x_min_max (tuple, optional): manually specified x min and x max. 
            Defaults to None, which will set x min and max to the limits of the vertices.
        y_min_max (tuple, optional): manually specified y min and x max. 
            Defaults to None, which will set y min and max to the limits of the vertices.
        capstyle (str, optional): shape of the endpoints. Defaults to 'round'.
        joinstyle (str, optional): shape of the points between linecollection pieces. 
            Defaults to 'round'.
        ax (matplotlib.axes, optional): axis on which to plot the skeleton
            If none is given, will find current axis with plt.gca()
    """    
    if ax is None:
        ax = plt.gca()

    if skel_colors is None:
        if pull_compartment_colors:
            skel_colors = sk.vertex_properties['compartment']

    if pull_radius:
        radius = sk.vertex_properties['radius']
    else:
        radius = None

    plot_verts(sk.vertices, sk.edges, ax = ax, radius = radius, 
                skel_colors = skel_colors, title = title, 
                line_width = line_width, x = x, y = y,  plot_soma = plot_soma, soma_node = soma_node,
                color = color, soma_size = soma_size, invert_y = invert_y, 
                skel_color_map = skel_color_map, x_min_max = x_min_max, 
                y_min_max = y_min_max, capstyle = capstyle, joinstyle = joinstyle
                )

def plot_mw_skel(mw: meshwork, plot_presyn = False, plot_postsyn = False, presyn_color = 'deepskyblue', 
                    postsyn_color = 'violet', presyn_size = 5, postsyn_size = 5, syn_res = [4,4,40],
                    presyn_alpha = 1, postsyn_alpha = 1,
                    title='', line_width = 1, x = 'x', y = 'y', radius = None, pull_radius = False, 
                    radius_anno = 'segment_properties', basal_anno = 'basal_mesh_labels', apical_anno = 'apical_mesh_labels', 
                    axon_anno = 'is_axon', plot_soma = False, soma_node = None, soma_size = 120, 
                    invert_y = False, skel_colors = None, pull_compartment_colors = False,  color = 'darkslategray',
                    skel_color_map = {3: "firebrick", 4: "salmon", 2: "steelblue", 1: "olive"},
                    x_min_max = None, y_min_max = None, capstyle = 'round', joinstyle = 'round',
                    pre_anno = {'pre_syn': 'pre_pt_position'}, post_anno = {'post_syn': 'post_pt_position'},
                    ax = None):

    if ax is None:
        ax = plt.gca()

    # pull out radius, compartments, soma node
    if skel_colors is None:
        if pull_compartment_colors:
            skel_colors = utils.pull_mw_skel_colors(mw, basal_anno, apical_anno, axon_anno)

    
    if radius is None:
        if pull_radius:
            radius = utils.pull_mw_rad(mw, radius_anno)


    sk = mw.skeleton

    if plot_soma and soma_node is None:
        soma_node = sk.root

    # add synapses

    if plot_presyn:
        pre_anno_table = list(pre_anno.keys())[0]
        pre_column = list(pre_anno.values())[0]
        presyn_verts = np.array([np.array(x) for x in (mw.anno[pre_anno_table][pre_column]).values])*syn_res

    if plot_postsyn:
        post_anno_table = list(post_anno.keys())[0]
        post_column = list(post_anno.values())[0]
        postsyn_verts = np.array([np.array(x) for x in (mw.anno[post_anno_table][post_column]).values])*syn_res

    plot_synapses(presyn_verts = presyn_verts, postsyn_verts = postsyn_verts, x = x, y = y, presyn_size = presyn_size, 
                    postsyn_size = postsyn_size, presyn_color = presyn_color, postsyn_color = postsyn_color, 
                    presyn_alpha = presyn_alpha, postsyn_alpha = postsyn_alpha, ax = ax)
    
    # plot verts 
    plot_verts(sk.vertices, sk.edges, ax = ax, radius = radius,
                skel_colors = skel_colors, title = title, 
                line_width = line_width, x = x, y = y,  plot_soma = plot_soma, soma_node = soma_node,
                color = color, soma_size = soma_size, invert_y = invert_y, 
                skel_color_map = skel_color_map, x_min_max = x_min_max, 
                y_min_max = y_min_max, capstyle = capstyle, joinstyle = joinstyle,
                )

def plot_synapses(presyn_verts = None, postsyn_verts = None, x = 'x', y = 'y', 
                    presyn_size = 5, postsyn_size = 5, presyn_color = 'deepskyblue', 
                    postsyn_color = 'violet', presyn_alpha = 1, postsyn_alpha = 1,
                    x_min_max = None, y_min_max = None, title=None, invert_y = False, 
                    ax = None
                    ):
    """plots presynaptic and postsynaptic sites on ax

    Args:
        presyn_verts (array, optional): vertices for each presyn point to be plotted. 
            Defaults to None.
        postsyn_verts (array, optional): vertices for each presyn point to be plotted. 
            Defaults to None.
        x (str, optional): which dimension to plot in x. x y or z. Defaults to 'x'.
        y (str, optional): which dimension to plot in y. x y or z. Defaults to 'y'.
        presyn_size (int or array, optional): size(s) for presynaptic points. 
            Defaults to 5.
        postsyn_size (int or array, optional): size(s) for postsynaptic points.  
            Defaults to 5.
        presyn_color (str, optional): color for presynaptic points. 
            Defaults to 'deepskyblue'.
        postsyn_color (str, optional): color for postsynaptic points. 
            Defaults to 'violet'.
        presyn_alpha (int, optional): opacity for presynaptic points. 
            between 0(transparent) and 1(opaque). Defaults to 1.
        postsyn_alpha (int, optional): opacity for presynaptic points. 
            between 0(transparent) and 1(opaque). Defaults to 1.
        x_min_max (tuple, optional): manually specified x min and x max. 
            Defaults to None, which will set x min and max to the limits of the vertices.
        y_min_max (tuple, optional): manually specified y min and x max. 
            Defaults to None, which will set y min and max to the limits of the vertices.
        title (str, optional): title to display on plot. Defaults to ''.
        ax (matplotlib.axes, optional): axis on which to plot the skeleton
            If none is given, will find current axis with plt.gca()
    """   
    x, y = axis_dict[x], axis_dict[y]

    if presyn_verts is not None:
        ax.scatter(presyn_verts[:,x], presyn_verts[:,y], s = presyn_size, c = presyn_color, alpha = presyn_alpha)
    if postsyn_verts is not None:
        ax.scatter(postsyn_verts[:,x], postsyn_verts[:,y], s = postsyn_size, c = postsyn_color, alpha = postsyn_alpha)

    utils._set_xy_lims(ax, verts = np.vstack((presyn_verts, postsyn_verts)), invert_y = invert_y, 
            x_min_max = x_min_max, y_min_max = y_min_max, x = x, y = y)


def plot_layer_lines(y_vals, ax = None, labels = None, buffer_space = .01):
    """    
    takes a list of y values on which to plot horizontal line across the current x ax.
    Optionally, labels can be provided to label each line.

    Args:
        y_vals (list): y value for each line you wish to plot 
        ax (matplotlib.axes, optional): axis on which to plot the skeleton
            If none is given, will find current axis with plt.gca()
        labels (list, optional): list of str labels for each line. Defaults to None.
        buffer_space (float, optional): percentage of the x range of the plot to  
            have as a buffer between the edge of the plot to the layer labels.
            Defaults to .01.
    """
    
    if ax is None:
        plt.gca()
    # get x vals
    x_vals = ax.get_xlim()

    if labels is None:
        for y_val in y_vals:
            ax.plot([x_vals[0], x_vals[1]], [y_val, y_val])
    else:
        # if labels are provided, add them to the lines
        for y_val, label in zip(y_vals, labels):
            ax.plot([x_vals[0], x_vals[1]], [y_val, y_val])
            # add a buffer space between plot and labels
            buffer = buffer_space * (x_vals[1] - x_vals[0])
            ax.text(x_vals[1] + buffer, y_val, label, verticalalignment='center')
        


