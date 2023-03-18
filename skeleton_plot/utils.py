import numpy as np

def apply_casts(df, casts):

    for key, typ in casts.items():
        df[key] = df[key].astype(typ)


def pull_mw_rad(mw, radius_anno_table):
    ''' pulls the segment properties from meshwork anno and translates into skel index'''
    r_df = mw.anno[radius_anno_table].df[['r_eff', 'mesh_ind']].set_index('mesh_ind')
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