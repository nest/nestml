from sympy import *
from sympy.matrices import zeros

__a__, __h__ = symbols('__a__ __h__')
<#compress>
    <#list variables as variable> ${variable.getName()} , </#list> = symbols('<#list variables as variable> ${variable.getName()} </#list>')
</#compress>

# Handle aliases
<#list aliases as alias>
${alias.getName()} = ${printer.print(alias.getDeclaringExpression().get())}
</#list>

# Shapes must be symbolic for the differetiation step
rhsTmp = ${printer.print(ode.getRhs())}
constantInputs = simplify(1/diff(rhsTmp, ${shapes[0].getLhs()}) * (rhsTmp - diff(rhsTmp, ${ode.getLhs().getSimpleName()})*${ode.getLhs().getSimpleName()}) - (
<#assign operator = "">
<#compress> <#list shapes as eq>
${operator} ${eq.getLhs()}
<#assign operator = "+">
</#list> </#compress>
))

# TODO take the comment for the source model
<#list shapes as eq>
${eq.getLhs()} = ${printer.print(eq.getRhs())}
</#list>
rhs = ${printer.print(ode.getRhs())}
dev${ode.getLhs().getSimpleName()} = diff(rhs, ${ode.getLhs().getSimpleName()})
dev_t_dev${ode.getLhs().getSimpleName()} = diff(dev${ode.getLhs().getSimpleName()}, t)

