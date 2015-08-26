package org.nest.nestml.cocos;


import com.google.common.base.Preconditions;
import com.google.common.collect.Lists;
import de.monticore.cocos.CoCoLog;
import de.monticore.symboltable.Scope;
import de.se_rwth.commons.Names;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.ASTNESTMLCompilationUnit;
import org.nest.nestml._cocos.NESTMLASTAliasDeclCoCo;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.symboltable.symbols.NESTMLMethodSymbol;
import org.nest.symboltable.symbols.NESTMLTypeSymbol;
import org.nest.utils.NESTMLSymbols;

import java.util.Optional;

public class AliasHasNoSetter implements NESTMLASTAliasDeclCoCo {


  public static final String ERROR_CODE = "NESTML_ALIAS_HAS_NO_SETTER";
    private final ASTNESTMLCompilationUnit astNestmlCompilationUnit;


    public AliasHasNoSetter(final ASTNESTMLCompilationUnit astNestmlCompilationUnit) {
      this.astNestmlCompilationUnit = astNestmlCompilationUnit;
  }


  @Override
  public void check(ASTAliasDecl alias) {
    if (alias.isAlias() && alias.getDeclaration() != null) {

      final ASTDeclaration decl = alias.getDeclaration();
      final Optional<? extends Scope> scope = decl.getEnclosingScope();
      Preconditions.checkState(scope.isPresent(), "No scope is assigned to the node: " + decl);

      if (decl.getVars().size() == 1) {
        String aliasVar = decl.getVars().get(0);

        // TODO
        //ASTParameter para = NESTMLNodeFactory.createASTParameter(
        //        "v", LiteralsNodeFactory.createASTDottedName(decl
        //                .getType().getNames()));
        String varTypeName = Names.getQualifiedName(decl.getType().get().getParts());


        final Optional<? extends Scope> enclosingScope = decl.getEnclosingScope();

        Preconditions.checkState(enclosingScope.isPresent(), "No scope assigned to the node: " + decl);
        final String setterName = "set_" + aliasVar;

        Optional<NESTMLMethodSymbol> setter = NESTMLSymbols.resolveMethod(enclosingScope.get(), setterName, Lists.newArrayList(varTypeName));

        if (!setter.isPresent()) {
          final String msg = "Alias-variable '" + aliasVar
                  + "' needs a setter-function: set_" + aliasVar
                  + "(v " + decl.getType().get().toString() + ")";

          CoCoLog.error(ERROR_CODE,
              msg,
              alias.get_SourcePositionStart());
        }
        else {

          if (setter.get().getParameterTypes().size() == 1) {
            NESTMLTypeSymbol setterType = setter.get().getParameterTypes().get(0);

            if (!setterType.getName().endsWith(decl.getType().get().toString())) {
              final String msg = "Alias-variable '" + aliasVar
                      + "' needs a setter-function: set_" + aliasVar
                      + "(v " + decl.getType().get().toString() + ")";

              CoCoLog.error(ERROR_CODE,
                  msg,
                  alias.get_SourcePositionStart());
            }
          }
          else {
            // TODO check it
            final String msg = "Alias-variable '" + aliasVar
                    + "' needs a setter-function: set_" + aliasVar
                    + "(v " + decl.getType().get().toString() + ")";
            CoCoLog.error(ERROR_CODE,
                msg,
                alias.get_SourcePositionStart());

          }

        }

      }

    }

  }

}
