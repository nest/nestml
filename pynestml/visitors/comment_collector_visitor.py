# -*- coding: utf-8 -*-
#
# comment_collector_visitor.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

from typing import List, Optional

from pynestml.generated.PyNestMLParserVisitor import PyNestMLParserVisitor


class CommentCollectorVisitor(PyNestMLParserVisitor):
    """
    This visitor iterates over a given parse tree and inspects the corresponding stream of tokens in order
    to update all nodes by their corresponding tokens.
    Attributes:
    """

    def __init__(self, tokens, strip_delim: bool = True):
        """
        Parameters
        ----------
        tokens
            A list of all tokens representing the model.
        strip_delim
            Whether to strip the comment delimiters (``#`` and ``\"\"\"``...``\"\"\"``).
        """

        self.__tokens = tokens
        self.__strip_delim = strip_delim

    def visitBlockWithVariables(self, ctx):
        return (get_comments(ctx, self.__tokens, self.__strip_delim), get_pre_comments(ctx, self.__tokens, self.__strip_delim),
                get_in_comment(ctx, self.__tokens, self.__strip_delim))

    def visitBlock(self, ctx):
        return (get_comments(ctx, self.__tokens, self.__strip_delim), get_pre_comments(ctx, self.__tokens, self.__strip_delim),
                get_in_comment(ctx, self.__tokens, self.__strip_delim))

    def visitNeuron(self, ctx):
        return (get_comments(ctx, self.__tokens, self.__strip_delim), get_pre_comments(ctx, self.__tokens, self.__strip_delim),
                get_in_comment(ctx, self.__tokens, self.__strip_delim))

    def visitSynapse(self, ctx):
        return (get_comments(ctx, self.__tokens), get_pre_comments(ctx, self.__tokens),
                get_in_comment(ctx, self.__tokens))

    def visitOdeEquation(self, ctx):
        return (get_comments(ctx, self.__tokens, self.__strip_delim), get_pre_comments(ctx, self.__tokens, self.__strip_delim),
                get_in_comment(ctx, self.__tokens, self.__strip_delim))

    def visitInlineExpression(self, ctx):
        return (get_comments(ctx, self.__tokens, self.__strip_delim), get_pre_comments(ctx, self.__tokens, self.__strip_delim),
                get_in_comment(ctx, self.__tokens, self.__strip_delim))

    def visitKernel(self, ctx):
        return (get_comments(ctx, self.__tokens, self.__strip_delim), get_pre_comments(ctx, self.__tokens, self.__strip_delim),
                get_in_comment(ctx, self.__tokens, self.__strip_delim))

    def visitStmt(self, ctx):
        return (get_comments(ctx, self.__tokens, self.__strip_delim), get_pre_comments(ctx, self.__tokens, self.__strip_delim),
                get_in_comment(ctx, self.__tokens, self.__strip_delim))

    def visitSmallStmt(self, ctx):
        return (get_comments(ctx, self.__tokens, self.__strip_delim), get_pre_comments(ctx, self.__tokens, self.__strip_delim),
                get_in_comment(ctx, self.__tokens, self.__strip_delim))

    def visitCompoundStmt(self, ctx):
        return (get_comments(ctx, self.__tokens, self.__strip_delim), get_pre_comments(ctx, self.__tokens, self.__strip_delim),
                get_in_comment(ctx, self.__tokens, self.__strip_delim))

    def visitSpikeInputPort(self, ctx):
        return (get_comments(ctx, self.__tokens, self.__strip_delim), get_pre_comments(ctx, self.__tokens, self.__strip_delim),
                get_in_comment(ctx, self.__tokens, self.__strip_delim))

    def visitContinuousInputPort(self, ctx):
        return (get_comments(ctx, self.__tokens, self.__strip_delim), get_pre_comments(ctx, self.__tokens, self.__strip_delim),
                get_in_comment(ctx, self.__tokens, self.__strip_delim))

    def visitDeclaration(self, ctx):
        return (get_comments(ctx, self.__tokens, self.__strip_delim), get_pre_comments(ctx, self.__tokens, self.__strip_delim),
                get_in_comment(ctx, self.__tokens, self.__strip_delim))

    def visitAssignment(self, ctx):
        return (get_comments(ctx, self.__tokens, self.__strip_delim), get_pre_comments(ctx, self.__tokens, self.__strip_delim),
                get_in_comment(ctx, self.__tokens, self.__strip_delim))

    def visitUpdateBlock(self, ctx):
        return (get_comments(ctx, self.__tokens, self.__strip_delim), get_pre_comments(ctx, self.__tokens, self.__strip_delim),
                get_in_comment(ctx, self.__tokens, self.__strip_delim))

    def visitOnReceiveBlock(self, ctx):
        return (get_comments(ctx, self.__tokens), get_pre_comments(ctx, self.__tokens),
                get_in_comment(ctx, self.__tokens))

    def visitEquationsBlock(self, ctx):
        return (get_comments(ctx, self.__tokens, self.__strip_delim), get_pre_comments(ctx, self.__tokens, self.__strip_delim),
                get_in_comment(ctx, self.__tokens, self.__strip_delim))

    def visitInputBlock(self, ctx):
        return (get_comments(ctx, self.__tokens, self.__strip_delim), get_pre_comments(ctx, self.__tokens, self.__strip_delim),
                get_in_comment(ctx, self.__tokens, self.__strip_delim))

    def visitOutputBlock(self, ctx):
        return (get_comments(ctx, self.__tokens, self.__strip_delim), get_pre_comments(ctx, self.__tokens, self.__strip_delim),
                get_in_comment(ctx, self.__tokens, self.__strip_delim))

    def visitFunctionCall(self, ctx):
        return (get_comments(ctx, self.__tokens, self.__strip_delim), get_pre_comments(ctx, self.__tokens, self.__strip_delim),
                get_in_comment(ctx, self.__tokens, self.__strip_delim))

    def visitFunction(self, ctx):
        return (get_comments(ctx, self.__tokens, self.__strip_delim), get_pre_comments(ctx, self.__tokens, self.__strip_delim),
                get_in_comment(ctx, self.__tokens, self.__strip_delim))

    def visitForStmt(self, ctx):
        return (get_comments(ctx, self.__tokens, self.__strip_delim), get_pre_comments(ctx, self.__tokens, self.__strip_delim),
                get_in_comment(ctx, self.__tokens, self.__strip_delim))

    def visitWhileStmt(self, ctx):
        return (get_comments(ctx, self.__tokens, self.__strip_delim), get_pre_comments(ctx, self.__tokens, self.__strip_delim),
                get_in_comment(ctx, self.__tokens, self.__strip_delim))

    def visitIfClause(self, ctx):
        temp = list()
        temp.extend(get_pre_comments(ctx, self.__tokens, self.__strip_delim))
        temp.append(get_in_comment(ctx, self.__tokens, self.__strip_delim))
        return (temp, get_pre_comments(ctx, self.__tokens, self.__strip_delim),
                get_in_comment(ctx, self.__tokens, self.__strip_delim), list())

    def visitElifClause(self, ctx):
        temp = get_in_comment(ctx, self.__tokens, self.__strip_delim)
        if temp is None:
            temp = list()
        else:
            temp = list(temp)
        # for elif clauses, only in comments are supported
        return (temp, list(), get_in_comment(ctx, self.__tokens, self.__strip_delim),
                list())

    def visitElseClause(self, ctx):
        temp = get_in_comment(ctx, self.__tokens, self.__strip_delim)
        if temp is None:
            temp = list()
        else:
            temp = list(temp)
        return temp, list(), get_in_comment(ctx, self.__tokens, self.__strip_delim)


