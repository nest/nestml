/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.symboltable.typechecking;

import java.util.Optional;

/**
 * This class is used to store
 *
 * @author plotnikov
 */
public class Either<A, B> {
  private Optional<A> value;
  private Optional<B> error;

  /**
   * Use static factory methods instead.

   */
  private Either(final Optional<A> value, final Optional<B> error) {
    this.value = value;
    this.error = error;
  }

  public static <LType, RType> Either<LType, RType> value(final LType left) {
    return new Either<>(Optional.of(left), Optional.empty());
  }

  public static <LType, RType> Either<LType, RType> error(final RType right) {
    return new Either<>(Optional.empty(), Optional.of(right));
  }

  public A getValue() {
    return value.get();
  }

  public B getError() {
    return error.get();
  }

  public boolean isValue() {
    return value.isPresent();
  }

  public boolean isError() {
    return error.isPresent();
  }

  public String toString()
  {
    return "(" + value + ", " + error + ")";
  }

}
