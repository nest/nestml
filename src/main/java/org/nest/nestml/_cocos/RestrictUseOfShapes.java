package org.nest.nestml._cocos;

import de.monticore.ast.ASTNode;
import de.monticore.symboltable.Scope;
import org.nest.nestml._ast.*;
import org.nest.nestml._symboltable.predefined.PredefinedFunctions;
import org.nest.nestml._symboltable.symbols.VariableSymbol;
import org.nest.nestml._visitor.NESTMLVisitor;
import org.nest.utils.AstUtils;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import static de.se_rwth.commons.logging.Log.error;

/**
 * Forbids the usage of the functional shapes everywhere but in the convolve-call.
 * @author traeder, plotnikov
 */
public class RestrictUseOfShapes implements NESTMLASTNeuronCoCo {

  @Override
  public void check(final ASTNeuron node) {

    ShapeCollectingVisitor shapeCollectingVisitor = new ShapeCollectingVisitor();
    List<String> shapeNames = shapeCollectingVisitor.collectShapes(node);

    ShapeUsageVisitor shapeUsageVisitor = new ShapeUsageVisitor(shapeNames);
    shapeUsageVisitor.workOn(node);

  }

  public class ShapeCollectingVisitor implements NESTMLVisitor {

    private List<String> shapeNames = new ArrayList<>();

    List<String> collectShapes(ASTNeuron node) {
      node.accept(this);
      return shapeNames;
    }

    @Override
    public void visit(ASTShape node) {
      ASTDerivative shapeVar = node.getLhs();
      shapeNames.add(shapeVar.getName());
    }

  }

  class ShapeUsageVisitor implements NESTMLVisitor {

    private List<String> shapes;
    private ASTNeuron neuronNode;

    ShapeUsageVisitor(List<String> shapes) {
      this.shapes = shapes;
    }

    void workOn(ASTNeuron node) {
      neuronNode = node;
      node.accept(this);
    }

    public void visit(ASTVariable astVariable){
      for(String shapeName: shapes){
        if(astVariable.getName().equals(shapeName)){
          Optional<ASTNode> parent = AstUtils.getParent(astVariable,neuronNode);
          if(parent.isPresent()){
            //Dont mind its own declaration
            if(parent.get() instanceof ASTShape){
              continue;
            }
            //We have to dig deeper for funcitonCalls:
            Optional<ASTNode> grandparent = AstUtils.getParent(parent.get(),neuronNode);
            if(grandparent.isPresent() &&
                grandparent.get() instanceof ASTFunctionCall){
              ASTFunctionCall grandparentCall = (ASTFunctionCall) grandparent.get();
              if(grandparentCall.getCalleeName().equals(PredefinedFunctions.CONVOLVE)){
                continue;
              }

            }
            final String errorMsg = NestmlErrorStrings.message(RestrictUseOfShapes.this);

            error(errorMsg, astVariable.get_SourcePositionStart());
          }

        }

      }

    }

    @Override
    public void visit(final ASTEquation astEquation) {
      final Scope scope = astEquation.getEnclosingScope().get();

      final Optional<VariableSymbol> shapeVariable = scope.resolve(
          astEquation.getLhs().getNameOfDerivedVariable(),
          VariableSymbol.KIND);
      if (shapeVariable.isPresent() &&
          shapeVariable.get().isFunctionalShape() &&
          shapes.contains(shapeVariable.get().getName())) {
        final String errorMsg = NestmlErrorStrings.message(RestrictUseOfShapes.this);
        error(errorMsg, astEquation.get_SourcePositionStart());
      }

    }

  }

}
