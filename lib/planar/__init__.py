__all__ = ('set_epsilon', 'Vec2')

__versioninfo__ = (0, 1, 0)
__version__ = '.'.join(str(n) for n in __versioninfo__)

try: # pragma: no cover
    # Default to C implementation
    from planar.cvector import Vec2
    __implementation__ = 'C'
except ImportError: # pragma: no cover
    # Fall-back to Python implementation
    from planar.vector import Vec2
    __implementation__ = 'Python'

Point = Vec2
"""``Point`` is an alias for ``Vec2``. 
Use ``Point`` where desired for clarity in your code.
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
