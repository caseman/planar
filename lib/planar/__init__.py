__all__ = ('set_epsilon', 'Vec2')
__version__ = (0, 1, 0)

from planar.vector import Vec2

Point = Vec2
"""``Point`` is an alias for ``Vec2``, since points are mathematically
equivilent to vectors. Use ``Point`` where desired for clarity in
your code.
"""

def set_epsilon(epsilon):
    """Set the global limit value for floating point comparisons. 

    The default value of ``0.00001`` is suitable for values
    that are in the "counting range". You may need a larger
    epsilon when using large absolute values, and a smaller value
    for very small values close to zero. Otherwise approximate
    comparison operations will not work as expected.
    """
    global EPSILON, EPSILON2
    EPSILON = float(epsilon)
    EPSILON2 = EPSILON**2

set_epsilon(1e-5)
