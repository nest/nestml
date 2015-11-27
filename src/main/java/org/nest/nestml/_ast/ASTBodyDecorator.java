package org.nest.nestml._ast;

import com.google.common.collect.ImmutableList;
import org.nest.nestml._visitor.NESTMLInheritanceVisitor;
import org.nest.spl._ast.ASTOdeDeclaration;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static com.google.common.base.Preconditions.checkNotNull;
import static com.google.common.base.Preconditions.checkState;
import static java.util.stream.Collectors.toList;

/**
 * Provides convenient  functions to statically type interfaces astnodes resulting from the Body-grammar
 * production.
 *
 * @author (last commit) $Author$
 * @version $Revision$, $Date$
 */
public class ASTBodyDecorator extends ASTBody {

  public static final String MISSING_DYNAMICS_ERROR =
      "There is no dynamics in the NESTML model. This error should be catched by "
          + "the context conditions.lease check you tool configuration and enable context conditions.!";

  private final ASTBody body;

  public ASTBodyDecorator(ASTBody body) {
    checkNotNull(body);

    this.body = body;
  }

  public List<ASTFunction> getFunctions() {
    List<ASTFunction> result = body.getBodyElements().stream()
        .filter(be -> be instanceof ASTFunction)
        .map(be -> (ASTFunction) be)
        .collect(Collectors.toList());

    return ImmutableList.copyOf(result);
  }

  public List<ASTDynamics> getDynamics() {
    List<ASTDynamics> result = body.getBodyElements().stream()
        .filter(be -> be instanceof ASTDynamics)
        .map(be -> (ASTDynamics) be)
        .collect(Collectors.toList());

    return ImmutableList.copyOf(result);
  }

  public Optional<ASTBodyElement> getStateBlock() {
    return body.getBodyElements().stream()
        .filter(be -> be instanceof ASTVar_Block && ((ASTVar_Block) be).isState())
        .findFirst();
  }

  public Optional<ASTBodyElement> getParameterBlock() {
    return body.getBodyElements().stream()
        .filter(be -> be instanceof ASTVar_Block && ((ASTVar_Block) be).isParameter())
        .findFirst();
  }

  public List<ASTAliasDecl> getStates() {
    List<ASTAliasDecl> result = new ArrayList<ASTAliasDecl>();

    body.getBodyElements().stream().filter(be -> be instanceof ASTVar_Block).forEach(be -> {
      ASTVar_Block block = (ASTVar_Block) be;
      if (block.isState()) {
        for (ASTAliasDecl ad : block.getAliasDecls()) {
          result.add(ad);
        }
      }
    });

    return ImmutableList.copyOf(result);
  }

  @SuppressWarnings("unused") // used in templates
  public List<ASTAliasDecl> getAliasStates() {
    return getStates().stream().filter(decl->decl.isAlias()).collect(toList());
  }

  @SuppressWarnings("unused") // used in templates
  public List<ASTAliasDecl> getNonAliasStates() {
    return getStates().stream().filter(v->!v.isAlias()).collect(toList());
  }

  public List<ASTAliasDecl> getParameters() {
    List<ASTAliasDecl> result = new ArrayList<ASTAliasDecl>();

    body.getBodyElements().stream().filter(be -> be instanceof ASTVar_Block).forEach(be -> {
      ASTVar_Block block = (ASTVar_Block) be;
      if (block.isParameter()) {
        result.addAll(block.getAliasDecls().stream().collect(Collectors.toList()));
      }
    });

    return ImmutableList.copyOf(result);
  }

  public List<ASTAliasDecl> getAliasParameters() {

    return getParameters().stream().filter(decl -> decl.isAlias()).collect(toList());
  }

  @SuppressWarnings("unused") // used in templates
  public List<ASTAliasDecl> getNonAliasParameters() {

    return getParameters().stream().filter(decl -> !decl.isAlias()).collect(toList());
  }

  public List<ASTAliasDecl> getInternals() {
    List<ASTAliasDecl> result = new ArrayList<ASTAliasDecl>();

    body.getBodyElements().stream().filter(be -> be instanceof ASTVar_Block).forEach(be -> {
      ASTVar_Block block = (ASTVar_Block) be;

      if (block.isInternal()) {
        for (ASTAliasDecl ad : block.getAliasDecls()) {
          result.add(ad);
        }
      }
    });

    return ImmutableList.copyOf(result);
  }

