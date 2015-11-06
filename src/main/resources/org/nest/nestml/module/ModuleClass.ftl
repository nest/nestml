<#assign lowerModuleName = moduleName?lower_case>
<#assign upperModuleName = moduleName?upper_case>
/*
 *  ${moduleName}.cpp
 *
 *  This file is part of NEST.
 *
 *  Copyright (C) 2004 The NEST Initiative
 *
 *  NEST is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  NEST is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

// include necessary NEST headers
#include "config.h"
#include "network.h"
#include "model.h"
#include "dynamicloader.h"
#include "genericmodel.h"
#include "booldatum.h"
#include "integerdatum.h"
#include "tokenarray.h"
#include "exceptions.h"
#include "sliexceptions.h"
#include "nestmodule.h"
#include "connector_model_impl.h"
#include "target_identifier.h"

// include headers with your own stuff
#include "${moduleName}Config.h"

<#list neuronModelNames as name>
  #include "${name}.h"
</#list>
// -- Interface to dynamic module loader ---------------------------------------

/*
 * The dynamic module loader must be able to find your module.
 * You make the module known to the loader by defining an instance of your
 * module class in global scope. This instance must have the name
 *
 * <modulename>_LTX_mod
 *
 * The dynamicloader can then load modulename and search for symbol "mod" in it.
 */

${lowerModuleName}::${moduleName} ${lowerModuleName}_LTX_mod;

// -- DynModule functions ------------------------------------------------------

${lowerModuleName}::${moduleName}::${moduleName}()
{
#ifdef LINKED_MODULE
  // register this module at the dynamic loader
  // this is needed to allow for linking in this module at compile time
  // all registered modules will be initialized by the main app's dynamic loader
  nest::DynamicLoaderModule::registerLinkedModule( this );
#endif
}

${lowerModuleName}::${moduleName}::~${moduleName}()
{
}

const std::string
${lowerModuleName}::${moduleName}::name(void) const
{
  return std::string("${moduleName}"); // Return name of the module
}

const std::string
${lowerModuleName}::${moduleName}::commandstring( void ) const
{
  // Instruct the interpreter to load ${moduleName}-init.sli
  return std::string( "(${moduleName}-init) run" );
}

//-------------------------------------------------------------------------------------
void
${lowerModuleName}::${moduleName}::init( SLIInterpreter* i )
{<#list neuronModelNames as name>
  <#assign fqnName = packageName + "." + name>
  nest::register_model<${fqnName?replace(".", "::")}>(nest::NestModule::get_network(),
  "${fqnName?replace(".", "_")}");

  </#list>

} // ${moduleName}::init()