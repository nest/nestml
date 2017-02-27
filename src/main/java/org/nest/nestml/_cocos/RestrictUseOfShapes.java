package org.nest.nestml._cocos;

import de.monticore.ast.ASTNode;
import org.nest.commons._ast.ASTFunctionCall;
import org.nest.commons._ast.ASTVariable;
import org.nest.nestml._ast.ASTNeuron;
import org.nest.nestml._visitor.NESTMLVisitor;
import org.nest.ode._ast.ASTDerivative;
import org.nest.ode._ast.ASTShape;
import org.nest.utils.AstUtils;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import static de.se_rwth.commons.logging.Log.error;

/**
 * @author  traeder
 */
public class RestrictUseOfShapes implements NESTMLASTNeuronCoCo {
  public static final String ERROR_CODE = "NESTML_RESTRICT_USE_OF_SHAPES";

  public class ShapeCollectingVisitor implements NESTMLVisitor {

    private List<String> shapeNames = new ArrayList<>();

    public List<String> collectShapes(ASTNeuron node){
      node.accept(this);
      return shapeNames;
    }

    @Override public void visit(ASTShape node) {
      ASTVariable shapeVar = node.getLhs();
      shapeNames.add(shapeVar.getName().toString());
    }
  }

  class ShapeUsageVisitor implements NESTMLVisitor{

    private List<String> shapes;
    private ASTNeuron neuronNode;

    public ShapeUsageVisitor(List<String> shapes){
      this.shapes = shapes;
    }

    public void workOn(ASTNeuron node){
      neuronNode = node;
      node.accept(this);
    }

    public void visit(ASTVariable node){
      for(String shapeName: shapes){
        if(node.getName().toString().equals(shapeName)){
          Optional<ASTNode> parent = AstUtils.getParent(node,neuronNode);
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
              if(grandparentCall.getCalleeName().equals("curr_sum")||
                  grandparentCall.getCalleeName().equals("cond_sum")){
                continue;
              }
            }
          }
          final String errorMsg = ERROR_CODE+ " " + AstUtils.print(node.get_SourcePositionStart()) + " : " +
              "Shapes may only be used as parameters to either 'curr_sum()' or 'cond_sum()'.";
          error(errorMsg,node.get_SourcePositionStart());
        }
      }
    }

    public void visit(ASTDerivative node){
      for(String shapeName: shapes){
        if(node.getName().toString().equals(shapeName)){
          final String errorMsg = ERROR_CODE+ " " + AstUtils.print(node.get_SourcePositionStart()) + " : " +
              "Shapes may only be used as parameters to either 'curr_sum()' or 'cond_sum()'.";
          error(errorMsg,node.get_SourcePositionStart());
        }
      }
    }
  }

  @Override
  public void check(ASTNeuron node) {

    ShapeCollectingVisitor shapeCollectingVisitor = new ShapeCollectingVisitor();
    List<String> shapeNames = shapeCollectingVisitor.collectShapes(node);

    ShapeUsageVisitor shapeUsageVisitor = new ShapeUsageVisitor(shapeNames);
    shapeUsageVisitor.workOn(node);

  }
}
