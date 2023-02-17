import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from meshparty import skeleton
import seaborn as sns
from cloudfiles import CloudFiles
import os
#import nglui 
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
    return cf.get_json(filename)


def apply_casts(df, casts):

    for key, typ in casts.items():
        df[key] = df[key].astype(typ)

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
                                            'compartment':df['type']}, root=0)
    return sk


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
    apply_casts(df, casts)
    return df

def path_to_skel(path):
    df = read_swc(path)
    verts = df[['x','y','z']].values
    verts = verts-1
    edges = df[['id','parent']].iloc[1:].values
    print(len(verts),len(edges))
    sk=skeleton.Skeleton(verts, edges, vertex_properties={'radius':df['radius'], 
                                    'compartment':df['type']}, root=0)
    return sk

# plan to remove compartment colors 
def plot_cell(ax, sk, title='', plot_radius = False, invert_y = False,  
                    compartment_colors = {3: "firebrick", 4: "salmon", 2: "steelblue"},
                    x_min_max = None, y_min_max = None):
    """plots a meshparty skeleton obj. 

    Args:
        ax (matplotlib.axes._subplots.AxesSubplot): axis on which to plot skeleton
        sk (meshparty.skeleton.Skeleton): skeleton to be plotted 
        title (str, optional): plot title. Defaults to ''.
        plot_radius (bool, optional): whether or not to plot the radius of each node.
            skeleton must have radius information under sk.vertex_properties['radius'] 
            Defaults to False.
        invert_y (bool, optional): flips the y axis. Defaults to False.
        compartment_colors (dict, optional): _description_. Defaults to {3: "firebrick", 4: "salmon", 2: "steelblue"}.
        x_min_max (_type_, optional): _description_. Defaults to None.
        y_min_max (_type_, optional): _description_. Defaults to None.
    """    
    if invert_y:    
        ax.invert_yaxis()

    for compartment, color in compartment_colors.items():
        lines_x = []
        lines_y = []
        guess = None

        skn=sk.apply_mask(sk.vertex_properties['compartment']==compartment)

        for cover_path in skn.cover_paths:
            if plot_radius:
                cover_paths_radius = skn.vertex_properties['radius'].values[cover_path[1:]]*5
            else:
                cover_paths_radius = [5]*len(cover_path)
            path_verts = skn.vertices[cover_path,:]
            segments = np.concatenate([path_verts[:-1, 0:2], path_verts[1:, 0:2]], axis=1).reshape(len(path_verts)-1,2,2)
            lc = LineCollection(segments, linewidths=cover_paths_radius, color=color)
            ax.add_collection(lc)
            
        ax.set_aspect("equal")

    if x_min_max:
        ax.set_xlim(x_min_max[0], x_min_max[1])
    if x_min_max and invert_y:
        ax.set_ylim(y_min_max[1], y_min_max[0])
    elif x_min_max:
        ax.set_ylim(y_min_max[0], y_min_max[1])
    
    sns.despine(left=True, bottom=True)
    ax.set_title(title)