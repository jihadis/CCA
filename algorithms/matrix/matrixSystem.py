import numpy as np
import numpy.matlib
from functools import reduce
from algorithms.tools.Toolkit import *
class MatrixSystem(object):

    @staticmethod
    def getDiagonal( matrix, shape):

        # 如果结果是标量对向量/矩阵求导不会生成雅克比/黑塞矩阵，则不需要化简，导数直接为向量形式
        if len(np.shape(list(matrix))) <= len(shape): return matrix

        def diagonalElem(elem, index, variable):
            variable["count"] += 1
            return elem[variable["count"]]

        return forEveryWithIndex(
            list(np.array(matrix).reshape
                 (list(shape) + [reduce(lambda x, y: x* y, shape)])),
            diagonalElem, len(shape), variables=dict({"count": -1}))

    @staticmethod
    def getRandn(size,sigma,mean):
        return sigma * np.matlib.randn(size) + mean