import pandas as pd
from meshparty import skeleton, meshwork
try:
    from cloudfiles import CloudFiles
    cf_imported = True
except:
    cf_imported = False
import os
import io
from . import utils

SWC_COLUMNS = ('id', 'type', 'x', 'y', 'z', 'radius', 'parent',)
COLUMN_CASTS = {
    'id': int,
    'parent': int,
    'type': int
}

def read_json(directory, filename):
    '''
    enter cloudpath location of json file(i.e. layer depths .json file), returns dict
    of that layer containing vertices
    
    Parameters
    ----------
    directory (str): directory location of json file. in cloudpath format as seen in https://github.com/seung-lab/cloud-files
    filename (str): full json filename 

    Returns:
    layer_bounds (list(dict)): list of dicts with values being the layer name, values containing the (x,y) vertices of the layer (among other things)
    ''' 
    if cf_imported == False:
        raise ImportError('cannot use read_depths without cloudfiles.Install https://github.com/seung-lab/cloud-files to continue')

    cf = CloudFiles(directory)
    js = cf.get_json(filename)

    if js is None:
        if filename not in list(cf):
            raise FileNotFoundError(f"filename '{filename}' not found in '{directory}'")
        else:
            raise ValueError('unable to retrieve file')

    return js

# will be moved to meshparty?
def read_skeleton(directory, filename):
    """reads skeleton file from cloudfiles style path

    Args:
    directory (str): directory location of swc skeleton file. in cloudpath format as seen in https://github.com/seung-lab/cloud-files
    filename (str): full .swc filename 
    df (pd.DataFrame, optional): _description_. Defaults to None.

    Returns:
        skeleton: (meshparty.meshwork.skeleton) skeleton object containing .swc data
    """
    if '://' not in directory:
        directory = 'file://' + directory
    file_path = os.path.join(directory, filename)
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



def load_mw(directory, filename):
    
    # filename = f"{root_id}_{nuc_id}/{root_id}_{nuc_id}.h5"
    '''
    """loads a meshwork file from .h5 into meshparty.meshwork object

    Args:
        directory (str): directory location of meshwork .h5 file. in cloudpath format as seen in https://github.com/seung-lab/cloud-files
        filename (str): full .h5 filename 

    Returns:
        meshwork (meshparty.meshwork): meshwork object containing .h5 data 
    """    '''
    if cf_imported == False:
        raise ImportError('cannot use load_mw without cloudfiles.Install https://github.com/seung-lab/cloud-files to continue')
    
    if "://" not in directory:
        directory = "file://" + directory
    
    cf = CloudFiles(directory)
    binary = cf.get([filename])

    with io.BytesIO(cf.get(binary[0]['path'])) as f:
        f.seek(0)
        mw = meshwork.load_meshwork(f)

    return mw