from sympy import *
from sympy.matrices import zeros
import numpy
from numpy.random import randint

a, h = symbols('a, h')
var(' tau_syn t tau_syn t Tau V C_m G ')
rhs = (-1)/Tau*V+1/C_m*G
G = (E/tau_syn)*t*exp((-1)/tau_syn*t)


firstDev = diff(rhs, V)
secondDev = diff(firstDev, V)

if secondDev == 0:
    print 'We have a linear differential equation!'
    order = None
    tmp_diffs = [ G, diff( G,t)]
    a_1 = solve(tmp_diffs[1] - a* G, a)
    SUM = tmp_diffs[1] - a_1[0] *  G
    if SUM == 0:
        order = 1
    else:
        for n in range(2, 10):
            tmp_diffs.append(diff( G, t, n))
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
                SUM += VecA[k]*diff( G, t, k)
            SUM -= tmp_diffs[n]
            print "SUM = " + str(simplify(SUM))
            if simplify(SUM) == sympify(0):
                order = n
                break

    if order is None:
        print 'We have a problem'
        exit(1)

    c1 = diff(rhs, V)
    G = symbols("G")
    c2 = diff((-1)/Tau*V+1/C_m*G, G)

    if order == 1:
        A = Matrix([[a_1[0], 0],
                [c2, c1]])
    elif order == 2:


        # VecA only if order 2 or larger
        solutionpq = -VecA[1]/2 + sqrt(VecA[1]**2 / 4 + VecA[0])
        print simplify(VecA)
        A = Matrix([[VecA[1]+solutionpq, 0,             0     ],
                   [1,                   -solutionpq,   0     ],
                   [0,                   c2,        c1]])
    elif order > 2:
        A = zeros(order)
        A[order-1, order-1] = c1
        A[order-1, order-2] = c2
        for j in range(0, order-1):
            A[0, j] = VecA[order-j-1]
        for i in range(1,order-1):
            A[i,i-1]=1

    print("Begins long running computation of the propagatormatrix.")
    propagatorMatrix = simplify(exp(A*h))
    print "Computed propagatormatrix is:"
    print propagatorMatrix

    stateVariables = ["y1", "y2", "y3", "y4", "y5", "y6", "y7", "y8", "y9", "y10"]
    var(",".join(stateVariables))

    y_vector = zeros(order+1, 1)

    for i in range(0, order):
        y_vector[i] = eval(stateVariables[i])
    y_vector[order] = V

    f = open('state.vector.mat', 'w')
    f.write(str(order) + "\n")
    for i in range(0, order):
        f.write(stateVariables[i] + " = " + str(simplify(propagatorMatrix*y_vector)[i]) + "# Update\n")

    f = open('update.step.mat', 'w')
    # TODO it is a hack
    f.write("V = P30 * (y0 + I_e) + " + str(simplify(propagatorMatrix*y_vector)[order]))

    f = open('pscInitialValue.mat', 'w')
    f.write("PSCInitialValue real = " + str(simplify(X[0, 1])) + "# PSCInitial value")

    f = open('P30.mat', 'w')
    f.write("P30 real = " + str(simplify(c2/c1*(exp(h*c1)-1))) + "# P00 expression")

else:
    print 'Not a linear differential equation'

