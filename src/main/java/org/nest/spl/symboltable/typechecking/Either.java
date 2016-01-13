/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.spl.symboltable.typechecking;

import java.util.Optional;

/**
 * This class is used to store
 *
 * @author plotnikov
 */
public class Either<A, B> {
  private Optional<A> left;
  private Optional<B> right;

  /**
   * Use static factory methods instead.

   */
  private Either(final Optional<A> left, final Optional<B> right) {
    this.left = left;
    this.right = right;
  }

  public static <LType, RType> Either<LType, RType> left(final LType left) {
    return new Either<>(Optional.of(left), Optional.empty());
  }

  public static <LType, RType> Either<LType, RType> right(final RType right) {
    return new Either<>(Optional.empty(), Optional.of(right));
  }

  public Optional<A> getLeft() {
    return left;
  }

  public Optional<B> getRight() {
    return right;
  }

  public boolean isLeft() {
    return left.isPresent();
  }

  public boolean isRight() {
    return right.isPresent();
  }

  public String toString()
  {
    return "(" + left + ", " + right + ")";
  }

}
