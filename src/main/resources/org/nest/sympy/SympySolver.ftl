from sympy import *
from sympy.matrices import zeros
import numpy
from numpy.random import randint

# TODO why a?
a, h = symbols('a h')
<#compress>
    var('<#list variables as variable> ${variable.getName()} </#list>')
</#compress>

<#list aliases as alias>
${alias.getName()} = ${printer.print(alias.getDeclaringExpression().get())}
</#list>

<#list EQs as eq>
${eq.getLhs()} = ${printer.print(eq.getRhs())}
</#list>
rhs = ${printer.print(ode.getRhs())}

var("${EQs[0].getLhs()}")
rhsTmp = ${printer.print(ode.getRhs())}
contantTerm = simplify(rhsTmp - diff(rhsTmp, ${ode.getLhs()})*${ode.getLhs()} - diff(rhsTmp, ${EQs[0].getLhs()})*${EQs[0].getLhs()})
<#list EQs as eq>
${eq.getLhs()} = ${printer.print(eq.getRhs())}
</#list>


dev${ode.getLhs()} = diff(rhs, ${ode.getLhs()})
dev_t_dev${ode.getLhs()} = diff(dev${ode.getLhs()}, t)

solverType = open('solverType.property', 'w')
if dev_t_dev${ode.getLhs()} == 0:
    print 'We have a linear differential equation!'
    solverType.write("exact")
    order = None

    shapes = [<#compress> <#list EQs as eq> ${eq.getLhs()}, </#list> </#compress>]
    orders = [None]*len(shapes)
    Ps = [None]*len(shapes)
    tmp_diffs = [None]*len(shapes)

    for shape_index in range(0, len(shapes)):
        tmp_diffs[shape_index] = [shapes[shape_index], diff(shapes[shape_index], t)]
        a_1 = solve(tmp_diffs[shape_index][1] - a * shapes[shape_index], a)
        SUM = tmp_diffs[shape_index][1] - a_1[0] * shapes[shape_index]

        if SUM == 0:
            orders[shape_index] = 1
        else:
            for n in range(2, 10):
                tmp_diffs[shape_index].append(diff(shapes[shape_index], t, n))
                X = zeros(n)
                Y = zeros(n, 1)
                found = False
                for k in range(0, 100): # tries
                    for i in range(0, n):
                        substitute = i+k
                        Y[i] = tmp_diffs[shape_index][n].subs(t, substitute)
                        for j in range(0, n):
                            X[i, j] = tmp_diffs[shape_index][j].subs(t, substitute)
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
                    SUM += VecA[k]*diff( shapes[shape_index], t, k)
                SUM -= tmp_diffs[shape_index][n]
                print "SUM = " + str(simplify(SUM))
                if simplify(SUM) == sympify(0):
                    orders[shape_index] = n
                    break

        if orders[shape_index] is None:
            print 'We have a problem'
            exit(1)

        c1 = diff(rhs, V)
        ${EQs[0].getLhs()} = symbols("${EQs[0].getLhs()}")
        c2 = diff( ${printer.print(ode.getRhs())} , ${EQs[0].getLhs()})

        if orders[shape_index] == 1:
            A = Matrix([[a_1[0], 0],
                    [c2, c1]])
        elif orders[shape_index] == 2:
            # VecA only if order 2 or larger
            solutionpq = -VecA[1]/2 + sqrt(VecA[1]**2 / 4 + VecA[0])
            print simplify(VecA)
            A = Matrix([[VecA[1]+solutionpq, 0,             0     ],
                       [1,                   -solutionpq,   0     ],
                       [0,                   c2,        c1]])
        elif orders[shape_index] > 2:
            A = zeros(order)
            A[order-1, order-1] = c1
            A[order-1, order-2] = c2
            for j in range(0, order-1):
                A[0, j] = VecA[order-j-1]
            for i in range(1,order-1):
                A[i,i-1]=1
        print("A Matrix:")
        print(str(simplify(A)))
        print("Begins long running computation of the propagatormatrix.")
        Ps[shape_index] = simplify(exp(A * h))
        print "Computed propagatormatrix is:"
        print Ps[shape_index]

    shapes = [<#compress> <#list EQs as eq> "${eq.getLhs()}", </#list> </#compress>]

    statefile = open('state.vector.mat', 'w')
    y_vector = [zeros(max(orders) + 1, 1)] * len(shapes)
    stateVariablesFile = open('state.variables.mat', 'w')
    initialValue = open('pscInitialValue.mat', 'w')
    for index in range(0, len(shapes)):
        stateVariables = ["y1_", "y2_", "y3_", "y4_", "y5_", "y6_", "y7_", "y8_", "y9_", "y10_"]
        var((str(shapes[index]) + " ,").join(stateVariables))

        for i in reversed(range(0, orders[index])):
            y_vector[index][i] = eval(stateVariables[i] + shapes[index])
            stateVariablesFile.write(stateVariables[i] + shapes[index] + "\n")
        y_vector[index][orders[index]] = V

        pscInitialValues = list(reversed(tmp_diffs[index]))

        for i in range(0, orders[index]-1):
            statefile.write(stateVariables[i] + shapes[index] + " = " + str(simplify(Ps[index] * y_vector[index])[i]) + "\n")
            initialValue.write(stateVariables[i] + shapes[index] + "PSCInitialValue real = " + str(simplify(pscInitialValues[i].subs(t, 0))) + "# PSCInitial value\n")

    f = open('P30.mat', 'w')
    f.write("P30 real = " + str(simplify(c2 / c1 * (exp(h * c1) - 1))) + "# P00 expression")

    tmp = (Ps[0] * y_vector[0])[orders[0]]

    for index in range(1, len(shapes)):
        tmp += (Ps[index][0:(orders[index]-1), 0:(orders[index]-1)] * Matrix(y_vector[index][0:(orders[index]-1)]))[0]

    updateStep = open('update.step.mat', 'w')
    updateStep.write("V = P30 * (" + str(contantTerm) + ") + " + str(tmp))

else:
    print 'Not a linear differential equation'
    solverType.write("numeric")
    f = open('explicitSolution.mat', 'w')
<#list EQs as eq>
    # compute values for the  ${eq.getLhs()} equation
    order = None
    tmp_diffs = [ ${eq.getLhs()}, diff( ${eq.getLhs()},t)]
    a_1 = solve(tmp_diffs[1] - a* ${eq.getLhs()}, a)
    SUM = tmp_diffs[1] - a_1[0] *  ${eq.getLhs()}
    if SUM == 0:
        order = 1
    else:
        for n in range(2, 10):
            tmp_diffs.append(diff( ${eq.getLhs()}, t, n))
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
                SUM += VecA[k]*diff(${eq.getLhs()}, t, k)
            SUM -= tmp_diffs[n]
            print "SUM = " + str(simplify(SUM))
            if simplify(SUM) == sympify(0):
                order = n
                break

    if order is None:
        print 'We have a problem'
        exit(1)

    c1 = diff(rhs, ${ode.getLhs()})
    ${eq.getLhs()} = symbols("${eq.getLhs()}")
    c2 = diff(${printer.print(ode.getRhs())}, ${eq.getLhs()})

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
        f.write("D${eq.getLhs()}' = D${eq.getLhs()}*" + str(simplify(A[0,0])) +"\n")
        f.write("${eq.getLhs()}' = D${eq.getLhs()} + ${eq.getLhs()} *" + str(simplify(A[1,1])) + "\n")

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