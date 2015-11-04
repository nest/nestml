package org.nest.codegeneration.sympy;

import de.monticore.types.types._ast.TypesNodeFactory;
import org.nest.nestml._ast.ASTAliasDecl;
import org.nest.nestml._ast.NESTMLNodeFactory;
import org.nest.nestml._parser.DeclarationMCParser;
import org.nest.nestml._parser.ExprMCParser;
import org.nest.nestml._parser.NESTMLParserFactory;
import org.nest.spl._ast.ASTDeclaration;
import org.nest.spl._ast.ASTExpr;
import org.nest.spl._ast.SPLNodeFactory;

import java.io.File;
import java.io.IOException;
import java.io.StringReader;
import java.nio.file.Files;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Created by user on 20.05.15.
 */
public class Sympy2NESTMLConverter {

  private final SympyLine2ASTConverter line2ASTConverter;

  final DeclarationMCParser declarationParser = NESTMLParserFactory.createDeclarationMCParser();

  public Sympy2NESTMLConverter() {
    this.line2ASTConverter = new SympyLine2ASTConverter();
  }

  public List<ASTAliasDecl> convertMatrixFile2NESTML(final String filename) {
    final List<String> linesAsStrings = readMatrixElementsFromFile(filename);
    final List<ASTDeclaration> propagationElements
        = linesAsStrings.stream().map(line2ASTConverter::convert).collect(Collectors.toList());

    return propagationElements.stream().map(this::convertToAlias).collect(Collectors.toList());
  }

/*  public List<ASTAliasDecl> createDeclarationASTs(final String filename) {
    final List<String> linesAsStrings = readMatrixElementsFromFile(filename);
    final List<ASTDeclaration> propagationElements
        = linesAsStrings.stream().map(this::convert).collect(Collectors.toList());

    return propagationElements.stream().map(this::convertToAlias).collect(Collectors.toList());
  }*/

  private ASTAliasDecl convertToAlias(ASTDeclaration astDeclaration) {
    final ASTAliasDecl astAliasDecl = NESTMLNodeFactory.createASTAliasDecl();

    astAliasDecl.setDeclaration(astDeclaration);
    astAliasDecl.setAlias(false);
    astAliasDecl.setHide(false);
    astAliasDecl.setInvariants(SPLNodeFactory.createASTExprList());

    return astAliasDecl;
  }

  public ASTAliasDecl convertDeclaration(String p00File) {
    try {
      final ASTDeclaration declaration = declarationParser.parse(p00File).get();
      // it is ok to call get, since otherwise it is an error in the file structure
      return convertToAlias(declaration);
    }
    catch (IOException e) {
      final String msg = "Cannot parse P00 value from the SymPy analysis script.";
      throw new RuntimeException(msg, e);
    }

  }


  public List<String> readMatrixElementsFromFile(final String filename) {
    List<String> matrixElements;
    try {
      matrixElements = Files.lines(new File(filename).toPath())
          .filter(line -> !line.isEmpty())
          .collect(Collectors.toList());
      return matrixElements;
    }
    catch (IOException e) {
      throw new RuntimeException("Cannot find or read the file with propagator matrix.", e);
    }

  }
}
