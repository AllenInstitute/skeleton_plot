import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import LineCollection
from meshparty import meshwork, skeleton

from . import utils

axis_dict = {'x': 0, 'y': 1, 'z': 2}


def plot_verts(vertices, edges, radius = None, skel_colors = None, 
                color = 'darkslategray', title = '', line_width = 1,
                x = 'x', y = 'y',  plot_soma = False, soma_node = 0,
                soma_size = 120, skel_alpha = 1, invert_y = False, 
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
        skel_colors = utils.ensure_length(skel_colors, len(vertices))
    if radius is not None:
        radius = utils.ensure_length(radius, len(vertices), feature_name = 'radius')

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
        lc = LineCollection(segments, linewidths=linewidths, color=colors, capstyle = capstyle, joinstyle = joinstyle, 
                                    alpha = skel_alpha)
        ax.add_collection(lc)

    ax.set_aspect("equal")

    if plot_soma:
        if skel_colors is not None:
            soma_color = skel_color_map[1]
        else:
            soma_color = color
        ax.scatter(sk.root_position[x], sk.root_position[y], s = soma_size, c = soma_color, zorder = 2)

    utils.set_xy_lims(ax, verts = sk.vertices, invert_y = invert_y, 
                x_min_max = x_min_max, y_min_max = y_min_max, x = x, y = y)
    
    ax.set_title(title)


        

def plot_skel(sk: skeleton, title='', x = 'x', y = 'y', pull_radius = False, radius = None, 
                    line_width = 1, plot_soma = False, soma_size = 120, soma_node = None, 
                    invert_y = False, skel_colors = None, skel_alpha = 1,
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
    # make sure right shape 
    assert radius is None or len(radius) == len(sk.vertices), "Radius must be None or the same length as sk.vertices"

    if soma_node is None:
        soma_node = int(sk.root)

    plot_verts(sk.vertices, sk.edges, ax = ax, radius = radius, 
                skel_colors = skel_colors, title = title, skel_alpha = skel_alpha,
                line_width = line_width, x = x, y = y,  plot_soma = plot_soma, soma_node = soma_node,
                color = color, soma_size = soma_size, invert_y = invert_y, 
                skel_color_map = skel_color_map, x_min_max = x_min_max, 
                y_min_max = y_min_max, capstyle = capstyle, joinstyle = joinstyle
                )

def plot_mw_skel(mw: meshwork, plot_presyn = False, plot_postsyn = False, presyn_color = 'deepskyblue', 
                    postsyn_color = 'violet', presyn_size = 5, postsyn_size = 5, syn_res = [4,4,40],
                    presyn_alpha = 1, postsyn_alpha = 1, skel_alpha = 1,
                    title='', line_width = 1, x = 'x', y = 'y', radius = None, pull_radius = False, 
                    radius_anno = 'segment_properties', basal_anno = 'basal_mesh_labels', apical_anno = 'apical_mesh_labels', 
                    axon_anno = 'is_axon', plot_soma = False, soma_node = None, soma_size = 120, 
                    invert_y = False, skel_colors = None, pull_compartment_colors = False,  color = 'darkslategray',
                    skel_color_map = {3: "firebrick", 4: "salmon", 2: "steelblue", 1: "olive"},
                    x_min_max = None, y_min_max = None, capstyle = 'round', joinstyle = 'round',
                    pre_anno = {'pre_syn': 'pre_pt_position'}, post_anno = {'post_syn': 'post_pt_position'},
                    ax = None):
    """
    Plots a meshwork skeleton with optional synapse markers, compartment labels, radius plotting.

    Args:
    - mw (meshwork): The meshwork object containing the skeleton to be plotted.
    - plot_presyn (bool): Whether to plot presynaptic synapse markers.
    - plot_postsyn (bool): Whether to plot postsynaptic synapse markers.
    - presyn_color (str): Color of presynaptic synapse markers.
    - postsyn_color (str): Color of postsynaptic synapse markers.
    - presyn_size (int): Size of presynaptic synapse markers.
    - postsyn_size (int): Size of postsynaptic synapse markers. 
    - syn_res (list): Resolution of synapse markers. [4,4,40] for minnie, [9.7,9.7,45] for v1dd
    - presyn_alpha (float): Alpha opacity value of presynaptic synapse markers.
    - postsyn_alpha (float): Alpha opacity value of postsynaptic synapse markers.
    - skel_alpha (float): Alpha opacity value of skeleton lines.
    - title (str): Title of the plot.
    - line_width (int): Width of skeleton lines. also functions as a scalar of values found in meshwork when pull_radius is set to true
    - x (str): Name of x-axis.
    - y (str): Name of y-axis.
    - radius (float): Radius of skeleton lines.
    - pull_radius (bool): Whether to pull radius from meshwork.
    - radius_anno (str): Name of annotation containing radius information. contained in mw.anno
    - basal_anno (str): Name of annotation containing (basal) dendrite mesh labels. contained in mw.anno
    - apical_anno (str): Name of annotation containing apical mesh labels. can set to None if no apical. contained in mw.anno
    - axon_anno (str): Name of annotation containing axon information. contained in mw.anno
    - plot_soma (bool): Whether to plot soma.
    - soma_node (int): Index of soma node.
    - soma_size (int): Size of soma marker.
    - invert_y (bool): Whether to invert y-axis.
    - skel_colors (dict): Dictionary of skeleton colors.
    - pull_compartment_colors (bool): Whether to pull compartment colors from meshwork.
    - color (str): Color of skeleton lines.
    - skel_color_map (dict): Dictionary mapping compartment labels to colors.
    - x_min_max (tuple): Tuple of minimum and maximum x-axis values.
    - y_min_max (tuple): Tuple of minimum and maximum y-axis values.
    - capstyle (str): Cap style of skeleton lines.
    - joinstyle (str): Join style of skeleton lines.
    - pre_anno (dict): Dictionary of presynaptic annotation table and column names.
    - post_anno (dict): Dictionary of postsynaptic annotation table and column names.
    - ax (matplotlib.axes.Axes): Axes object to plot on.

    Returns:
    - None
    """
    if ax is None:
        ax = plt.gca()

    # pull out radius, compartments, soma node
    if skel_colors is None:
        if pull_compartment_colors:
            skel_colors = utils.pull_mw_skel_colors(mw, basal_anno, axon_anno, apical_anno)

    
    if radius is None:
        if pull_radius:
            radius = utils.pull_mw_rad(mw, radius_anno)


    sk = mw.skeleton

    if soma_node is None:
        soma_node = sk.root

    # add synapses

    if plot_presyn:
        pre_anno_table = list(pre_anno.keys())[0]
        pre_column = list(pre_anno.values())[0]
        presyn_verts = np.array([np.array(x) for x in (mw.anno[pre_anno_table][pre_column]).values])*syn_res
        plot_synapses(presyn_verts = presyn_verts, x = x, y = y, presyn_size = presyn_size, 
                postsyn_size = postsyn_size, presyn_color = presyn_color, postsyn_color = postsyn_color, 
                presyn_alpha = presyn_alpha, postsyn_alpha = postsyn_alpha, ax = ax)

    if plot_postsyn:
        post_anno_table = list(post_anno.keys())[0]
        post_column = list(post_anno.values())[0]
        postsyn_verts = np.array([np.array(x) for x in (mw.anno[post_anno_table][post_column]).values])*syn_res
        plot_synapses(postsyn_verts = postsyn_verts, x = x, y = y, presyn_size = presyn_size, 
                        postsyn_size = postsyn_size, presyn_color = presyn_color, postsyn_color = postsyn_color, 
                        presyn_alpha = presyn_alpha, postsyn_alpha = postsyn_alpha, ax = ax)
    
    # plot verts 
    plot_verts(sk.vertices, sk.edges, ax = ax, radius = radius,
                skel_colors = skel_colors, title = title, skel_alpha = skel_alpha,
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
        presyn_colors = utils.ensure_length(presyn_color, len(presyn_verts))
        ax.scatter(presyn_verts[:,x], presyn_verts[:,y], s = presyn_size, c = presyn_colors, alpha = presyn_alpha)
    if postsyn_verts is not None:
        postsyn_colors = utils.ensure_length(postsyn_color, len(postsyn_verts))
        ax.scatter(postsyn_verts[:,x], postsyn_verts[:,y], s = postsyn_size, c = postsyn_colors, alpha = postsyn_alpha)

    # utils.set_xy_lims(ax, verts = np.vstack((presyn_verts, postsyn_verts)), invert_y = invert_y, 
    #         x_min_max = x_min_max, y_min_max = y_min_max, x = x, y = y)


def plot_layer_lines(y_vals, ax = None, labels = None, buffer_space = .01, line_styles = None, x_min_max = None):
    """    
    takes a list of y values on which to plot horizontal line across the current x ax.
    Optionally, labels can be provided to label each line.

    Args:
        y_vals (list): y value for each line you wish to plot 
        x_vals (list, optional): x value for each line you wish to plot.
        ax (matplotlib.axes, optional): axis on which to plot the skeleton
            If none is given, will find current axis with plt.gca()
        labels (list, optional): list of str labels for each line. Defaults to None.
        buffer_space (float, optional): percentage of the x range of the plot to  
            have as a buffer between the edge of the plot to the layer labels.
            Defaults to .01.
        x_min_max (tuple, optional): manually specified x min and x max.
        line_styles (list, optional): list of dictionaries of line styles for each line.
    """
    
    if ax is None:
        ax = plt.gca()
    # get x vals
    if x_min_max is None:
        x_min_max = ax.get_xlim()
    

    if labels is None:
        labels = ['']*len(y_vals)

    if line_styles is None:
        line_styles = [{}]*len(y_vals)
    elif isinstance(line_styles, dict):
        line_styles = [line_styles] * len(y_vals)

    for y_val, label, style in zip(y_vals, labels, line_styles):
        ax.plot([x_min_max[0], x_min_max[1]], [y_val, y_val], **style)
        # add a buffer space between plot and labels
        buffer = buffer_space * (x_min_max[1] - x_min_max[0])
        ax.text(x_min_max[1] + buffer, y_val, label, verticalalignment='center')


def plot_layer_poly(layer_poly_json, ax = None, res = 0.3603, size = 1, invert_y = True):
    '''
    
    If you do not pass a soma id, it will plot the average layer bounds file. otherwise pass 
    soma id to plot the neuron and the custom layer bounds for that neuron. 

    '''
    if ax is None:
        ax = plt.gca()

    verts = np.empty((0,2))
    for key in layer_poly_json.keys():
        if key == 'layer_polygons':

            for layer in layer_poly_json[key]:
                bound = np.array(layer['path'])
                verts = np.vstack([verts,bound])
                ax.scatter(bound[:,0]*res, bound[:,1]*res, s = size)

        else:
            bound = np.array(layer_poly_json[key]['path'])
            verts = np.vstack([verts,bound])
        ax.scatter(bound[:,0]*res, bound[:,1]*res, s = size)
    utils.set_xy_lims(ax = ax, verts = verts*res, x = 'x', y = 'y', invert_y=invert_y)


def plot_skeleton_lineup(skel_list, depths = None, space_between = 0, figsize = (26,12), x = 'x',
                                  axis_lines = 'off', skel_colors = None, title = '', 
                                  pull_radius = False, radius = None, line_width = 1, 
                                  plot_soma = False, soma_size = 120, soma_node = None, invert_y = False, 
                                  skel_alpha = 1, pull_compartment_colors = False, 
                                  color = 'darkslategray', 
                                  skel_color_map = {3: "firebrick", 4: "salmon", 2: "steelblue", 1: "olive"},
                                  x_min_max = None, y_min_max = None, capstyle = 'round', joinstyle = 'round',
                                  ax = None, line_styles_depths = {"color": "gray", "linewidth": 1, "linestyle": "-"},
                                  buffer_space_depths = -1.3, 
                                  depths_labels = ['layer 2/3\nboundary', 'layer 4', 'layer 5', 'layer 6a', 'layer 6b', 'white matter']

                                 ):
    '''
    plots multiple skeletons one after the other on the same plot with optional depth lines

    skel_list (list): list of meshparty.skeleton.Skeleton objects
    depths (dict, optional): dictionary of depth values for each layer
    space_between (int float): blank space between skeletons in x
    figsize (tuple): size of the plot
    x (str, optional): which dimension to plot in x. x y or z. Defaults to 'x'.
    axis_lines (str, optional): whether to plot axis lines. Defaults to 'off'. passed in ax.axis(axis_lines)
    skel_colors (iterable, optional): map of numbers that indicate 
            color for each vertex recorded in skel_color_map. 
            Overwrites color argument. Defaults to None.
    title (str, optional): title to display on plot. Defaults to ''.
    pull_radius (bool, optional): whether or not to pull and plot the radius from 
        sk.vertex_properties['radius']. Defaults to False.
    radius (iterable, optional): radius of each vertex. overwritten if pull_radius.
        Defaults to None.
    line_width (int): Width of skeleton lines. also functions as a scalar of values found in meshwork when pull_radius is set to true
    plot_soma (bool, optional): whether or not to plot the soma. Defaults to False.
    soma_size (int, optional): size of soma node to display. Defaults to 120.
    soma_node (int, optional): the index of the soma node in sk.vertices. Defaults to 0.
    invert_y (bool, optional): whether or not to invert the y axis. Defaults to False.
    skel_alpha (float): Alpha opacity value of skeleton lines.
    pull_compartment_colors (bool, optional): whether to pull and plot the compartments in 
        sk.vertex_properties['compartment']. Defaults to False.
    color (str, optional): color of all vertices. Defaults to 'darkslategray'.
    skel_color_map (dict, optional): map of skel_colors values->colors. 
        Defaults to {3: "firebrick", 4: "salmon", 2: "steelblue", 1: "olive"}.
    x_min_max (tuple, optional): manually specified x min and x max. 
        Defaults to None, which will set x min and max to the limits of the vertices.
    y_min_max (tuple, optional): manually specified y min and x max. 
        Defaults to None, which will set y min and max to the limits of the vertices.
    capstyle (str, optional): shape of the endpoints. Defaults to 'round'.
    joinstyle (str, optional): shape of the points between linecollection pieces. 
        Defaults to 'round'.
    ax (matplotlib.axes, optional): axis on which to plot the skeleton
        If none is given, will find current axis with plt.gca()
    line_styles_depths (list, optional): list of dictionaries of line styles for each layer line.
    buffer_space (float, optional): percentage of the x range of the plot to  
            have as a buffer between the edge of the plot to the layer labels.
            Defaults to .01.
    depths_labels (list, optional): list of str labels for each layer. Defaults to None.

    '''
    if ax is None:
        ax = plt.gca()
    x_max = 0
    x_min = 0
    x_max = 0
    
    x_ax = axis_dict[x]

    if depths is not None:
        depths_vals = depths.values()
    
    for skel in skel_list:
        
        current_min = min(skel.vertices[:,x_ax])
        x_offset = space_between + x_max - current_min
        
        x_offset_add = [0,0,0]
        x_offset_add[x_ax] = x_offset
        
        skel._vertices = skel.vertices + x_offset_add
        
        if x_min_max is None:
            x_min = min(x_min, min(skel.vertices[:,x_ax]))
            x_max = max(x_max, max(skel.vertices[:,x_ax]) + space_between)
        
        plot_skel(skel, title=title, x = x, y = 'y', pull_radius = pull_radius, radius = radius, 
                line_width = line_width, plot_soma = plot_soma, soma_size = soma_size, soma_node = soma_node, 
                invert_y = invert_y, skel_colors = skel_colors, skel_alpha = skel_alpha,
                pull_compartment_colors = pull_compartment_colors, color = color,
                skel_color_map = skel_color_map, x_min_max = x_min_max, y_min_max = y_min_max, 
                capstyle = capstyle, joinstyle = joinstyle, ax = ax)
        if depths is not None:
            plot_layer_lines(depths_vals, ax = ax, 
                    line_styles = line_styles_depths,
                    buffer_space = buffer_space_depths, labels = depths_labels, x_min_max = [x_min, x_max])

            
        depths_labels = None
        
        # prevent invert_y from flipping it over and over lol


    if y_min_max is None:
        y_min, y_max = ax.get_ybound()
    else:
        y_min, y_max = y_min_max
    utils.set_xy_lims(ax, invert_y = invert_y, x_min_max = [x_min, x_max], y_min_max = [y_min, y_max])
    ax.axis(axis_lines)
