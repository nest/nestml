from sympy import *
from sympy.matrices import zeros
import numpy
from numpy.random import randint
# TODO why a?
a, h = symbols('a h')
<#compress>
    var('<#list variables as variable> ${variable} </#list>')
</#compress>

<#list EQs as eq>
${eq.getLhsVariable()} = ${expressionsPrettyPrinter.print(eq.getRhs())}
</#list>
rhs = ${expressionsPrettyPrinter.print(ode.getRhs())}

var("${EQs[0].getLhsVariable()}")
rhsTmp = ${expressionsPrettyPrinter.print(ode.getRhs())}
contantTerm = simplify(rhsTmp - diff(rhsTmp, ${ode.getLhsVariable()})*${ode.getLhsVariable()} - diff(rhsTmp, ${EQs[0].getLhsVariable()})*${EQs[0].getLhsVariable()})
<#list EQs as eq>
${eq.getLhsVariable()} = ${expressionsPrettyPrinter.print(eq.getRhs())}
</#list>


dev${ode.getLhsVariable()} = diff(rhs, ${ode.getLhsVariable()})
dev_t_dev${ode.getLhsVariable()} = diff(dev${ode.getLhsVariable()}, t)

solverType = open('solverType.property', 'w')
if dev_t_dev${ode.getLhsVariable()} == 0:
    print 'We have a linear differential equation!'
    solverType.write("exact")
    order = None
    tmp_diffs = [ ${EQs[0].getLhsVariable()}, diff( ${EQs[0].getLhsVariable()},t)]
    a_1 = solve(tmp_diffs[1] - a* ${EQs[0].getLhsVariable()}, a)
    SUM = tmp_diffs[1] - a_1[0] *  ${EQs[0].getLhsVariable()}
    if SUM == 0:
        order = 1
    else:
        for n in range(2, 10):
            tmp_diffs.append(diff( ${EQs[0].getLhsVariable()}, t, n))
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
                SUM += VecA[k]*diff( ${EQs[0].getLhsVariable()}, t, k)
            SUM -= tmp_diffs[n]
            print "SUM = " + str(simplify(SUM))
            if simplify(SUM) == sympify(0):
                order = n
                break

    if order is None:
        print 'We have a problem'
        exit(1)

    c1 = diff(rhs, ${ode.getLhsVariable()})
    ${EQs[0].getLhsVariable()} = symbols("${EQs[0].getLhsVariable()}")
    c2 = diff(${expressionsPrettyPrinter.print(ode.getRhs())}, ${EQs[0].getLhsVariable()})

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

    for i in reversed(range(0, order)):
        y_vector[i] = eval(stateVariables[i])
    y_vector[order] = ${ode.getLhsVariable()}

    f = open('state.vector.mat', 'w')
    for i in range(0, order):
        f.write(stateVariables[i] + " = " + str(simplify(propagatorMatrix*y_vector)[i]) + "# Update\n")

    f = open('update.step.mat', 'w')
    f.write("V = P30 * (" + str(contantTerm) + ") + " + str(simplify(propagatorMatrix*y_vector)[order]))

    f = open('pscInitialValue.mat', 'w')
    f.write("PSCInitialValue real = " + str(simplify(X[0, 1])) + "# PSCInitial value")

    f = open('P30.mat', 'w')
    f.write("P30 real = " + str(simplify(c2/c1*(exp(h*c1)-1))) + "# P00 expression")

else:
    print 'Not a linear differential equation'
    solverType.write("numeric")
    f = open('explicitSolution.mat', 'w')
<#list EQs as eq>
    # compute values for the  ${eq.getLhsVariable()} equation
    order = None
    tmp_diffs = [ ${eq.getLhsVariable()}, diff( ${eq.getLhsVariable()},t)]
    a_1 = solve(tmp_diffs[1] - a* ${eq.getLhsVariable()}, a)
    SUM = tmp_diffs[1] - a_1[0] *  ${eq.getLhsVariable()}
    if SUM == 0:
        order = 1
    else:
        for n in range(2, 10):
            tmp_diffs.append(diff( ${eq.getLhsVariable()}, t, n))
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

    c1 = diff(rhs, ${ode.getLhsVariable()})
    ${eq.getLhsVariable()} = symbols("${eq.getLhsVariable()}")
    c2 = diff(${expressionsPrettyPrinter.print(ode.getRhs())}, ${eq.getLhsVariable()})

    if order == 1:
        A = Matrix([[a_1[0], 0],
                [c2, c1]])

        f.write("y1' = y1 * " + str(A[0, 0]) + "\n")
    elif order == 2:
        # VecA only if order 2 or larger
        solutionpq = -VecA[1]/2 + sqrt(VecA[1]**2 / 4 + VecA[0])
        print simplify(VecA)
        A = Matrix([[VecA[1]+solutionpq, 0,             0     ],
                   [1,                   -solutionpq,   0     ],
                   [0,                   c2,        c1]])
        f.write("D${eq.getLhsVariable()}' = D${eq.getLhsVariable()}*" + str(simplify(A[0,0])) +"\n")
        f.write("${eq.getLhsVariable()}' = D${eq.getLhsVariable()} + ${eq.getLhsVariable()} *" + str(simplify(A[1,1])) + "\n")

    elif order > 2:
        A = zeros(order)
        A[order-1, order-1] = c1
        A[order-1, order-2] = c2
        for j in range(0, order-1):
            A[0, j] = VecA[order-j-1]
        for i in range(1,order-1):
            A[i,i-1]=1

        y1_derivation = "y1' = "
        separator = ""
        for i in range(0, order-1):
            y1_derivation = separator + "y"+str(i)*str(simplify(A[0,i-1]))
            separator = "+"
        f.write()

        for i in range(2, order+1):
            f.write("y" + i + "=" + "y" + (i-1)+"\n")

</#list>