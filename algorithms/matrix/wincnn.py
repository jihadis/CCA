from __future__ import print_function
from sympy import symbols, Matrix, Poly, zeros, eye, Indexed, simplify, IndexedBase, init_printing, pprint
from operator import mul
from functools import reduce

def At(a,m,n):
    return Matrix(m, n, lambda i,j: a[i]**j)


def A(a,m,n):
    return At(a, m-1, n).row_insert(m-1, Matrix(1, n, lambda i,j: 1 if j==n-1 else 0))

def T(a,n):
    return Matrix(Matrix.eye(n).col_insert(n, Matrix(n, 1, lambda i,j: -a[i]**n)))

def Lx(a,n):
    x=symbols('x')
    return Matrix(n, 1, lambda i,j: Poly((reduce(mul, ((x-a[k] if k!=i else 1) for k in range(0,n)), 1)).expand(basic=True), x))

def F(a,n):
    return Matrix(n, 1, lambda i,j: reduce(mul, ((a[i]-a[k] if k!=i else 1) for k in range(0,n)), 1))

def Fdiag(a,n):
    f=F(a,n)
    return Matrix(n, n, lambda i,j: (f[i,0] if i==j else 0))

def FdiagPlus1(a,n):
    f = Fdiag(a,n-1)
    f = f.col_insert(n-1, zeros(n-1,1))
    f = f.row_insert(n-1, Matrix(1,n, lambda i,j: (1 if j==n-1 else 0)))
    return f

def L(a,n):
    lx = Lx(a,n)
    f = F(a, n)
    return Matrix(n, n, lambda i,j: lx[i, 0].nth(j)/f[i]).T

def Bt(a,n):
    return L(a,n)*T(a,n)

def B(a,n):
    return Bt(a,n-1).row_insert(n-1, Matrix(1, n, lambda i,j: 1 if j==n-1 else 0))

FractionsInG=0
FractionsInA=1
FractionsInB=2
FractionsInF=3

def cookToomFilter(a,n,r,fractionsIn=FractionsInG):
    alpha = n+r-1
    f = FdiagPlus1(a,alpha)
    if f[0,0] < 0:
        f[0,:] *= -1
    if fractionsIn == FractionsInG:
        AT = A(a,alpha,n).T
        G = (A(a,alpha,r).T/f).T
        BT = f * B(a,alpha).T
    elif fractionsIn == FractionsInA:
        BT = f * B(a,alpha).T
        G = A(a,alpha,r)
        AT = (A(a,alpha,n)).T/f
    elif fractionsIn == FractionsInB:
        AT = A(a,alpha,n).T
        G = A(a,alpha,r)
        BT = B(a,alpha).T
    else:
        AT = A(a,alpha,n).T
        G = A(a,alpha,r)
        BT = f * B(a,alpha).T
    return (AT,G,BT,f)


def filterVerify(n, r, AT, G, BT):

    alpha = n+r-1

    di = IndexedBase('d')
    gi = IndexedBase('g')
    d = Matrix(alpha, 1, lambda i,j: di[i])
    g = Matrix(r, 1, lambda i,j: gi[i])

    V = BT*d
    U = G*g
    M = U.multiply_elementwise(V)
    Y = simplify(AT*M)

    return Y

def convolutionVerify(n, r, B, G, A):

    di = IndexedBase('d')
    gi = IndexedBase('g')

    d = Matrix(n, 1, lambda i,j: di[i])
    g = Matrix(r, 1, lambda i,j: gi[i])

    V = A*d
    U = G*g
    M = U.multiply_elementwise(V)
    Y = simplify(B*M)

    return Y

def showCookToomFilter(a,n,r,fractionsIn=FractionsInG):

    AT,G,BT,f = cookToomFilter(a,n,r,fractionsIn)

    # print ("AT = ")
    # pprint(AT)
    # print ("")
    #
    # print ("G = ")
    # pprint(G)
    # print ("")
    #
    # print ("BT = ")
    # pprint(BT)
    # print ("")
    #
    # # if fractionsIn != FractionsInF:
    # #     print ("FIR filter: AT*((G*g)(BT*d)) =")
    # #     pprint(filterVerify(n,r,AT,G,BT))
    # #     print ("")
    #
    # if fractionsIn == FractionsInF:
    #     print ("fractions = ")
    #     pprint(f)
    #     print ("")
    return AT, G, BT
def showCookToomConvolution(a,n,r,fractionsIn=FractionsInG):

    AT,G,BT,f = cookToomFilter(a,n,r,fractionsIn)

    B = BT.transpose()
    A = AT.transpose()

    print ("A = ")
    pprint(A)
    print ("")

    print ("G = ")
    pprint(G)
    print ("")

    print ("B = ")
    pprint(B)
    print ("")

    if fractionsIn != FractionsInF:
        print ("Linear Convolution: B*((G*g)(A*d)) =")
        pprint(convolutionVerify(n,r,B,G,A))
        print ("")

    if fractionsIn == FractionsInF:
        print ("fractions = ")
        pprint(f)
        print ("")

