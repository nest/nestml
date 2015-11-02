from sympy import *
from sympy.matrices import zeros
import numpy
from numpy.random import randint

a, h = symbols('a, h')
<#compress>
<#assign separator = "">
<#list variables as variable>${separator} ${variable} <#assign separator = ","></#list> = <#assign separator = ""> symbols('<#list variables as variable> ${separator} ${variable} <#assign separator = ","> </#list>')
</#compress>

rhs = ${expressionsPrettyPrinter.print(ode.getRhs())}
${eq.getLhsVariable()} = ${expressionsPrettyPrinter.print(eq.getRhs())}

firstDev = diff(rhs, ${ode.getLhsVariable()})
secondDev = diff(firstDev, ${ode.getLhsVariable()})
Ordnung = None

if secondDev == 0:
    print 'We have a linear differential equation!'
    order = None
    tmp_diffs = [${eq.getLhsVariable()}, diff(${eq.getLhsVariable()},t)]
    a_1 = solve(tmp_diffs[1] - a*${eq.getLhsVariable()}, a)
    SUM = tmp_diffs[1] - a_1[0] * ${eq.getLhsVariable()}
    if SUM == 0:
        order = 1
    else:
        for n in range(2, 10):
            tmp_diffs.append(diff(${eq.getLhsVariable()}, t, n))
            X = zeros(n)
            Y = zeros(n, 1)
            found = False
            for k in range(0, 100): # tries
                for i in range(0, n):
                    substitute = i+k
                    Y[i] = tmp_diffs[n].subs(t, substitute)
                    for j in range(0, n):
                        X[i, j] = tmp_diffs[j].subs(t, substitute)
                print "Try if X is invertable:"
                print X
                d = det(X)
                print "det(X) = " + str(d)
                if d != 0:
                    found = True
                    break
            if not found:
                print 'We have a problem'
                exit(1)
            VecA = X.inv() * Y
            SUM = 0
            for k in range(0, n):
                SUM += VecA[k]*diff(${eq.getLhsVariable()}, t, k)
            SUM -= tmp_diffs[n]
            print "SUM = " + str(simplify(SUM))
            if simplify(SUM) == sympify(0):
                order = n
                break

    if order is None:
        print 'We have a problem'
        exit(1)

    if order == 1:
        A = Matrix([[a_1[0], 0],
                [1/C_m, -1/Tau]])
    elif order == 2:
        # VecA only if Ordnung 2 or larger
        solutionpq = -VecA[1]/2 + sqrt(VecA[1]**2 / 4 + VecA[0])
        print simplify(VecA)
        A = Matrix([[VecA[1]+solutionpq, 0,         0     ],
                   [1,                -solutionpq, 0     ],
                   [0,                1/C_m,        -1/Tau]])
    elif order > 2:
        A = zeros(order)
        A[order-1, order-1] = -1/tau_in
        A[order-1, order-2] = 1/C_m
        for j in range(0, order-1):
            A[0, j] = VecA[order-j-1]
        for i in range(1,order-1):
            A[i,i-1]=1

    print simplify(A)
    #exit(0)
    print("Compute propagatormatrix...")
    propogatorMatrix = simplify(exp(A*h))
    print "Propagatormatrix:"
    print propogatorMatrix

    if order == 2:
        print 'Solution matrix is printed into solution.matrix.tmp'
        f = open('solution.matrix.tmp', 'w')
        f.write("P00 real = " + str(propogatorMatrix[0, 0]) + "# P00\n")
        f.write("P01 real = " + str(propogatorMatrix[0, 1]) + "# P01\n")
        f.write("P02 real = " + str(propogatorMatrix[0, 2]) + "# P02\n")
        f.write("P10 real = " + str(propogatorMatrix[1, 0]) + "# P10\n")
        f.write("P11 real = " + str(propogatorMatrix[1, 1]) + "# P11\n")
        f.write("P12 real = " + str(propogatorMatrix[1, 2]) + "# P12\n")
        f.write("P20 real = " + str(propogatorMatrix[2, 0]) + "# P20\n")
        f.write("P21 real = " + str(propogatorMatrix[2, 1]) + "# P21\n")
        f.write("P22 real = " + str(propogatorMatrix[2, 2]) + "# P22\n")
else:
    print 'Not a linear differential equation'
