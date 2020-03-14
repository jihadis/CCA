class Bmatrix:
    #增广矩阵,根据线代，求增广矩阵的值。
    zeros=lambda i:len(i)==i.count(0)
    def augmented_Matrix(self,funciton):
        pass
    # 简化阶梯型矩阵
    def simplify_Echelon_Matrix(self,matrix):
        matrix=self.echelon_Matrix(matrix)
        def loop(matrix,row=len(matrix)-1):
            master = [i for i in range(len(matrix[row])) if matrix[row][i] != 0][0]  # 取主元列。
            diff = matrix[row][master]
            for j in range(len(matrix[row])):#除以该主元
                if j != master:
                    matrix[row][j] /= diff
                else:
                    matrix[row][master] = 1
            for i in range(row):#其他行每个元素减去主元上方的值乘以该行的值。
                diff=-matrix[i][master]
                for j in range(len(matrix[i])):
                    if j !=master:
                        matrix[i][j]+=diff*matrix[row][j]
                    elif j!=i:matrix[i][master] = 0
            if row!=0:return loop(matrix,row-1)
            return matrix

        return loop(matrix)

    #梯形矩阵
    def echelon_Matrix(self,matrix):
        def loop(matrix,row=0):
            if not Bmatrix.zeros(matrix[row]):
                master=[i for i in range(len(matrix[row])) if matrix[row][i]!=0][0] #取主元列。
                for i in range(row+1, len(matrix)):
                    diff =-matrix[i][master]/matrix[row][master] #算出方差
                    matrix[i][master]=0 #将主元列归0化
                    for j in range(master+1,len(matrix[i])):
                        matrix[i][j]+=matrix[row][j]*diff#将该行所有元素加上主元数所在行所有元素乘以方差
                for i in range(len(matrix)): #将所有为0的行抛在后方
                    if Bmatrix.zeros(matrix[i]):
                        matrix.append(matrix.pop(i))
                if row==len(matrix)-1:return matrix
                return loop(matrix,row+1)
            return matrix
        head=matrix[0]
        if head[0]==0:
            for i in range(len(matrix)-1,0,-1):
                if matrix[i][0]!=0:
                    matrix[0]=matrix[i]
                    matrix[i]=head
                    break

        return loop(matrix)

    #矩阵的秩
    def rank(self,matrix):
        return len([i for i in self.echelon_Matrix(matrix) if not Bmatrix.zeros(i)])
import numpy as np
#[0,-3,-6,4,9],[-1,-2,-1,3,1],[-2,-3,0,3,-1],[1,4,5,-9,-7]
from numpy import mat
m=[[1,4,5,-9,-7],

   [-1,-2,-1,3,1],
   [-2,-3,0,3,-1],
   [0, -3, -6, 4, 9] ]

res=Bmatrix().echelon_Matrix(m.copy())


#print("\n".join([str(i)for i in m]))


#[[3.8,-1.2],[-1.2,3.8]]

x=[[2,3],[3,2]]

weight=[[1.2,0.1],[3.2,0.7]]# unknow

r=np.dot(x,weight)
print(np.dot(x,r/x),r )