# from sympy import Rational
# print(Rational(1,2),-Rational(1,2))
#showCookToomFilter((0,1,-1), 2, 3)

#print(signal.convolve(img,core))

#0 1 -1 2 -2 1/2 -1/2
#[-0.566406058202890, 0.183788074551046, 0.906002138994950, 1.49028559069665] 1-38
#[-0.566406058158464, 0.183788074561107, 0.906002139001060, 1.49028559071415] 1/x
#[-0.566406058202678, 0.183788074552091, 0.906002138999368, 1.49028559071354] 1-38 /2
#[-0.566406058034772, 0.183788076610654, 0.906002152187284, 1.49028568486392] 38-1
# r=[]
# [r.extend([i/s1,-i/s1]) for i in range(int((s1+s-2)/2))]
# print(r)
# Atb,G,Btb=showCookToomFilter(r[1:], (s-s1+1), s1)
# conv=lambda img,core:Atb.dot(numpy.array(G.dot(core))*numpy.array(Btb.dot(img)))
# # print(numpy.array(G.dot(core))*numpy.array(Btb.dot(img)))
# c=conv(img,core)
# print(c)
# import tensorflow as tf
#
# print(tf.nn.conv1d(tf.Variable(img,dtype=tf.float32),tf.Variable(core,dtype=tf.float32),1,"VALID"))
import numpy
import math
s=55
s1=15
print(s,s1)
from controllers.workflow_controller.flowVaribale import FlowVaribale
img=FlowVaribale.getRandomGaussian((s,s),sigma=1e-1).toList()
#img=FlowVaribale.ones((s,s)).forEvery(lambda e,i:math.sin(sum(i)))
core=FlowVaribale.getRandomGaussian((s1,s1),sigma=2).toList()
print(img)
print(core)
import tensorflow as tf
import numpy as np
#40 11.x
#30 8
#20 4
#10 2
#5 1

import math
from sympy import Rational as Rat
lamdafunc=FlowVaribale.Lagrange([Rat(i)for i in [1,4,6,8.4,13.072265625000565,17.03125083278428]],[6,12,24,32,48,64])
# lamdas={
#     64:17.03125083278428,#dx 6.21724893790088e-15
#
#     48:Rat(13.072265625000565) ,#dx  5.605193857299268e-44
#     32:Rat(8.4),
#     24:Rat(6),
#     12:Rat(4),
#     6:1,
#
# }

sess = tf.InteractiveSession()

# --------------- tf.nn.conv1d  -------------------

x = tf.Variable(img, dtype=tf.float64)
x = tf.reshape(x, [1,s,s,1])  #这一步必不可少，否则会报错说维度不一致；
'''
[batch, in_height, in_width, in_channels] = [1,1,4,1]
'''
W_conv1 = tf.Variable(core,dtype=tf.float64)  # 权重值
W_conv1 = tf.reshape(W_conv1, [s1,s1,1,1])  # 这一步同样必不可少
'''
[filter_height, filter_width, in_channels, out_channels]
'''
conv1 = tf.nn.conv2d(x, W_conv1, strides=[1,1,1,1] ,padding='VALID')  # conv1=[batch, round(n_sqs/stride), n_filers],stride是步长。

tf.global_variables_initializer().run()
out = sess.run(conv1)
out=FlowVaribale(np.array(out).tolist()).flat().reshape((s-s1+1,s-s1+1))
from controllers.workflow_controller.flowVaribale import FlowVaribale
#print(out)
#print("error",(FlowVaribale(np.array(out).tolist()).flat()-c).forEvery(lambda e:abs(e)).sum())
stride=1
# pridict [[0.945391435103375, -0.159706994666166], [-0.215179517836077, 0.0537592670834250]]
# real [[0.009263985603628925, -0.027690843375215192], [-0.01804863392058006, 0.01899513164902322]]







from algorithms.tools.Toolkit import *
def get_patchs( map, size):
    def f(elem, index):
        if stride <= 1 or (FlowVaribale(list(index)) % stride).all(lambda x: x == 0):
            return map[size.indexes() + list(index)]
    return forEveryWithIndex(map, f, clear_null=True)


