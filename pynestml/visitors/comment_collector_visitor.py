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
from pynestml.generated.PyNestMLParserVisitor import PyNestMLParserVisitor


class CommentCollectorVisitor(PyNestMLParserVisitor):
    """
    This visitor iterates over a given parse tree and inspects the corresponding stream of tokens in order
    to update all nodes by their corresponding tokens.
    Attributes:
        __tokens (list): A list of all tokens representing the model.
    """

    def __init__(self, tokens):
        self.__tokens = tokens

    def visitBlockWithVariables(self, ctx):
        return (get_comments(ctx, self.__tokens), get_pre_comment(ctx, self.__tokens),
                get_in_comments(ctx, self.__tokens), get_post_comments(ctx, self.__tokens))

    def visitBlock(self, ctx):
        return (get_comments(ctx, self.__tokens), get_pre_comment(ctx, self.__tokens),
                get_in_comments(ctx, self.__tokens), get_post_comments(ctx, self.__tokens))

    def visitNeuron(self, ctx):
        return (get_comments(ctx, self.__tokens), get_pre_comment(ctx, self.__tokens),
                get_in_comments(ctx, self.__tokens), get_post_comments(ctx, self.__tokens))

    def visitOdeEquation(self, ctx):
        return (get_comments(ctx, self.__tokens), get_pre_comment(ctx, self.__tokens),
                get_in_comments(ctx, self.__tokens), get_post_comments(ctx, self.__tokens))

    def visitInlineExpression(self, ctx):
        return (get_comments(ctx, self.__tokens), get_pre_comment(ctx, self.__tokens),
                get_in_comments(ctx, self.__tokens), get_post_comments(ctx, self.__tokens))

    def visitKernel(self, ctx):
        return (get_comments(ctx, self.__tokens), get_pre_comment(ctx, self.__tokens),
                get_in_comments(ctx, self.__tokens), get_post_comments(ctx, self.__tokens))

    def visitStmt(self, ctx):
        return (get_comments(ctx, self.__tokens), get_pre_comment(ctx, self.__tokens),
                get_in_comments(ctx, self.__tokens), get_post_comments(ctx, self.__tokens))

    def visitSmallStmt(self, ctx):
        return (get_comments(ctx, self.__tokens), get_pre_comment(ctx, self.__tokens),
                get_in_comments(ctx, self.__tokens), get_post_comments(ctx, self.__tokens))

    def visitCompoundStmt(self, ctx):
        return (get_comments(ctx, self.__tokens), get_pre_comment(ctx, self.__tokens),
                get_in_comments(ctx, self.__tokens), get_post_comments(ctx, self.__tokens))

    def visitInputPort(self, ctx):
        return (get_comments(ctx, self.__tokens), get_pre_comment(ctx, self.__tokens),
                get_in_comments(ctx, self.__tokens), get_post_comments(ctx, self.__tokens))

    def visitDeclaration(self, ctx):
        return (get_comments(ctx, self.__tokens), get_pre_comment(ctx, self.__tokens),
                get_in_comments(ctx, self.__tokens), get_post_comments(ctx, self.__tokens))

    def visitAssignment(self, ctx):
        return (get_comments(ctx, self.__tokens), get_pre_comment(ctx, self.__tokens),
                get_in_comments(ctx, self.__tokens), get_post_comments(ctx, self.__tokens))

    def visitUpdateBlock(self, ctx):
        return (get_comments(ctx, self.__tokens), get_pre_comment(ctx, self.__tokens),
                get_in_comments(ctx, self.__tokens), get_post_comments(ctx, self.__tokens))

    def visitEquationsBlock(self, ctx):
        return (get_comments(ctx, self.__tokens), get_pre_comment(ctx, self.__tokens),
                get_in_comments(ctx, self.__tokens), get_post_comments(ctx, self.__tokens))

    def visitInputBlock(self, ctx):
        return (get_comments(ctx, self.__tokens), get_pre_comment(ctx, self.__tokens),
                get_in_comments(ctx, self.__tokens), get_post_comments(ctx, self.__tokens))

    def visitOutputBlock(self, ctx):
        return (get_comments(ctx, self.__tokens), get_pre_comment(ctx, self.__tokens),
                get_in_comments(ctx, self.__tokens), get_post_comments(ctx, self.__tokens))

    def visitFunctionCall(self, ctx):
        return (get_comments(ctx, self.__tokens), get_pre_comment(ctx, self.__tokens),
                get_in_comments(ctx, self.__tokens), get_post_comments(ctx, self.__tokens))

    def visitFunction(self, ctx):
        return (get_comments(ctx, self.__tokens), get_pre_comment(ctx, self.__tokens),
                get_in_comments(ctx, self.__tokens), get_post_comments(ctx, self.__tokens))

    def visitForStmt(self, ctx):
        return (get_comments(ctx, self.__tokens), get_pre_comment(ctx, self.__tokens),
                get_in_comments(ctx, self.__tokens), get_post_comments(ctx, self.__tokens))

    def visitWhileStmt(self, ctx):
        return (get_comments(ctx, self.__tokens), get_pre_comment(ctx, self.__tokens),
                get_in_comments(ctx, self.__tokens), get_post_comments(ctx, self.__tokens))

    def visitIfClause(self, ctx):
        temp = list()
        temp.extend(get_pre_comment(ctx, self.__tokens))
        temp.append(get_in_comments(ctx, self.__tokens))
        # for if clauses no post comments are supported
        return (temp, get_pre_comment(ctx, self.__tokens),
                get_in_comments(ctx, self.__tokens), list())

    def visitElifClause(self, ctx):
        temp = get_in_comments(ctx, self.__tokens)
        if temp is None:
            temp = list()
        else:
            temp = list(temp)
        # for elif clauses, only in comments are supported
        return (temp, list(), get_in_comments(ctx, self.__tokens),
                list())

    def visitElseClause(self, ctx):
        temp = get_in_comments(ctx, self.__tokens)
        if temp is None:
            temp = list()
        else:
            temp = list(temp)
        return (temp, list(), get_in_comments(ctx, self.__tokens),
                get_post_comments(ctx, self.__tokens))