def is_newline(tok):
    return tok.type == 9  # NEWLINE token


def is_indent(tok):
    return tok.type == 1  # INDENT token


def is_dedent(tok):
    return tok.type == 2  # DEDENT token


def get_comments(ctx, tokens, strip_delim: bool = True) -> List[str]:
    """
    Returns all pre- and inline comments.
    :param ctx: a context
    :type ctx: ctx
    :param tokens: list of token objects
    :type tokens: list(Tokens)
    :return: a list of comments
    """
    ret = list()
    pre_comments = get_pre_comments(ctx, tokens, strip_delim=strip_delim)
    in_comment = get_in_comment(ctx, tokens, strip_delim=strip_delim)
    if pre_comments is not None:
        ret.extend(pre_comments)
    if in_comment is not None:
        ret.append(in_comment)
    return ret


def get_pre_comments(ctx, tokens, strip_delim: bool = True) -> List[str]:
    """
    Returns the comment which has been started before this element but also before the next previous token.
    :param ctx: a context
    :type ctx: ctx
    :param tokens: list of token objects
    :type tokens: list(Tokens)
    :return: the corresponding comments
    """
    # first find the position of this token in the stream
    comments = list()
    empty_before = __no_definitions_before(ctx, tokens)
    temp = None
    lastToken = None
    for possibleCommentToken in reversed(tokens[0:tokens.index(ctx.start)]):
        # if we hit a normal token (i.e. not whitespace and not newline) then stop
        if possibleCommentToken.channel == 0 \
                and not (is_newline(possibleCommentToken)
                         or is_indent(possibleCommentToken) or is_dedent(possibleCommentToken)):
            # This is to omit the inline comments that are parsed
            if is_newline(lastToken) and temp is not None:
                comments.append(temp)
            break

        # a newline on comment channel (2) by itself separates elements
        if possibleCommentToken.channel == 2 and is_newline(possibleCommentToken) and is_newline(lastToken):
            if temp is not None:
                comments.append(temp)
            break

        # if we have found a comment, put it on the "stack". we now have to check if there is an element defined
        # in the same line, since in this case, the comments does not belong to us
        if possibleCommentToken.channel == 2 and not is_newline(possibleCommentToken):
            if temp is not None:
                comments.append(temp)
            if strip_delim:
                temp = replace_delimiters(possibleCommentToken.text)
            else:
                temp = possibleCommentToken.text
        lastToken = possibleCommentToken

    # this last part is required in the case, that the very first token is a comment
    if empty_before and temp is not None and temp not in comments:
        comments.append(temp)
    # strip leading newlines -- this removes the newline after an opening ``"""`` if present
    for i, comment in enumerate(comments):
        if len(comment) > 0 and comment[0] == '\n':
            comments[i] = comment[1:]
        if len(comment) > 1 and comment[0] == '\r' and comment[1] == '\n':
            comments[i] = comment[2:]
    # strip trailing newlines
    for i, comment in enumerate(comments):
        if len(comment) > 0 and comment[-1] == '\n':
            comments[i] = comment[:-1]
        if len(comment) > 1 and comment[-1] == '\n' and comment[-2] == '\r':
            comments[i] = comment[:-2]
    # we reverse it in order to get the right order of comments
    return list(reversed(comments)) if len(comments) > 0 else list()


