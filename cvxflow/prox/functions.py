
from tensorflow.python.framework import dtypes
from tensorflow.python.framework import ops
from tensorflow.python.ops import array_ops
from tensorflow.python.ops import linalg_ops
from tensorflow.python.ops import math_ops

class ProxFunction(object):
    def __repr__(self):
        return self.__class__.__name__


class AbsoluteValue(ProxFunction):
    """Absolute value.

    If lam is a scalar, lam*|x|
    If lam is a tuple, -lam[0]*neg(x) + lam[1]*pos(x)."""
    def __init__(self, scale=1):
        self.scale = scale
        if not isinstance(self.scale, tuple):
            self.scale = (scale, scale)

    def __call__(self, v):
        return (math_ops.maximum(v - self.scale[1], 0) +
                math_ops.minimum(v + self.scale[0], 0))

class LeastSquares(ProxFunction):
    """Least squares.

    0.5*sum_squares(A*x - b) + 0.5*mu*sum_squares(x)."""
    def __init__(self, A=None, b=None, mu=None, W=None, n=None, shape=None):
        n = None
        if A is not None:
            n = int(A.shape[1])
            dtype = A.dtype
            A = A.to_dense()
        elif W is not None:
            n = int(W.shape[1])
            dtype = W.dtype
            W = W.to_dense()
        else:
            raise ValueError("Must specify either A or W")

        M = 0
        if A is not None:
            M += math_ops.matmul(A, A, transpose_a=True)

        if A is not None and b is not None:
            if len(b.get_shape()) == 1:
                b = array_ops.expand_dims(b, -1)
            self.ATb = math_ops.matmul(A, b, transpose_a=True)
        else:
            self.ATb = 0

        if W is not None:
            M += math_ops.matmul(W, W, transpose_a=True)
        else:
            M += linalg_ops.eye(n, dtype=dtype)

        if mu is not None:
            M += mu*linalg_ops.eye(n, dtype=dtype)


        self.L = linalg_ops.cholesky(M)

    def __call__(self, v):
        return linalg_ops.cholesky_solve(self.L, self.ATb + v)