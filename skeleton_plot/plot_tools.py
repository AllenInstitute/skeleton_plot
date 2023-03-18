import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from meshparty import skeleton, meshwork
import seaborn as sns
from cloudfiles import CloudFiles
import os
import io
from . import utils

from caveclient import CAVEclient
from matplotlib.collections import LineCollection


SWC_COLUMNS = ('id', 'type', 'x', 'y', 'z', 'radius', 'parent',)
COLUMN_CASTS = {
    'id': int,
    'parent': int,
    'type': int
}

def read_depths(cloudpath, filename):
    '''
    enter cloudpath location of layer depths .json file 
    
    Parameters
    ----------
    cloudpath: directory location of layer file. in cloudpath format as seen in 
        https://github.com/seung-lab/cloud-files
    filename: full json filename 
    ''' 
    cf = CloudFiles(cloudpath)
    depths = cf.get_json(filename)

    if depths is None:
        if filename not in list(cf):
            raise FileNotFoundError(f"filename '{filename}' not found in '{cloudpath}'")
        else:
            raise ValueError('unable to retrieve file')

    return cf.get_json(filename)

# will be moved to meshparty?
def read_skeleton(cloudfile_dir, filename,
                 df = None):
    """reads skeleton file from cloudfiles style path

    Args:
        cloudfile_dir (str): _description_
        filename (str): _description_
        df (pd.DataFrame, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    if '://' not in cloudfile_dir:
        cloudfile_dir = 'file://' + cloudfile_dir
    file_path = os.path.join(cloudfile_dir, filename)
    df = read_swc(file_path)
    if not all(df.index == df['id']):
        # remap id and parent to index to 
        id_map = dict(zip(df['id'], df.index))
        id_map[-1] = -1
        df['id'] = [id_map[x] for x in df['id']]
        df['parent'] = [id_map[x] for x in df['parent']]
        
        
    verts = df[['x','y','z']].values
    edges = df[['id','parent']].iloc[1:].values
    
    sk=skeleton.Skeleton(verts, edges, vertex_properties={'radius':df['radius'], 
                                            'compartment':df['type']}, root=0,
                                            remove_zero_length_edges=False)
    return sk

# to meshparty?
def read_swc(path, columns=SWC_COLUMNS, sep=' ', casts=COLUMN_CASTS):
    """Read an swc file into a pandas dataframe

    Args:
        path (str): path to swc. if cloud path, use https://storage.googleapis.com/path_here
        columns (tuple, optional): column labels for swc file. Defaults to ('id', 'type', 'x', 'y', 'z', 'radius', 'parent').
        sep (str, optional): separator when reading swc into df. Defaults to ' '.
        casts (dict, optional): type casts for columns in swc. Defaults to {'id': int,'parent': int,'type': int}.

    Returns:
        df (pd.DataFrame): dataframe of swc data
    """    
    if "://" not in path:
        path = "file://" + path

    df = pd.read_csv(path, names=columns, comment='#', sep=sep)
    utils.apply_casts(df, casts)
    return df



def load_mw(filename, folder_path):
    
    # filename = f"{root_id}_{nuc_id}/{root_id}_{nuc_id}.h5"
    
    cf = CloudFiles(folder_path)
    binary = cf.get([filename])

    with io.BytesIO(cf.get(binary[0]['path'])) as f:
        f.seek(0)
        mw = meshwork.load_meshwork(f)

    return mw


def plot_verts(ax, vertices, edges, radii = None, skeleton_colors = None, title = '', line_width = 1,
                 x = 'x', y = 'y',  plot_soma = False, soma_node = 0,
                color = 'darkslategray', soma_size = 120, invert_y = False, 
                skel_color_map = {3: "firebrick", 4: "salmon", 2: "steelblue", 1: "olive"},
                x_min_max = None, y_min_max = None, capstyle = 'round', joinstyle = 'round'
                ):

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

    for cover_path in sk.cover_paths:
        
        if skeleton_colors is None:
            colors = [color]*len(cover_path)
        else:
            colors = [skel_color_map[x] for x in sk.vertex_properties['compartment'][cover_path].values]
        if radii is None:
            linewidths  = pd.Series([line_width]*len(cover_path))
        else:
            linewidths = (sk.vertex_properties['radius'][cover_path])*line_width

        path_verts = sk.vertices[cover_path][:,[x, y]]

        segments = np.concatenate([path_verts[:-2], path_verts[1:-1], path_verts[2:]], axis=1).reshape(len(path_verts)-2,3,2)
        lc = LineCollection(segments, linewidths=linewidths, color=colors, capstyle = capstyle, joinstyle = joinstyle)
        ax.add_collection(lc)
    ax.set_aspect("equal")

    if plot_soma:
        if skeleton_colors is not None:
            soma_color = skel_color_map[1]
        else:
            soma_color = color
        
        plt.scatter(sk.root_position[x], sk.root_position[y], s = soma_size, c = soma_color, zorder = 2)

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

    
    sns.despine(left=True, bottom=True)
    ax.set_title(title)
        

def plot_skel(ax, sk: skeleton, title='', line_width = 1, x = 'x', y = 'y', plot_radius = False, plot_soma = False, 
                    soma_size = 120, soma_node = 0, invert_y = False, skeleton_colors = None,
                    pull_compartment_colors = False, 
                    color = 'darkslategray',
                    skel_color_map = {3: "firebrick", 4: "salmon", 2: "steelblue", 1: "olive"},
                    x_min_max = None, y_min_max = None, capstyle = 'round', joinstyle = 'round'):
    """plots a meshparty skeleton obj. 

    Args:
        ax (matplotlib.axes._subplots.AxesSubplot): axis on which to plot skeleton
        sk (meshparty.skeleton.Skeleton): skeleton to be plotted 
        title (str, optional): plot title. Defaults to ''.
        plot_radius (bool, optional): whether or not to plot the radius of each node.
            skeleton must have radius information under sk.vertex_properties['radius'] 
            Defaults to False.
        invert_y (bool, optional): flips the y axis. Defaults to False.
        skel_color_map (dict, optional): Color for each compartment. 
            Defaults to {3: "firebrick", 4: "salmon", 2: "steelblue", 1: "olive"}.
            1 is soma, 2 is axon, 3 is dendrite (basal), 4 is apical dendrite. 
        x_min_max (_type_, optional): _description_. Defaults to None.
        y_min_max (_type_, optional): _description_. Defaults to None.
    """    

    if skeleton_colors is None:
        if pull_compartment_colors:
            skeleton_colors = sk.vertex_properties['compartment']

    if plot_radius:
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