def __no_definitions_before(ctx, tokens):
    """
    This method indicates whether before the start of ctx, something has been defined, e.g. a different neuron.
    This method is used to identify the start of a model.
    :param ctx: a context
    :type ctx: ctx
    :param tokens: list of token objects
    :type tokens: list(Tokens)
    :return: True if nothing defined before, otherwise False.
    :rtype: bool
    """
    for token in tokens[0:tokens.index(ctx.start)]:
        if token.channel == 0 and not is_newline(token) and not is_indent(token):
            return False
    return True


def get_in_comment(ctx, tokens, strip_delim: bool = True) -> Optional[str]:
    """
    Returns the sole comment if one is defined in the same line, e.g. ``a = 10 mV # comment``
    :param ctx: a context
    :type ctx: ctx
    :param tokens: list of token objects
    :type tokens: list(Tokens)
    :return: a comment
    """
    prevToken = None
    for possibleComment in tokens[tokens.index(ctx.start):]:
        if possibleComment.channel == 2:
            if is_newline(possibleComment):  # new line, thus the one line comment ends here
                break
            if strip_delim:
                comment = replace_delimiters(possibleComment.text)
            else:
                comment = possibleComment.text
            if len(comment) > 0 and comment[-1] == '\n':
                comment = comment[:-1]
            if len(comment) > 1 and comment[-1] == '\n' and comment[-2] == '\r':
                comment = comment[:-2]
            return comment
        # While parsing blocks separately, there can be cases where the ctx.start (possibleComment) can begin with a new line.
        # In this case, the parsing should not be stopped. Hence, prevToken checks if possibleComment is the first new line.
        if possibleComment.channel == 0 and prevToken is not None and is_newline(possibleComment):
            break
        prevToken = possibleComment
    return None


def replace_delimiters(comment: str) -> str:
    """
    Returns the raw comment, i.e., without the comment delimiters (``#`` or ``\"\"\"``...``\"\"\"``).
    """
    if len(comment) > 2 and comment[:2] == "\"\"\"":
        # it's a docstring comment
        return comment.replace("\"\"\"", "")
    # it's a hash comment
    if len(comment) > 0 and comment[0] == "#":
        # strip initial character hash
        comment = comment[1:]
    return comment.replace('\n#', '').replace('\r\n#', '')
