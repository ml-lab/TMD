'''
tmd Tree's methods
'''
import numpy as _np


def _rd(point1, point2):
    '''Returns euclidean distance between point1 and point2
    '''
    return _np.linalg.norm(_np.subtract(point1, point2), 2)


def _rd_w(p1, p2, w=(1., 1., 1.), normed=True):
    '''Returns weighted euclidean distance between p1 and p2
    '''
    if normed:
        w = (_np.array(w) / _np.linalg.norm(w))
    return _np.dot(w, (_np.subtract(p1, p2)))


def size(tree):
    '''
    Tree method to get the size of the tree lists.

    Note: All the lists of the Tree should be
    of the same size, but this should be
    checked in the initialization of the Tree!
    '''
    return int(len(tree.x))


def get_type(self):
    '''Returns type of tree
    '''
    return int(_np.median(self.t))


def get_bounding_box(self):
    """
    Input
    ------
    tree: tmd tree

    Returns
    ---------
    bounding_box: np.array
        ([xmin,ymin,zmin], [xmax,ymax,zmax])
    """
    xmin = _np.min(self.x)
    xmax = _np.max(self.x)
    ymin = _np.min(self.y)
    ymax = _np.max(self.y)
    zmin = _np.min(self.z)
    zmax = _np.max(self.z)

    return _np.array([[xmin, ymin, zmin], [xmax, ymax, zmax]])


# Segment features
def get_segments(self):
    """
    Input
    ------
    tree: tmd tree

    Returns
    ---------
    seg_list: np.array
        (child[x,y,z], parent[x,y,z])
    """
    seg_list = []

    for seg_id in range(1, size(self)):
        par_id = self.p[seg_id]
        child_coords = _np.array([self.x[seg_id],
                                  self.y[seg_id],
                                  self.z[seg_id]])
        parent_coords = _np.array([self.x[par_id],
                                   self.y[par_id],
                                   self.z[par_id]])
        seg_list.append(_np.array([parent_coords, child_coords]))

    return seg_list


def get_segment_lengths(tree):
    '''Returns segment lengths
    '''
    seg_len = _np.zeros(size(tree) - 1)
    segs = tree.get_segments()

    for iseg, seg in enumerate(segs):
        seg_len[iseg] = _rd(seg[0], seg[1])

    return seg_len


# Points features to be used for topological extraction
def get_point_radial_distances(self, point=None, dim='xyz'):
    '''Tree method to get radial distances from a point.
    If point is None, the soma surface -defined by
    the initial point of the tree- will be used
    as a reference point.
    '''
    if point is None:
        point = []
        for d in dim:
            point.append(getattr(self, d)[0])

    radial_distances = _np.zeros(size(self), dtype=float)

    for i in range(size(self)):
        point_dest = []
        for d in dim:
            point_dest.append(getattr(self, d)[i])

        radial_distances[i] = _rd(point, point_dest)

    return radial_distances


def get_point_radial_distances_time(self, point=None, dim='xyz', zero_time=0, time=1):
    '''Tree method to get radial distances from a point.
    If point is None, the soma surface -defined by
    the initial point of the tree- will be used
    as a reference point.
    '''
    if point is None:
        point = []
        for d in dim:
            point.append(getattr(self, d)[0])
    point.append(zero_time)

    radial_distances = _np.zeros(size(self), dtype=float)

    for i in range(size(self)):
        point_dest = []
        for d in dim:
            point_dest.append(getattr(self, d)[i])
        point_dest.append(time)

        radial_distances[i] = _rd(point, point_dest)

    return radial_distances


def get_point_weighted_radial_distances(self, point=None, dim='xyz', w=(1, 1, 1), normed=False):
    '''Tree method to get radial distances from a point.
    If point is None, the soma surface -defined by
    the initial point of the tree- will be used
    as a reference point.
    '''
    if point is None:
        point = []
        for d in dim:
            point.append(getattr(self, d)[0])

    radial_distances = _np.zeros(size(self), dtype=float)

    for i in range(size(self)):
        point_dest = []
        for d in dim:
            point_dest.append(getattr(self, d)[i])

        radial_distances[i] = _rd_w(point, point_dest, w, normed)

    return radial_distances


def get_point_path_distances(self):
    '''Tree method to get path distances from the root.
    '''
    seg_len = get_segment_lengths(self)

    def path_length(seg_id):
        '''Returns path length of segment'''
        return sum([seg_len[i] for i in get_way_to_root(self, seg_id)[1:]])

    return _np.array([path_length(i) for i in range(size(self))])


def get_point_path_distances_2(self):
    '''Tree method to get path distances from the root.
    '''
    import copy

    seg_len = get_segment_lengths(self)
    path_lengths = _np.append(0, copy.deepcopy(seg_len))
    children = get_children(self)

    for i in children.keys():     
        path_lengths[children[i]] = path_lengths[children[i]] + path_lengths[i]

    return path_lengths


def get_point_section_lengths(self):
    '''Tree method to get section lengths.
    '''
    lengths = _np.zeros(size(self), dtype=float)
    ways, end = self.get_sections_only_points()
    seg_len = get_segment_lengths(self)

    for i, item in enumerate(end):
        lengths[item] = _np.sum(seg_len[ways[i]:item])

    return lengths


def get_branch_order(tree, seg_id):
    '''Returns branch order of segment'''
    B = tree.get_multifurcations()
    return sum([1 if i in B else 0 for i in get_way_to_root(tree, seg_id)])


