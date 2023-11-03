"""
The permute module.

This module implements permutation of blocks, trials and conditions.

"""

__author__ = 'Florian Krause <florian@expyriment.org>, \
Oliver Lindemann <oliver@expyriment.org>'
__version__ = '0.10.0'
__revision__ = 'bac5b00'
__date__ = 'Wed Oct 30 23:26:23 2019 +0100'


from ._permute import is_permutation_type
from ._permute import balanced_latin_square, cycled_latin_square
