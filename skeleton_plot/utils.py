import numpy as np

def apply_casts(df, casts):

    for key, typ in casts.items():
        df[key] = df[key].astype(typ)


def pull_mw_rad(mw, radius_anno_table):
    ''' pulls the segment properties from meshwork anno and translates into skel index'''
    r_df = mw.anno[radius_anno_table].df[['r_eff', 'mesh_ind_filt']].set_index('mesh_ind_filt')
    rad = r_df.loc[mw.skeleton_indices.to_mesh_region_point].r_eff.values/1000
    return rad


def pull_mw_skel_colors(mw, basal_table, apical_table, axon_table):
    ''' pulls the segment properties from meshwork anno and translates into skel index'''
    node_labels = np.full(len(mw.skeleton.vertices), 0)
    soma_node = mw.skeleton.root
    
    basal_nodes = mw.anno[basal_table].skel_index
    node_labels[basal_nodes] = 3

    apical_nodes = mw.anno[apical_table].skel_index
    node_labels[apical_nodes] = 4

    axon_nodes = mw.anno[axon_table].skel_index
    node_labels[axon_nodes] = 2

    node_labels[soma_node] = 1
    
    return node_labels

def set_xy_lims(ax, verts = None, invert_y = False, x_min_max = None, 
                y_min_max = None, x = 'x', y = 'y'
                ):
    '''
    helps set x and y lims on the given ax
    '''
    
    if x_min_max is not None:
        ax.set_xlim(x_min_max[0], x_min_max[1])
    if y_min_max is not None and invert_y:
        ax.set_ylim(y_min_max[1], y_min_max[0])
    elif y_min_max is not None:
        ax.set_ylim(y_min_max[0], y_min_max[1])

    
    elif x_min_max is None and y_min_max is None:
        if invert_y:
            ax.set_ylim(max(verts[:,y]), min(verts[:,y]))
        else:
            ax.set_ylim(min(verts[:,y]), max(verts[:,y]))
        ax.set_xlim(min(verts[:,x]), max(verts[:,x]))