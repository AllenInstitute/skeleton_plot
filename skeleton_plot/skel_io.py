import pandas as pd
from meshparty import skeleton, meshwork
import seaborn as sns
from cloudfiles import CloudFiles
import os
import io
from . import utils

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
    cloudpath: directory location of layer file. in cloudpath format as seen in https://github.com/seung-lab/cloud-files
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