if dev_t_dev${ode.getLhs().getSimpleName()} == 0:
    print 'We have a linear differential equation!'

    # a list of defining exressions of shapes
    shapes = [<#compress> <#list shapes as eq> ${eq.getLhs()}, </#list> </#compress>]
    # a list of intergers. each number represents the order of the differential equations corresponding to its shape
    orders = [None]*len(shapes)
    # a list of propagator matrices of the dimension [order x order]
    Ps = [None]*len(shapes)
    # list of list of derivatives of elements in "shapes" from 0 to order-1
    tmp_diffs = [None]*len(shapes)

    # Goal: produce a propagator matrix for each shape
    for shape_index in range(0, len(shapes)):
        # tmp_diffs is needed to calculate PSCInitialValues and the propagator matrix
        tmp_diffs[shape_index] = [shapes[shape_index], diff(shapes[shape_index], t)]
        # if this element of shapes solves a first order linear differential equation, we calculate the corresponding factor
        a_1 = solve(tmp_diffs[shape_index][1] - __a__ * shapes[shape_index], __a__)
        # SUM equals 0 iff. this element of shape is the solution of  a first order linear differential equations
        SUM = tmp_diffs[shape_index][1] - a_1[0] * shapes[shape_index]

        if SUM == 0:
            # we have a first order linear differential equation
            orders[shape_index] = 1
        else:
            # we check if this element in shape sastisfies a linear differential equation upto order 10
            for n in range(2, 10):
                # add new differential of the
                tmp_diffs[shape_index].append(diff(shapes[shape_index], t, n))
                # helps to calculate Ps. Datatype Matrix [n x n]
                X = zeros(n)
                # Datatype: Vector [n x 1]
                Y = zeros(n, 1)
                found = False
                for k in range(0, 100): # tries
                    for i in range(0, n):
                        substitute = i+k
                        Y[i] = tmp_diffs[shape_index][n].subs(t, substitute)
                        for j in range(0, n):
                            X[i, j] = tmp_diffs[shape_index][j].subs(t, substitute)
                    # "Try if X is invertable:"
                    d = det(X)
                    if d != 0:
                        found = True
                        break
                if not found:
                    # TODO print out the status into a file to notify the code generator about the error
                    print 'Error: could not find X. The equations will be solved numerically.'
                    # TODO jump to X
                    exit(1)
                VecA = X.inv() * Y
                SUM = 0
                # SUM equals 0 iff. this element of shape is the solution of  a nth order linear differential equations
                for k in range(0, n):
                    # sum up derivatives of this element of shapes
                    SUM += VecA[k]*diff( shapes[shape_index], t, k)
                SUM -= tmp_diffs[shape_index][n]
                print "SUM = " + str(simplify(SUM))
                if simplify(SUM) == sympify(0):
                    orders[shape_index] = n
                    break

        if orders[shape_index] is None:
            print 'The equations will be solved numerically.'
            exit(1) # TODO jump to X

        # calculate -1/Tau
        c1 = diff(rhs, ${ode.getLhs().getSimpleName()})
        # The symbol must be declared again. Otherwise, the right hand side will be used for the derivative
        ${shapes[0].getLhs()} = symbols("${shapes[0].getLhs()}")
        c2 = diff( ${printer.print(ode.getRhs())} , ${shapes[0].getLhs()})

        # define matrices depending on order
        # for order 1 and 2 A is lower triangular matrix
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
        Ps[shape_index] = simplify(exp(A * __h__))
        print "Computed propagatormatrix is:"
        print Ps[shape_index]

    shapes = [<#compress> <#list shapes as eq> "${eq.getLhs()}", </#list> </#compress>]

    stateVariablesFile = open('state.variables.tmp', 'w')
    initialValueFile = open('pscInitialValues.tmp', 'w')
    stateVectorTmpDeclarationsFile = open('state.vector.tmp.declarations.tmp', 'w')
    stateVectorUpdateSteps = open('state.vector.update.steps.tmp', 'w')
    stateVectorTmpBackAssignmentsFile = open('state.vector.tmp.back.assignments.tmp', 'w')

    stateVectors = zeros(max(orders) + 1, len(shapes))
    for shapeIndex in range(0, len(shapes)):
        stateVariables = ["y1_", "y2_", "y3_", "y4_", "y5_", "y6_", "y7_", "y8_", "y9_", "y10_"]
        var((str(shapes[shapeIndex]) + " ,").join(stateVariables))
        for i in range(0, orders[shapeIndex]):
            stateVectors[i, shapeIndex] = eval(stateVariables[i] + shapes[shapeIndex])
            stateVariablesFile.write(stateVariables[i] + shapes[shapeIndex] + "\n")
        stateVectors[orders[shapeIndex], shapeIndex] = ${ode.getLhs().getSimpleName()}

        pscInitialValues = tmp_diffs[shapeIndex]
        for i in range(0, orders[shapeIndex]):
            initialValue = simplify(pscInitialValues[orders[shapeIndex] - i - 1].subs(t, 0))
            if initialValue != 0:
                initialValueFile.write(stateVariables[i] + shapes[shapeIndex] + "PSCInitialValue real = " + str(
                    initialValue) + "# PSCInitial value\n")

        for i in reversed(range(0, orders[shapeIndex])):
            stateVectors[i, shapeIndex] = stateVariables[i] + shapes[shapeIndex]

        if orders[shapeIndex] > 2:
            for i in reversed(range(0, orders[shapeIndex])):
                stateVectorTmpDeclarationsFile.write(stateVariables[i] + shapes[shapeIndex] + "_tmp real\n")
            for i in reversed(range(0, orders[shapeIndex])):
                stateVectorUpdateSteps.write(stateVariables[i] + shapes[shapeIndex] + "_tmp" + " = " + str(simplify(Ps[shapeIndex] * stateVectors[:, shapeIndex])[i]) + "\n")
            for i in reversed(range(0, orders[shapeIndex])):
                stateVectorTmpBackAssignmentsFile.write(stateVariables[i] + shapes[shapeIndex] + " = " + stateVariables[i] + shapes[shapeIndex] + "_tmp" + "\n")

        else:
            for i in reversed(range(0, orders[shapeIndex])):
                stateVectorUpdateSteps.write(stateVariables[i] + shapes[shapeIndex] + " = " + str(
                    simplify(Ps[shapeIndex] * stateVectors[:, shapeIndex])[i]) + "\n")

    f = open('P30.tmp', 'w')
    f.write("P30 real = " + str(simplify(c2 / c1 * (exp(__h__ * c1) - 1))) + "# P00 expression")

    updateStep = open('propagator.step.tmp', 'w')
    # the result matrix of matrix with 1 element. therefore, take it by [] operator
    updateStep.write("${ode.getLhs().getSimpleName()} = P30 * (" + str(constantInputs) + ") + " + str(
        (Ps[0][orders[0], orders[0]] * stateVectors.col(0)[orders[0]])) + "\n")

    propagatorMatrixFile = open('propagator.matrix.tmp', 'w')
    tmpPropagator = zeros(len(Ps[shapeIndex].row(0)), len(Ps[shapeIndex].col(0)))

    for rowIndex in range(0, len(Ps[shapeIndex].row(0))):
        for colIndex in range(0, len(Ps[shapeIndex].col(0))):
            propagatorMatrixFile.write(
                "P" + str(rowIndex) + str(colIndex) + " real = " + str(Ps[shapeIndex][rowIndex, colIndex]) + "\n")
            tmpPropagator[rowIndex, colIndex] = symbols("P" + str(rowIndex) + str(colIndex));
    print(str(tmpPropagator))

    for shapeIndex in range(0, len(shapes)):
        updateStep.write("${ode.getLhs().getSimpleName()} += " + str((tmpPropagator[1:(orders[shapeIndex] + 1),
                                        0:(orders[shapeIndex])] * stateVectors.col(shapeIndex)[0:orders[shapeIndex],
                                                                  0])[orders[shapeIndex] - 1]) + "\n")

    solverType = open('solverType.tmp', 'w')
    solverType.write("exact")
else:
    print 'This differential equation will be converted into the implicit form'

    # a list of defining exressions of shapes
    shapes = [<#compress> <#list shapes as eq> ${eq.getLhs()}, </#list> </#compress>]
    # a list of intergers. each number represents the order of the differential equations corresponding to its shape
    orders = [None]*len(shapes)
    # a list of propagator matrices of the dimension [order x order]
    Ps = [None]*len(shapes)
    # list of list of derivatives of elements in "shapes" from 0 to order-1
    tmp_diffs = [None]*len(shapes)

    # Goal: produce a propagator matrix for each shape
    for shape_index in range(0, len(shapes)):
        # tmp_diffs is needed to calculate PSCInitialValues and the propagator matrix
        tmp_diffs[shape_index] = [shapes[shape_index], diff(shapes[shape_index], t)]
        # if this element of shapes solves a first order linear differential equation, we calculate the corresponding factor
        a_1 = solve(tmp_diffs[shape_index][1] - __a__ * shapes[shape_index], __a__)
        # SUM equals 0 iff. this element of shape is the solution of  a first order linear differential equations
        SUM = tmp_diffs[shape_index][1] - a_1[0] * shapes[shape_index]

        if SUM == 0:
            # we have a first order linear differential equation
            orders[shape_index] = 1
        else:
            # we check if this element in shape sastisfies a linear differential equation upto order 10
            for n in range(2, 10):
                # add new differential of the
                tmp_diffs[shape_index].append(diff(shapes[shape_index], t, n))
                # helps to calculate Ps. Datatype Matrix [n x n]
                X = zeros(n)
                # Datatype: Vector [n x 1]
                Y = zeros(n, 1)
                found = False
                for k in range(0, 100): # tries
                    for i in range(0, n):
                        substitute = i+k
                        Y[i] = tmp_diffs[shape_index][n].subs(t, substitute)
                        for j in range(0, n):
                            X[i, j] = tmp_diffs[shape_index][j].subs(t, substitute)
                    # "Try if X is invertable:"
                    d = det(X)
                    if d != 0:
                        found = True
                        break
                if not found:
                    # TODO print out the status into a file to notify the code generator about the error
                    print 'Error: could not find X. The equations will be solved numerically.'
                    # TODO jump to X
                    exit(1)
                VecA = X.inv() * Y
                SUM = 0
                # SUM equals 0 iff. this element of shape is the solution of  a nth order linear differential equations
                for k in range(0, n):
                    # sum up derivatives of this element of shapes
                    SUM += VecA[k]*diff( shapes[shape_index], t, k)
                SUM -= tmp_diffs[shape_index][n]
                print "SUM = " + str(simplify(SUM))
                if simplify(SUM) == sympify(0):
                    orders[shape_index] = n
                    break

        if orders[shape_index] is None:
            print 'The equations will be solved numerically.'
            exit(1) # TODO jump to X
