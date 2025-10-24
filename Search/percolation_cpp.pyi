'''Type stubs for peroclation_cpp C++ module.'''

import numpy as np 
from numpy.typing import NDArray

def find_clusters(grid: NDArray[np.bool_]) -> NDArray[np.int32]:
    '''
    Find clusters using C++ Union-Find algo.

    Args: 
        grid: NxN bool array where True = occupied site

        Returns:
                NxN int32 array with cluster labels (0 = empty)
    '''