def get_diff(lamda):
    lamda=Rat(lamda)
    r = []
    [r.extend([i / lamda, -i / lamda]) for i in range(int((s1 + s - 2) / 2))]
    # print(r)
    Ata, G, Btb = showCookToomFilter(r[1:], (s - s1 + 1), s1)
    print(Ata, G, Btb)
    print(int(math.sqrt(math.sqrt(s)*s)))
    #int(math.sqrt(math.sqrt(s)*s))
    Ata,G,Btb=[FlowVaribale(i.tolist()).forEvery(lambda e:round(e.evalf(),int(math.sqrt(math.sqrt(s)*s)))) for i in [Ata,G,Btb]]
    print(Ata,G,Btb)
    print(122)
    conv = lambda x, w: FlowVaribale(Ata.dot(numpy.array(G.dot(w)) * numpy.array(Btb.dot(x))))
    # patchs=get_patchs(FlowVaribale(img),FlowVaribale(core).shape())
    # print(numpy.array(G.dot(core[0])))
    c = [sum([conv(img[i + j], core[j]) for j in range(len(core))]) for i in range(len(img) - len(core) + 1)]
    print("pridict", FlowVaribale(c))
    print("real", out)
    err = (FlowVaribale(np.array(out).tolist()) - c).forEvery(lambda e: abs(e)).sum()[0][0]
    print("error", lamda, (err))
    return err
lamda =lamdafunc(s)
print("lambda",lamda )
get_diff(lamda)
#for j in range(11,s):
def pridict():
    dx=Rat(6.21724893790088e-15)
    j=Rat(17.03125083278428)
    #old=get_diff(j);j+=dx
    #3.145672370464453

    result=[]

    #while dx>1e-4:
    #中值点获取，逼近真真实结果
    while True:
        if j!=0:
            dx /= 2
            #print("dx",dx.evalf())
            err_l,err_r = get_diff(j-dx),get_diff(j+dx)
            result+=[[err_l,j-dx,j,dx,len(result)],[err_r,j+dx,j,dx,len(result)+1]]
            most_min = sorted(result,key=lambda e:e[0])[0]
            print("most_min:",most_min)
            if sorted([err_l,err_r])[0]>most_min[0]:
                print("gogogo",most_min)
                j,dx=most_min[1],most_min[3]
                most_min[3] /= 2
                # dx /=2
                # result[most_min[-1]][-2]/=2
            else:
                j +=(dx if err_l > err_r else -dx)
            #j+=((-rf) if err>old else rf)
            print(sorted(result,key=lambda e:e[0])[0])


        #conv = lambda img, core: Atb.dot(numpy.array(G.dot(core)) * numpy.array(Btb.dot(img)))
        # print(numpy.array(G.dot(core))*numpy.array(Btb.dot(img)))
        #print([G.dot(c) for c in core])
        #print(np.array([G.dot(c) for c in core]))


        # a=FlowVaribale([G.dot(c) for c in core]).dot(G.tolist())
        # print(a.shape())
        # b=FlowVaribale([Btb.dot(i) for i in img])*Btb.T.tolist()
        # print(np.array(a.toList())*np.array(b.toList()))
        # print(a.shape(),b.shape(),a,b)
        # c = Atb.dot(np.array(G.dot([G.dot(c) for c in core])).dot(G.T) * FlowVaribale([Btb.dot(i) for i in img]).dot(Btb.T)).dot(Atb.T)
        #print(c)
        #print((np.array(out)-np.array(c)).tolist())


# error 5 [[0.000628697824370340]]
# error 6 [[5.78310669399271e-5]]
# error 7 [[7.11768213672997e-6]]
# error 8 [[1.12571333604761e-6]]
# error 9 [[1.56247283878280e-5]]
# error 10 [[0.000213669661349197]]
# error 11 [[0.000618294369637229]]
# error 12 [[0.00168770164813312]]
# error 13 [[0.00958448156928075]]
# error 14 [[0.0313271056484478]]
# error 15 [[0.305877191667301]]


# [0.314462066001450, 13.072265625, 13.08203125, 5.960464477539062e-07, 20]
# dx 5.960464477539062e-07
# pridict [[0.288783938231063, -0.111227886175987], [-0.216866316390224, 0.170257366933683]]
# real [[0.009263985603628925, -0.027690843375215192], [-0.01804863392058006, 0.01899513164902322]]
# error 13.072265028953552 0.713136913182510

#
# dx 2.3283064365386963e-09
# pridict [[0.0315011480852263, -0.459971110801449], [-0.399149213524652, 0.126464260942470]]
# real [[0.009263985603628925, -0.027690843375215192], [-0.01804863392058006, 0.01899513164902322]]
# error 13.072265622671694 0.943087138805350
# pridict [[-0.624610293089063, -0.448323717187174], [-0.102397595881484, -0.214233272616967]]
# real [[0.009263985603628925, -0.027690843375215192], [-0.01804863392058006, 0.01899513164902322]]


