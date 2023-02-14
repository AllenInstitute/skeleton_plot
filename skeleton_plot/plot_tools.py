import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from meshparty import skeleton, skeleton_io
import seaborn as sns
from cloudfiles import CloudFiles
import io
from meshparty import meshwork
import nglui 
from caveclient import CAVEclient


SWC_COLUMNS = ('id', 'type', 'x', 'y', 'z', 'radius', 'parent',)
COLUMN_CASTS = {
    'id': int,
    'parent': int,
    'type': int
}

def read_layer_depths(cloudpath, soma_id = None, filename = 'mouse_me_and_met_avg_layer_depths.json'):
    '''
    if you do not pass a soma id, it will load the average layer bounds file 
    '''
    if not soma_id is None:
        filename = f'{soma_id}_poly.json'

    cf = CloudFiles(cloudpath)
    return cf.get_json(filename)


def plot_layers(ax, cloudpath, soma_id = None):
    '''
    
    If you do not pass a soma id, it will plot the average layer bounds file. otherwise pass 
    soma id to plot the neuron and the custom layer bounds for that neuron
    '''
    
    layer_file = read_layer_depths(cloudpath, soma_id)
    
    # calculate x min and max on ax 
    xmin, xmax = ax.get_xlim()
    
    if soma_id == None:
        layer_file = np.array(list(layer_file.values()))*-1
        
        [ax.hlines(y_val, xmin = xmin, xmax = xmax) for y_val in layer_file]

    else:
        for key in layer_file.keys():
            if key == 'layer_polygons':

                for layer in layer_file[key]:
                    bound = np.array(layer['path'])
                    ax.scatter(bound[:,0]*0.3603, bound[:,1]*0.3603, s = 1)

            else:
                bound = np.array(layer_file[key]['path'])
            ax.scatter(bound[:,0]*0.3603, bound[:,1]*0.3603, s = 1)
    


def apply_casts(df, casts):

    for key, typ in casts.items():
        df[key] = df[key].astype(typ)

    

def read_skeleton(root_id, nuc_id, cloud_path = skel_path, 
                 df = None):
    if cloud_path == skel_path:
        file_path = cloud_path + f"{root_id}_{nuc_id}/{root_id}_{nuc_id}.swc"
    elif cloud_path == upright_path or cloud_path == layer_aligned_path:
        file_path = cloud_path + f"{nuc_id}.swc"
    #print(file_path)
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

    """ Read an swc file into a pandas dataframe
    """
    if "://" not in path:
        path = "file://" + path

    #cloudpath, file = os.path.split(path)
    #cf = CloudFiles(cloudpath)
    #path = io.BytesIO(cf.get(file))
    
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

def plot_cell(ax, sk, title='', invert_ax = True):

    
    #ax.set_ylim(1100, 300)
    
    MORPH_COLORS = {3: "firebrick", 4: "salmon", 2: "steelblue"}
    if min(sk.vertices[:,1]) < 0:    
        ax.invert_yaxis()
    for compartment, color in MORPH_COLORS.items():
        lines_x = []
        lines_y = []
        guess = None

        skn=sk.apply_mask(sk.vertex_properties['compartment']==compartment)

        for cover_path in skn.cover_paths:
            path_verts = skn.vertices[cover_path,:]
            ax.plot(path_verts[:,0], path_verts[:,1], c=color, linewidth=1)
            
        ax.set_aspect("equal")
        
    if invert_ax:
        ax.invert_yaxis()

    
    #ax.set_ylim(1100, 300)
    sns.despine(left=True, bottom=True)
    #ax.set_xticks([])
    #ax.set_yticks([])
    ax.set_title(title)


    
    
def load_mws_from_folder(root_id, nuc_id, folder_path = mw_path):
    
    filename = f"{root_id}_{nuc_id}/{root_id}_{nuc_id}.h5"
    
    cf = CloudFiles(folder_path)
    binary = cf.get([filename])


    with io.BytesIO(cf.get(binary[0]['path'])) as f:
        f.seek(0)
        mw = meshwork.load_meshwork(f)

    return mw

def plot_mw_skel(ax, mw, title = '', view_synapses = 'none', pre_color = 'yellowgreen', post_color = 'plum',
                view_layers = False):
    '''
    view synapses can be 'none', 'all', 'pre', 'post'
    
    '''
    
    
    MORPH_COLORS = {3: "firebrick", 4: "salmon", 2: "steelblue"}
    colors = np.ones(len(mw.skeleton.vertices))
    colors[mw.anno.basal_mesh_labels.skel_mask] = 3
    colors[mw.anno.apical_mesh_labels.skel_mask] = 4
    colors[mw.anno.is_axon.skel_mask] = 2
    
    ax.invert_yaxis()
    for compartment, color in MORPH_COLORS.items():
        lines_x = []
        lines_y = []
        guess = None

        skn=mw.skeleton.apply_mask(colors==compartment)

        for cover_path in skn.cover_paths:
            path_verts = skn.vertices[cover_path,:]
            ax.plot(path_verts[:,0], path_verts[:,1], c=color, linewidth=1)
            
        ax.set_aspect("equal")
        
    if view_synapses != 'none':
        
        if view_synapses == 'all' or view_synapses == 'pre':
            presyns = np.array([np.array(x) for x in (mw.anno.pre_syn['pre_pt_position']).values])
            ax.scatter(presyns[:,0]*4, presyns[:,1]*4, s = 2, c = pre_color)
            
        if view_synapses == 'all' or view_synapses == 'post':
            postsyns = np.array([np.array(x) for x in (mw.anno.post_syn['post_pt_position']).values])
            ax.scatter(postsyns[:,0]*4, postsyns[:,1]*4, s = 2, c = post_color)


        
    
    
    #ax.set_ylim(1100, 300)
    sns.despine(left=True, bottom=True)
    #ax.set_xticks([])
    #ax.set_yticks([])
    ax.set_title(title)
    
    
 
