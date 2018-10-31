// Generated from PyNestMLParser.g4 by ANTLR 4.7.1
import org.antlr.v4.runtime.tree.ParseTreeVisitor;

/**
 * This interface defines a complete generic visitor for a parse tree produced
 * by {@link PyNestMLParser}.
 *
 * @param <T> The return type of the visit operation. Use {@link Void} for
 * operations with no return type.
 */
public interface PyNestMLParserVisitor<T> extends ParseTreeVisitor<T> {
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#dataType}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDataType(PyNestMLParser.DataTypeContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#unitType}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitUnitType(PyNestMLParser.UnitTypeContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#expression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitExpression(PyNestMLParser.ExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#simpleExpression}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSimpleExpression(PyNestMLParser.SimpleExpressionContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#unaryOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitUnaryOperator(PyNestMLParser.UnaryOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#bitOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitBitOperator(PyNestMLParser.BitOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#comparisonOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitComparisonOperator(PyNestMLParser.ComparisonOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#logicalOperator}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLogicalOperator(PyNestMLParser.LogicalOperatorContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#variable}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitVariable(PyNestMLParser.VariableContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#functionCall}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFunctionCall(PyNestMLParser.FunctionCallContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#odeFunction}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitOdeFunction(PyNestMLParser.OdeFunctionContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#odeEquation}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitOdeEquation(PyNestMLParser.OdeEquationContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#odeShape}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitOdeShape(PyNestMLParser.OdeShapeContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#block}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitBlock(PyNestMLParser.BlockContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#stmt}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitStmt(PyNestMLParser.StmtContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#compoundStmt}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitCompoundStmt(PyNestMLParser.CompoundStmtContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#smallStmt}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSmallStmt(PyNestMLParser.SmallStmtContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#assignment}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitAssignment(PyNestMLParser.AssignmentContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#declaration}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDeclaration(PyNestMLParser.DeclarationContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#anyMagicKeyword}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitAnyMagicKeyword(PyNestMLParser.AnyMagicKeywordContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#returnStmt}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitReturnStmt(PyNestMLParser.ReturnStmtContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#ifStmt}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitIfStmt(PyNestMLParser.IfStmtContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#ifClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitIfClause(PyNestMLParser.IfClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#elifClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitElifClause(PyNestMLParser.ElifClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#elseClause}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitElseClause(PyNestMLParser.ElseClauseContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#forStmt}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitForStmt(PyNestMLParser.ForStmtContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#whileStmt}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitWhileStmt(PyNestMLParser.WhileStmtContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#nestMLCompilationUnit}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitNestMLCompilationUnit(PyNestMLParser.NestMLCompilationUnitContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#neuron}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitNeuron(PyNestMLParser.NeuronContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#body}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitBody(PyNestMLParser.BodyContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#synapse}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSynapse(PyNestMLParser.SynapseContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#synapseBody}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSynapseBody(PyNestMLParser.SynapseBodyContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#blockWithVariables}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitBlockWithVariables(PyNestMLParser.BlockWithVariablesContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#updateBlock}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitUpdateBlock(PyNestMLParser.UpdateBlockContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#equationsBlock}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitEquationsBlock(PyNestMLParser.EquationsBlockContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#inputBlock}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitInputBlock(PyNestMLParser.InputBlockContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#inputLine}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitInputLine(PyNestMLParser.InputLineContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#inputType}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitInputType(PyNestMLParser.InputTypeContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#outputBlock}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitOutputBlock(PyNestMLParser.OutputBlockContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#function}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFunction(PyNestMLParser.FunctionContext ctx);
	/**
	 * Visit a parse tree produced by {@link PyNestMLParser#parameter}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitParameter(PyNestMLParser.ParameterContext ctx);
}