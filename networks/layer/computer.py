from math import *
#while True:print(" result: "+str(eval(input("formulas:\n"))))
# methods={"+":(1,lambda a,b:a+b),"-":(1,lambda a,b:a-b),"*":(2,lambda a,b:a*b),"/":(2,lambda a,b:a/b),"^":(3,lambda a,b:a**b)}
# functions={"sin":lambda x:sin(x),"cos":lambda x:cos(x),"log":lambda x,b:log(b,x)}
# while True:
#     f,weight=input("formula:\n"),0
#     def add(i):
#         global weight
#         if f[i] in methods.keys():
#             return (f[i], methods[f[i]][0]+weight)
#         if f[i] == "(": weight += 4
#         if f[i] == ")": weight -= 4
#     chars=[j for  j in [add(i) for i in range(len(f))] if j !=None ] #提取运算符给运算符分配权重
#     for k in list(methods.keys()):f=f.replace("(", "").replace(")", "").replace(k,"|") #提取数字
#     numbers=f.split("|")
#     for i in range(len(numbers)):
#         for k in functions.keys():
#             if k in str(numbers[i]):
#                 numbers[i]=functions[k](*[float(j) for j in str(numbers[i]).replace(k,"").split(",")])
#         numbers[i]=float(numbers[i])
#     result = numbers[0]
#     if len(numbers)>1:
#         for p in [i for i in range(max([j[1] for j in chars]))][::-1]:
#             for i in range(len(chars)):
#                 if chars[i][1] == p + 1:
#                     result = methods[chars[i][0]][1](numbers[i], numbers[i + 1])
#                     numbers[i], numbers[i + 1]=result, result
#                     for j in range(i+1,len(chars)):
#                         if chars[j][1]> chars[i][1]:
#                             numbers[j+1]=result
#                         else:break;
#                     for j in [j for j in range(0,i-1)][::-1]:
#                         if chars[j][1]> chars[i][1]:
#                             numbers[j-1]=result
#                         else:break;
#     print("  result: "+str(result))

# def a(n):
#     if n<2:
#         return 1
#     return a(n-1)+a(n-2)
# print(a(6))
import matplotlib.pyplot as plt

def hanio():
    import random
    n = 5
    count = 0
    towers = [[1,2], [3,4], [6]]
    results=""
    def r():
        def f(e,prev=0):
            if len(e) != n:
                return True
            for i in e:
                if i < prev: return True
                prev = i
            return False
        return [f(e) for e in towers].count(False)==0

    while r():
        indexes=random.sample([0,1,2],2)

        a,b=[towers[i] for i in indexes]
        if len(a)>0 and (len(b)==0 or b[0]>a[0]):
            b.insert(0,a.pop(0))
            results += chr(65 + indexes[0]) + "-->" + chr(65 + indexes[1]) + "\n"
            count+=1
    return count

plt.plot([hanio()for i in range(100)])
plt.text(2.8, 7,"hanio")
plt.show()





from math import *
#while True:print(" result: "+str(eval(input("formulas:\n"))))
methods={"+":(1,lambda a,b:a+b),"-":(1,lambda a,b:a-b),"*":(2,lambda a,b:a*b),"/":(2,lambda a,b:a/b),"^":(3,lambda a,b:a**b)}
functions={"sin":lambda x:sin(x),"cos":lambda x:cos(x),"log":lambda x,b:log(b,x)}
while True:
    f,weight=input("formula:\n"),0
    def add(i):
        global weight
        if f[i] in methods.keys():
            return (f[i], methods[f[i]][0]+weight)
        if f[i] == "(": weight += 4
        if f[i] == ")": weight -= 4
    chars=[j for  j in [add(i) for i in range(len(f))] if j !=None ]
    for k in list(methods.keys()):f=f.replace("(", "").replace(")", "").replace(k,"|")
    numbers=f.split("|")
    for i in range(len(numbers)):
        for k in functions.keys():
            if k in str(numbers[i]):
                numbers[i]=functions[k](*[float(j) for j in str(numbers[i]).replace(k,"").split(",")])
        numbers[i]=float(numbers[i])
    result = numbers[0]
    if len(numbers) >1:
        for p in [i for i in range(max([j[1] for j in chars]))][::-1]:
            for i in range(len(chars)):
                if chars[i][1] == p + 1:
                    result = methods[chars[i][0]][1](numbers[i], numbers[i + 1])
                    numbers[i], numbers[i + 1]=result, result
                    for j in range(i+1,len(chars)):
                        if chars[j][1]> chars[i][1]:
                            numbers[j+1]=result
                        else:break;
                    for j in [j for j in range(0,i-1)][::-1]:
                        if chars[j][1]> chars[i][1]:
                            numbers[j-1]=result
                        else:break;
    print("  result: "+str(result))