  public void addToInternalBlock(final ASTAliasDecl astAliasDecl) {
    body.getBodyElements().stream().filter(variableBlock -> variableBlock instanceof ASTVar_Block).forEach(be -> {

      ASTVar_Block block = (ASTVar_Block) be;

      if (block.isInternal()) {
        block.getAliasDecls().add(astAliasDecl);
      }

    });

  }

  public void addToStateBlock(final ASTAliasDecl astAliasDecl) {
    body.getBodyElements().stream().filter(variableBlock -> variableBlock instanceof ASTVar_Block).forEach(be -> {

      ASTVar_Block block = (ASTVar_Block) be;

      if (block.isState()) {
        block.getAliasDecls().add(astAliasDecl);
      }

    });

  }
  private static class OdeDefinitionCollector implements NESTMLInheritanceVisitor {

    private Optional<ASTOdeDeclaration> astOdeDeclaration = Optional.empty();

    @Override
    public void visit(final ASTOdeDeclaration astOdeDeclarationNode) {
      this.astOdeDeclaration = Optional.of(astOdeDeclarationNode);
    }

    public Optional<ASTOdeDeclaration> collect(final ASTNESTMLNode astNestmlBase) {
      astNestmlBase.accept(this);
      return astOdeDeclaration;
    }

    public Optional<ASTOdeDeclaration> getAstOdeDeclaration() {
      return astOdeDeclaration;
    }

  }

  /**
   * TODO rework: ODE is not a body element
   * @return
   */
  public Optional<ASTOdeDeclaration> getOdeDefinition() {
    // It is ensured through cocos that there is exactly one dynamics
    final Optional<ASTBodyElement> astDynamics = findDynamics();
    checkState(astDynamics.isPresent(), MISSING_DYNAMICS_ERROR);

    final OdeDefinitionCollector odeDefinitionCollector = new OdeDefinitionCollector();
    Optional<ASTOdeDeclaration> foundOdeDeclaration = odeDefinitionCollector.collect(astDynamics.get());

    return foundOdeDeclaration;
  }

  private Optional<ASTBodyElement> findDynamics() {
    return body.getBodyElements().stream()
          .filter(be -> be instanceof ASTDynamics)
          .findFirst();
  }

  @SuppressWarnings("unchecked")
  public List<ASTAliasDecl> getAliasInternals() {
    return getInternals().stream().filter(decl -> decl.isAlias()).collect(toList());
  }

  @SuppressWarnings("unchecked")
  public List<ASTAliasDecl> getNonAliasInternals() {

    return getInternals().stream().filter(decl -> !decl.isAlias()).collect(toList());
  }

  public List<ASTUSE_Stmt> getUses() {
    List<ASTUSE_Stmt> result = body.getBodyElements().stream()
        .filter(be -> be instanceof ASTUSE_Stmt)
        .map(be -> (ASTUSE_Stmt) be)
        .collect(Collectors.toList());

    return ImmutableList.copyOf(result);
  }

  public List<ASTInputLine> getInputLines() {
    List<ASTInputLine> result = new ArrayList<ASTInputLine>();

    for (ASTBodyElement be : body.getBodyElements()) {
      if (be instanceof ASTInput) {
        ASTInput in = (ASTInput) be;
        for (ASTInputLine inline : in.getInputLines()) {
          result.add(inline);
        }
      }
    }

    return ImmutableList.copyOf(result);
  }

  public List<ASTOutput> getOutputs() {
    List<ASTOutput> result = body.getBodyElements().stream()
        .filter(be -> be instanceof ASTOutput)
        .map(be -> (ASTOutput) be)
        .collect(Collectors.toList());

    return ImmutableList.copyOf(result);
  }

  public List<ASTStructureLine> getStructure() {
    List<ASTStructureLine> result = new ArrayList<ASTStructureLine>();

    for (ASTBodyElement be : body.getBodyElements()) {
      if (be instanceof ASTStructure) {
        ASTStructure st = (ASTStructure) be;
        for (ASTStructureLine stline : st.getStructureLines()) {
          result.add(stline);
        }
      }
    }

    return ImmutableList.copyOf(result);
  }
}
