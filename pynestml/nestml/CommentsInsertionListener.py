#
# CommentsInsertionListener.py
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
from pynestml.generated.PyNESTMLListener import PyNESTMLListener


class CommentsInsertionListener(PyNESTMLListener):
    tokens = None

    def __init__(self, tokens):
        self.tokens = tokens

    def enterBlockWithVariables(self, ctx):
        ctx.comment = self.getComments(ctx)

    def enterBlock(self, ctx):
        ctx.comment = self.getComments(ctx)

    def enterNeuron(self, ctx):
        ctx.comment = self.getComments(ctx)

    def enterOdeEquation(self, ctx):
        ctx.comment = self.getComments(ctx)

    def enterOdeFunction(self, ctx):
        ctx.comment = self.getComments(ctx)

    def enterOdeShape(self, ctx):
        ctx.comment = self.getComments(ctx)

    def enterStmt(self, ctx):
        ctx.comment = self.getComments(ctx)

    def enterInputLine(self, ctx):
        ctx.comment = self.getComments(ctx)

    def enterDeclaration(self, ctx):
        ctx.comment = self.getComments(ctx)

    def enterAssignment(self, ctx):
        ctx.comment = self.getComments(ctx)

    def getComments(self, ctx):
        """
        Returns all previously, in-line and pos comments.
        :param ctx: a context
        :type ctx: ctx
        :return: a list of comments
        :rtype: list(str)
        """
        ret = list()
        preComments = self.getCommentStatedBefore(ctx)
        inComment = self.getCommentInLine(ctx)
        postComments = self.getCommentStatedAfter(ctx)
        if preComments is not None:
            ret.extend(preComments)
        if inComment is not None:
            ret.append(inComment)
        if postComments is not None:
            ret.extend(postComments)
        return ret

    def getCommentStatedBefore(self, ctx):
        """
        Returns the comment which has been stated before this element but also before the next previous token.
        :param ctx: a context
        :type ctx: ctx
        :return: the corresponding comment or None
        :rtype: str
        """
        # first find the position of this token in the stream
        comments = list()
        emptyBefore = self.__noDefinitionsBefore(ctx)
        eol = False
        temp = None
        for possibleCommentToken in reversed(self.tokens[0:self.tokens.index(ctx.start)]):
            # if we hit a normal token (i.e. not whitespace, not newline and not token) then stop, since we reached
            # the next previous element, thus the next comments belong to this element
            if possibleCommentToken.channel == 0:
                break
            # if we have found a comment, put it on the "stack". we now have to check if there is an element defined
            # in the same line, since in this case, the comments does not belong to us
            if possibleCommentToken.channel == 2:
                # if it is something on the comment channel -> get it
                temp = self.replaceTags(possibleCommentToken.text)
                eol = False
            # skip whitespaces
            if possibleCommentToken.channel == 1:
                continue
            # if the previous token was an EOL and and this token is neither a white space nor a comment, thus
            # it is yet another newline,stop (two lines separate a two elements)
            elif eol and not emptyBefore:
                break
            # we have found a new line token. thus if we have stored a comment on the stack, its ok to store it in
            # our element, since it does not belong to a declaration in its line
            if possibleCommentToken.channel == 3:
                if temp is not None:
                    comments.append(temp)
                eol = True
                continue
        # we reverse it in order to get the right order of comments
        return reversed(comments) if len(comments) > 0 else None

    def __noDefinitionsBefore(self, ctx):
        """
        This method indicates whether before the start of ctx, something has been defined, e.g. a different neuron.
        This method is used to identify the start of a model.
        :param ctx: a context
        :type ctx: ctx
        :return: True if nothing defined before, otherwise False.
        :rtype: bool
        """
        for token in self.tokens[0:self.tokens.index(ctx.start)]:
            if token.channel == 0:
                return False
        return True

    def getCommentInLine(self, ctx):
        """
        Returns the sole comment if one is defined in the same line, e.g. function a mV = 10mV # comment
        :param ctx: a context
        :type ctx: ctx
        :return: a comment
        :rtype: str
        """
        for possibleComment in self.tokens[self.tokens.index(ctx.stop):]:
            if possibleComment.channel == 2:
                return self.replaceTags(possibleComment.text)
            if possibleComment.channel == 3:  # channel 3 == new line, thus the one line comment ends here
                break
        return None

    def getCommentStatedAfter(self, ctx):
        """
        Returns the comment which has been stated after the current token but in the same line.
        :param ctx: a context
        :type ctx: ctx
        :return: the corresponding comment or None
        :rtype: str
        """
        comments = list()
        nextLineStartIndex = -1
        # first find out where the next line start, since we want to avoid to see comments, which have
        # been stated in the same line, as comments which are stated after the element
        for possibleToken in self.tokens[self.tokens.index(ctx.stop) + 1:]:
            if possibleToken.channel == 3:
                nextLineStartIndex = self.tokens.index(possibleToken)
                break
        firstLine = False
        for possibleCommentToken in self.tokens[nextLineStartIndex:]:
            if possibleCommentToken.channel == 2:
                # if it is a comment on the comment channel -> get it
                comments.append(self.replaceTags(possibleCommentToken.text))
                firstLine = False

            # we found a white line, thus a comment separator
            if possibleCommentToken.channel == 3 and firstLine:
                break
            elif possibleCommentToken.channel == 3:
                firstLine = True

            # if we see a different element, i.e. that we have reached the next declaration and should stop
            if possibleCommentToken.channel == 0:
                break

        return comments if len(comments) > 0 else None

    def replaceTags(self, _comment=None):
        """
        Returns the raw comment, i.e., without the comment-tags /* ..*/, \""" ""\" and #
        :param _comment: a comment
        :type _comment: str
        :return: a raw comment
        :rtype: str
        """
        ret = _comment
        ret = ret.replace('/*', '').replace('*/', '')
        ret = ret.replace('"""', '')
        return ret.replace('#', '')