def get_point_section_branch_orders(self):
    '''Tree method to get section lengths.
    '''
    return _np.array([get_branch_order(self, i) for i in range(size(self))])


def get_point_projection(self, vect=(0, 1, 0), point=None):
    """Projects each point in the tree (x,y,z) - input_point
       to a selected vector. This gives the orientation of
       each section according to a vector in space, if normalized,
       otherwise it returns the relative length of the section.
    """
    if point is None:
        point = [self.x[0], self.y[0], self.z[0]]

    xyz = _np.transpose([self.x, self.y, self.z]) - point

    return _np.dot(xyz, vect)


# Section features
def get_sections_2(self):
    '''Tree method to get the sections'
    begining and ending indices.
    '''
    import scipy.sparse as sp
    end = _np.array(sp.csr_matrix.sum(self.dA, 0) != 1)[0].nonzero()[0]

    if 0 in end:  # If first segment is a bifurcation
        end = end[1:]

    beg = _np.append([0], self.p[_np.delete(_np.hstack([0, 1 + end]), len(end))][1:])

    return beg, end


def get_sections_only_points(self):
    '''Tree method to get the sections'
    begining and ending indices.
    '''
    import scipy.sparse as sp
    end = _np.array(sp.csr_matrix.sum(self.dA, 0) != 1)[0].nonzero()[0]

    if 0 in end:  # If first segment is a bifurcation
        end = end[1:]

    beg = _np.delete(_np.hstack([0, 1 + end]), len(end))

    return beg, end


def extract_simplified(self):
    """Returns a simplified tree that corresponds
       to the start - end of the sections points
    """
    from tmd import Tree
    beg0, end0 = self.get_sections_2()
    sections = _np.transpose([beg0, end0])

    x = _np.zeros([len(sections)+1])
    y = _np.zeros([len(sections)+1])
    z = _np.zeros([len(sections)+1])
    d = _np.zeros([len(sections)+1])
    t = _np.zeros([len(sections)+1])
    p = _np.zeros([len(sections)+1])

    x[0] = self.x[sections[0][0]]
    y[0] = self.y[sections[0][0]]
    z[0] = self.z[sections[0][0]]
    d[0] = self.d[sections[0][0]]
    t[0] = self.t[sections[0][0]]
    p[0] = -1

    for i,s in enumerate(sections):
        x[i+1] = self.x[s[1]]
        y[i+1] = self.y[s[1]]
        z[i+1] = self.z[s[1]]
        d[i+1] = self.d[s[1]]
        t[i+1] = self.t[s[1]]
        p[i+1] = _np.where(beg0 ==s[0])[0][0]

    return Tree.Tree(x,y,z,d,t,p)


def get_bif_term(self):
    '''Returns number of children per point
    '''
    import scipy.sparse as sp
    return _np.array(sp.csr_matrix.sum(self.dA, axis=0))[0]


def get_bifurcations(self):
    '''Returns bifurcations
    '''
    bif_term = get_bif_term(self)
    bif = _np.where(bif_term == 2.)[0]
    return bif


def get_multifurcations(self):
    '''Returns bifurcations
    '''
    bif_term = get_bif_term(self)
    bif = _np.where(bif_term >= 2.)[0]
    return bif


def get_terminations(self):
    '''Returns terminations
    '''
    bif_term = get_bif_term(self)
    term = _np.where(bif_term == 0.)[0]
    return term


def get_direction_between(self, start_id=0, end_id=1):
    '''Returns direction of a branch
    defined as end point - start point
    normalized as a unit vector.
    '''
    vect = _np.subtract([self.x[end_id], self.y[end_id], self.z[end_id]],
                        [self.x[start_id], self.y[start_id], self.z[start_id]])

    if _np.linalg.norm(vect) != 0.0:
        return vect / _np.linalg.norm(vect)
    return vect


def _vec_angle(u, v):
    '''Returns the angle between v and u in 3D.
    '''
    c = _np.dot(u, v) / _np.linalg.norm(u) / _np.linalg.norm(v)
    return _np.arccos(c)


def get_angle_between(tree, sec_id1, sec_id2):
    '''Returns local bifurcations angle
    between two sections, defined by their ids.
    sec_id1: the start point of the section #1
    sec_id2: the start point of the section #2
    '''
    beg, end = tree.get_sections_only_points()
    b1 = _np.where(beg == sec_id1)[0][0]
    b2 = _np.where(beg == sec_id2)[0][0]

    u = tree.get_direction_between(beg[b1],
                                   end[b1])
    v = tree.get_direction_between(beg[b2],
                                   end[b2])

    return _vec_angle(u, v)


def get_way_to_root(tree, sec_id=0):
    '''Returns way to root
    '''
    way = []
    tmp_id = sec_id

    while tmp_id != -1:
        way.append(tree.p[tmp_id])
        tmp_id = tree.p[tmp_id]

    return way


def get_children(tree):
    '''Returns a dictionary of children
       for each node of the tree
    '''
    from collections import OrderedDict
    return OrderedDict({i: _np.where(tree.p == i)[0] for i in xrange(len(tree.p))})


# PCA
def get_pca(self, plane='xy', component=0):
    '''Returns the i-th principal
    component of PCA on the points
    of the tree in the selected plane
    '''
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2)
    pca.fit(_np.transpose([getattr(self, plane[0]), getattr(self, plane[1])]))

    return pca.components_[component]
