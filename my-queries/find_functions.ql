import cpp
import semmle.code.cpp.dataflow.new.DataFlow

/**
 * @name Potential memory leaks in libpng functions
 * @description Finds functions in libpng with allocations not freed.
 * @kind problem
 * @problem.severity warning
 * @id cpp/libpng/memory-leak-in-function
 */

class AllocCall extends FunctionCall {
  AllocCall() {
    this.getTarget().getName() = "malloc" or
    this.getTarget().getName() = "calloc" or
    this.getTarget().getName() = "realloc" or
    this.getTarget().getName() = "png_malloc"
  }
}

class FreeCall extends FunctionCall {
  FreeCall() {
    this.getTarget().getName() = "free" or
    this.getTarget().getName() = "png_free"
  }
}

from Function f, AllocCall alloc
where
  alloc.getEnclosingFunction() = f and
  alloc.getFile().getBaseName().matches("%png%") and
  not exists(FreeCall free |
    free.getEnclosingFunction() = f and
    free.getAnArgument() = alloc
  )
select alloc, 
  "Potential memory leak in function '" + f.getName() + "': allocation at line " + alloc.getLocation().getStartLine().toString() + " is not freed"