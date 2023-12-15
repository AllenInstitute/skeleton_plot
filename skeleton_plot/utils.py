import numpy as np

axis_dict = {'x': 0, 'y': 1, 'z': 2}

def apply_casts(df, casts):

    for key, typ in casts.items():
        df[key] = df[key].astype(typ)


def pull_mw_rad(mw, radius_anno_table):
    ''' pulls the segment properties from meshwork anno and translates into skel index'''
    r_df = mw.anno[radius_anno_table].df[['r_eff', 'mesh_ind_filt']].set_index('mesh_ind_filt')
    rad = r_df.loc[mw.skeleton_indices.to_mesh_region_point].r_eff.values/1000
    return rad


def pull_mw_skel_colors(mw, basal_table, axon_table, apical_table):
    ''' pulls the segment properties from meshwork anno and translates into skel index
    basal node table used for general dendrite labels if no apical/basal differentiation
    apical_table is optional 
    '''
    node_labels = np.full(len(mw.skeleton.vertices), 0)
    soma_node = mw.skeleton.root
    
    basal_nodes = mw.anno[basal_table].skel_index
    node_labels[basal_nodes] = 3

    node_labels[soma_node] = 1

    axon_nodes = mw.anno[axon_table].skel_index

    if apical_table is not None:
        apical_nodes = mw.anno[apical_table].skel_index
        node_labels[apical_nodes] = 4            
    
    node_labels[axon_nodes] = 2

    if 0 in node_labels:
        print("Warning: label annotations passed give labels that are shorter than total length of skeleton nodes to label. Unassigned nodes have been labeled 0. if using pull_compartment_colors, add an option for 0 in inskel_color_map such as skel_color_map={3: 'firebrick', 4: 'salmon', 2: 'steelblue', 1: 'olive', 0:'gray'}.")

    return node_labels

def set_xy_lims(ax, verts = None, invert_y = False, x_min_max = None, 
                y_min_max = None, x = 'x', y = 'y'):
    '''
    helps set x and y lims on the given ax
    '''
    #x, y = axis_dict[x], axis_dict[y]
    if x_min_max is not None:
        ax.set_xlim(x_min_max[0], x_min_max[1])
    if y_min_max is not None and invert_y:
        ax.set_ylim(y_min_max[1], y_min_max[0])
    elif y_min_max is not None:
        ax.set_ylim(y_min_max[0], y_min_max[1])

    
    elif x_min_max is None and y_min_max is None:
        if type(x) == str or type(y) == str:
            x, y = axis_dict[x], axis_dict[y]
        if invert_y:
            ax.set_ylim(max(verts[:,y]), min(verts[:,y]))
        else:

            ax.set_ylim(min(verts[:,y]), max(verts[:,y]))
        ax.set_xlim(min(verts[:,x]), max(verts[:,x]))

def cloud_path_join(*args, use_file_scheme = False):
    """
    Joins given arguments into a cloud path format with only forward slashes.
    """
    
    stripped_parts = [part.strip('/') for part in args]
    joined_path = '/'.join(stripped_parts)
    
    if use_file_scheme:
        return f'file://{joined_path}'
    
    return joined_path

def validate_color(color, num_elements):
    '''
    Validates if the color input is a single value or a list/array
    if array, checks that the length matches num_elements

    Args:
        color (str, list, array): color or array of colors
        num_elements (int): number of elements to validate against if color is array
    Returns:
        color (array): color or color array 
    Raises:
        ValueError: if color is array and length does not match num_elements
    
    '''
        
    if isinstance(color, (list, np.ndarray)):
        if len(color) != num_elements:
            raise ValueError(f'Length of color array ({len(color)}) does not match number of elements ({num_elements})')
        return color
    
    else:
        return np.array([color] * num_elements)