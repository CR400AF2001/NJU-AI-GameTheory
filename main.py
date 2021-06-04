import os
import numpy as np
from scipy.optimize import linprog

index = 0

def readPayoff(payoff, remain, n_player, actionNum):
    if remain == 0:
        point = np.zeros(n_player, dtype=np.int)
        global index
        for i in range(0, n_player):
            point[i] = payoff[index]
            index += 1
        return point
    else:
        newlist = readPayoff(payoff, remain - 1, n_player, actionNum)
        for i in range(0, actionNum[remain - 1]):
            if i == 0:
                newlist = np.expand_dims(newlist, 0).repeat(actionNum[remain - 1], axis=0)
            else:
                newlist[i] = readPayoff(payoff, remain - 1, n_player, actionNum)
    return newlist

def nash(in_path, out_path):
    # load file
    global index
    n_player = 0
    actionNum = []
    file = open(in_path, "r")
    allLines = file.readlines()
    for line in allLines:
        if '{' in line:
            line1 = line.split('{')
            line2 = line1[1].split('}')[0].split("\"")
            while '' in line2:
                line2.remove('')
            while ' ' in line2:
                line2.remove(' ')
            n_player = len(line2)
            line3 = line1[2].split('}')[0].split(" ")
            while '' in line3:
                line3.remove('')
            for i in line3:
                actionNum.append(int(i))
    payoff = allLines[-1].split(" ")
    while '' in payoff:
        payoff.remove('')
    index = 0
    payoffMaxtix = readPayoff(payoff, n_player, n_player, actionNum)
    file.close()
    # get NE
    result = []
    mixResult = []
    nowAction = np.zeros(n_player, dtype=np.int)
    notquit = 1
    while notquit == 1:
        flag = 1
        now = payoffMaxtix
        for n in range(0, n_player):
            now = now[nowAction[n]]
        for i in range(0, n_player):
            for j in range(0, actionNum[-(i+1)]):
                temp = payoffMaxtix
                for k in range(0, i):
                    temp = temp[nowAction[k]]
                temp = temp[j]
                for k in range(i + 1, n_player):
                    temp = temp[nowAction[k]]
                if now[-(i+1)] < temp[-(i+1)]:
                    flag = 0
        if flag == 1:
            result.append(list(nowAction))
        nowAction[-1] += 1
        for i in range(1, n_player + 1):
            if nowAction[-i] >= actionNum[i - 1]:
                nowAction[-i] = 0
                if i == n_player:
                    notquit = 0
                    break
                else:
                    nowAction[-(i + 1)] += 1
    if n_player == 2:
        c = [1]
        A = []
        b = []
        another = [0]
        u_bounds = (None, None)
        all_bounds = [u_bounds]
        for i in range(0, actionNum[0] - 1):
            c.append(0)
            another.append(1)
            all_bounds.append((0, 1))
        for i in range(0, actionNum[1]):
            temp = [-1]
            for j in range(0, actionNum[0] - 1):
                temp.append(payoffMaxtix[i][j][1] - payoffMaxtix[i][-1][1])
            A.append(temp)
            b.append(-payoffMaxtix[i][-1][1])
        A.append(another)
        b.append(1)
        c = np.array(c)
        A = np.array(A)
        b = np.array(b)
        res1 = linprog(c, A_ub=A, b_ub=b, bounds=tuple(all_bounds))
        c = [1]
        A = []
        b = []
        another = [0]
        u_bounds = (None, None)
        all_bounds = [u_bounds]
        for i in range(0, actionNum[1] - 1):
            c.append(0)
            another.append(1)
            all_bounds.append((0, 1))
        for i in range(0, actionNum[0]):
            temp = [-1]
            for j in range(0, actionNum[1] - 1):
                temp.append(payoffMaxtix[j][i][0] - payoffMaxtix[-1][i][0])
            A.append(temp)
            b.append(-payoffMaxtix[-1][i][0])
        A.append(another)
        b.append(1)
        c = np.array(c)
        A = np.array(A)
        b = np.array(b)
        res2 = linprog(c, A_ub=A, b_ub=b, bounds=tuple(all_bounds))
        mixResult.append([res1.x, res2.x])
    # write file
    file = open(out_path, "w")
    for i in result:
        resultstr = "("
        for n in range(0, n_player):
            if n != 0:
                resultstr += ','
            resultstr += '('
            for j in range(0, actionNum[n]):
                if j != 0:
                    resultstr += ','
                if j == i[n_player - 1 - n]:
                    resultstr += '1'
                else:
                    resultstr += '0'
            resultstr += ')'
        resultstr += ')'
        file.write(resultstr + '\n')
    if n_player == 2:
        for i in mixResult:
            flag = 1
            resultstr = "("
            resultstr += '('
            p = 1.0
            for j in range(0, actionNum[0] - 1):
                if abs(1.0 - i[0][j + 1]) < 10e-5:
                    flag = 2
                    resultstr += '1'
                    p -= 1
                elif abs(i[0][j + 1]) < 10e-5:
                    resultstr += '0'
                else:
                    resultstr += str(i[0][j + 1])
                    p -= i[0][j + 1]
                resultstr += ','
            if abs(1 - p) < 10e-5:
                flag = 2
                resultstr += '1'
            elif abs(p) < 10e-5:
                resultstr += '0'
            else:
                resultstr += str(p)
            resultstr += ')'
            resultstr += ','
            resultstr += '('
            p = 1.0
            for j in range(0, actionNum[1] - 1):
                if flag == 2 and abs(1.0 - i[1][j + 1]) < 10e-5:
                    flag = 0
                    resultstr += '1'
                    p -= 1
                elif abs(i[1][j + 1]) < 10e-5:
                    resultstr += '0'
                else:
                    resultstr += str(i[1][j + 1])
                    p -= i[1][j + 1]
                resultstr += ','
            if flag == 2 and abs(1 - p) < 10e-5:
                flag = 0
                resultstr += '1'
            elif abs(p) < 10e-5:
                resultstr += '0'
            else:
                resultstr += str(p)
            resultstr += ')'
            resultstr += ')'
            if flag != 0:
                file.write(resultstr + '\n')
    file.close()

if __name__ == '__main__':
    for f in os.listdir('input'):
        if f.endswith('.nfg'):
            nash('input/'+f, 'output/'+f.replace('nfg','ne'))