def get_comments(ctx, tokens):
    """
    Returns all previously, in-line and pos comments.
    :param ctx: a context
    :type ctx: ctx
    :param tokens: list of token objects
    :type tokens: list(Tokens)
    :return: a list of comments
    :rtype: list(str)
    """
    ret = list()
    pre_comments = get_pre_comment(ctx, tokens)
    in_comment = get_in_comments(ctx, tokens)
    post_comments = get_post_comments(ctx, tokens)
    if pre_comments is not None:
        ret.extend(pre_comments)
    if in_comment is not None:
        ret.append(in_comment)
    if post_comments is not None:
        ret.extend(post_comments)
    return ret


def get_pre_comment(ctx, tokens):
    """
    Returns the comment which has been stated before this element but also before the next previous token.
    :param ctx: a context
    :type ctx: ctx
    :param tokens: list of token objects
    :type tokens: list(Tokens)
    :return: the corresponding comment or None
    :rtype: str
    """
    # first find the position of this token in the stream
    comments = list()
    empty_before = __no_definitions_before(ctx, tokens)
    eol = False
    temp = None
    for possibleCommentToken in reversed(tokens[0:tokens.index(ctx.start)]):
        # if we hit a normal token (i.e. not whitespace, not newline and not token) then stop, since we reached
        # the next previous element, thus the next comments belong to this element
        if possibleCommentToken.channel == 0:
            break
        # if we have found a comment, put it on the "stack". we now have to check if there is an element defined
        # in the same line, since in this case, the comments does not belong to us
        if possibleCommentToken.channel == 2:
            # if it is something on the comment channel -> get it
            temp = replace_delimiters(possibleCommentToken.text)
            eol = False
        # skip whitespaces
        if possibleCommentToken.channel == 1:
            continue
        # if the previous token was an EOL and and this token is neither a white space nor a comment, thus
        # it is yet another newline,stop (two lines separate a two elements)
        elif eol and not empty_before:
            break
        # we have found a new line token. thus if we have stored a comment on the stack, its ok to store it in
        # our element, since it does not belong to a declaration in its line
        if possibleCommentToken.channel == 3:
            if temp is not None:
                comments.append(temp)
            eol = True
            continue
    # this last part is required in the case, that the very fist token is a comment
    if empty_before and temp is not None and temp not in comments:
        comments.append(temp)
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
        if token.channel == 0:
            return False
    return True


def get_in_comments(ctx, tokens):
    """
    Returns the sole comment if one is defined in the same line, e.g. function a mV = 10mV # comment
    :param ctx: a context
    :type ctx: ctx
    :param tokens: list of token objects
    :type tokens: list(Tokens)
    :return: a comment
    :rtype: str
    """
    for possibleComment in tokens[tokens.index(ctx.start):]:
        if possibleComment.channel == 2:
            return replace_delimiters(possibleComment.text)
        if possibleComment.channel == 3:  # channel 3 == new line, thus the one line comment ends here
            break
    return None


def get_post_comments(ctx, tokens):
    """
    Returns the comment which has been stated after the current token but in the same line.
    :param ctx: a context
    :type ctx: ctx
    :param tokens: list of token objects
    :type tokens: list(Tokens)
    :return: the corresponding comment or None
    :rtype: str
    """
    comments = list()
    next_line_start_index = -1
    # first find out where the next line start, since we want to avoid to see comments, which have
    # been stated in the same line, as comments which are stated after the element
    for possibleToken in tokens[tokens.index(ctx.stop) + 1:]:
        if possibleToken.channel == 3:
            next_line_start_index = tokens.index(possibleToken)
            break
    first_line = False
    for possibleCommentToken in tokens[next_line_start_index:]:
        if possibleCommentToken.channel == 2:
            # if it is a comment on the comment channel -> get it
            comments.append(replace_delimiters(possibleCommentToken.text))
            first_line = False

        # we found a white line, thus a comment separator
        if possibleCommentToken.channel == 3 and first_line:
            break
        elif possibleCommentToken.channel == 3:
            first_line = True

        # if we see a different element, i.e. that we have reached the next declaration and should stop
        if possibleCommentToken.channel == 0:
            break

    return comments if len(comments) > 0 else list()


def replace_delimiters(comment):
    # type: (str) -> str
    """
    Returns the raw comment, i.e., without the comment-tags /* ..*/, \""" ""\" and #
    """
    ret = comment
    ret = ret.replace('/*', '').replace('*/', '')
    ret = ret.replace('"""', '')
    return ret.replace('#', '')
