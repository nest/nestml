<#--
  Generates C++ declaration
  @grammar: AliasDecl = ([hide:"-"])? ([alias:"alias"])?
                        Declaration ("[" invariants:Expr (";" invariants:Expr)* "]")?;
                        Declaration = vars:Name ("," vars:Name)* (type:QualifiedName | primitiveType:PrimitiveType) ( "=" Expr )? ;
  @param ast ASTAliasDecl
  @param tc templatecontroller
  @result TODO
-->
${signature("var")}

<#assign varDomain = declarations.getDomainFromType(var.getType())>

<#if varDomain == "nest::double_t" && var.isLoggable()>
insert_("${var.getName()}", &${simpleNeuronName}::get_${var.getName()});
<#else>
// ignores the ${var.getName()} with the domain type ${varDomain}
</#if>
