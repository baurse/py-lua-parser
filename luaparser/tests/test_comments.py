from luaparser.utils import tests
from luaparser import ast
from luaparser.astnodes import *
import textwrap
import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:\t%(message)s')


class CommentsTestCase(tests.TestCase):
    def test_comment_before_local_assign(self):
        tree = ast.parse(textwrap.dedent("""
            -- rate limit
            -- an other comment
            --[==[ a long
            comment
            --]==]
            local rate_limit = 192"""))
        exp = Chunk(Block([
            LocalAssign(
                [Name('rate_limit')],
                [Number(192)],
                [
                    Comment('-- rate limit'),
                    Comment('-- an other comment'),
                    Comment('--[==[ a long\ncomment\n--]==]', True)
                ]
            )
        ]))
        self.assertEqual(exp, tree)

    def test_comment_before_global_assign(self):
        tree = ast.parse(textwrap.dedent("""
            -- rate limit
            rate_limit = 192"""))
        exp = Chunk(Block([
            Assign(
                [Name('rate_limit')],
                [Number(192)],
                [Comment('-- rate limit')]
            )
        ]))
        self.assertEqual(exp, tree)

    def test_comment_synonym_before_global_assign(self):
        tree = ast.parse(textwrap.dedent("""
            # rate limit
            rate_limit = 192
            """))
        exp = Chunk(Block([
            Assign(
                [Name('rate_limit')],
                [Number(192)],
                [Comment('# rate limit')]
            )
        ]))
        self.assertEqual(exp, tree)

    def test_inline_comment_at_global_assign(self):
        tree = ast.parse(textwrap.dedent("""
            rate_limit = 192 -- rate limit"""))
        exp = Chunk(Block([
            Assign(
                [Name('rate_limit')],
                [Number(192)],
                [Comment('-- rate limit')]
            )
        ]))
        self.assertEqual(exp, tree)

    def test_inline_comment_at_multiple_global_assigns(self):
        tree = ast.parse(textwrap.dedent("""
            rate_limit = 192 -- rate limit

            rate_limit_two = 1922 -- rate limit 2"""))
        exp = Chunk(Block([
            Assign(
                [Name('rate_limit')],
                [Number(192)],
                [Comment('-- rate limit')]
            ),
            Assign(
                [Name('rate_limit_two')],
                [Number(1922)],
                [Comment(''), Comment('-- rate limit 2')]
            )
        ]))
        self.assertEqual(exp, tree)

    def test_comment_before_method(self):
        tree = ast.parse(textwrap.dedent("""       
            --- description
            --- @tparam string arg a string
            function Class:print(arg)
            end"""))
        exp = Chunk(Block([
            Method(
                source=Name('Class'),
                name=Name('print'),
                args=[Name('arg')],
                body=Block([]),
                comments=[Comment('--- description'), Comment('--- @tparam string arg a string')]
            )
        ]))
        self.assertEqual(exp, tree)

    def test_comment_in_table(self):
        tree = ast.parse(textwrap.dedent("""
            --- @table a table of constants
            local limits = {
              -- pre field 1
              HIGH = 127,    -- max rate limit
              -- pre field 2
              LOW  = 42,   -- min rate limit
              [true] = false, -- test
              "foo" -- just a value
              -- last
              ,toto -- toto value
              ,
              Model = true -- model
            }"""))
        exp = Chunk(Block([
            LocalAssign(
                [Name('limits')],
                [Table([
                    Field(Name('HIGH'), Number(127), [Comment('-- pre field 1'), Comment('-- max rate limit')]),
                    Field(Name('LOW'), Number(42), [Comment('-- pre field 2'), Comment('-- min rate limit')]),
                    Field(TrueExpr(), FalseExpr(), [Comment('-- test')], between_brackets=True),
                    Field(Number(1), String('foo', StringDelimiter.DOUBLE_QUOTE), [Comment('-- just a value')]),
                    Field(Number(2), Name('toto'), [Comment('-- last'), Comment('-- toto value')]),
                    Field(Name('Model'), TrueExpr(), [Comment(''), Comment('-- model')])
                ])],
                [Comment('--- @table a table of constants')]
            )
        ]))
        self.assertEqual(exp, tree)

    def test_comment_in_table_2(self):
        tree = ast.parse(textwrap.dedent("""
            --- @module utils

            return {
                --- @export
                BAR = 4,
                --- test
                FOO = 5
            }"""))
        exp = Chunk(Block([
            Return(values=[
                Table([
                    Field(Name('BAR'), Number(4), [Comment('--- @export')]),
                    Field(Name('FOO'), Number(5), [Comment('--- test')])
                ])]
            )
        ]), comments=[
            Comment('--- @module utils'),
            Comment('')
        ])
        self.assertEqual(exp, tree)

    def test_comment_in_table_with_whitespace(self):
        tree = ast.parse(textwrap.dedent("""
            --- @module utils

            return {
                --- @export
                BAR = 4,


                --- test
                FOO = 5
            }"""))
        exp = Chunk(Block([
            Return(values=[
                Table([
                    Field(Name('BAR'), Number(4), [Comment('--- @export')]),
                    Field(Name('FOO'), Number(5), [Comment(''), Comment(''), Comment('--- test')])
                ])]
            )
        ]), comments=[
            Comment('--- @module utils'),
            Comment('')
        ])
        self.assertEqual(exp, tree)

    def test_comment_in_table_with_whitespace_2(self):
        tree = ast.parse(textwrap.dedent("""
            --- @module utils

            return {
                BAR = 4,

                FOO = 5
            }"""))
        exp = Chunk(Block([
            Return(values=[
                Table([
                    Field(Name('BAR'), Number(4)),
                    Field(Name('FOO'), Number(5), [Comment('')])
                ])]
            )
        ]), comments=[
            Comment('--- @module utils'),
            Comment('')
        ])
        self.assertEqual(exp, tree)

    def test_comment_after_global_assign_at_chunk_end(self):
        tree = ast.parse(textwrap.dedent("""
            rate_limit = 192
            -- the above specifies the rate limit"""))
        exp = Chunk(Block([
            Assign(
                [Name('rate_limit')],
                [Number(192)]
            )
        ]),
        None,
        [Comment('-- the above specifies the rate limit')])
        self.assertEqual(exp, tree)

    def test_comment_after_global_assign_at_chunk_end_with_space(self):
        tree = ast.parse(textwrap.dedent("""
            rate_limit = 192


            -- the above specifies the rate limit"""))
        exp = Chunk(Block([
            Assign(
                [Name('rate_limit')],
                [Number(192)]
            )
        ]),
        None,
        [Comment(''), Comment(''), Comment('-- the above specifies the rate limit')])
        self.assertEqual(exp, tree)

    def test_white_space_at_chunk_end(self):
        tree = ast.parse(textwrap.dedent("""
            rate_limit = 192


            """))
        exp = Chunk(Block([
            Assign(
                [Name('rate_limit')],
                [Number(192)]
            )
        ]),
        None,
        [Comment(''), Comment(''), Comment('')])
        self.assertEqual(exp, tree)

    def test_white_space_at_chunk_end_after_comment(self):
        tree = ast.parse(textwrap.dedent("""
            rate_limit = 192

            -- this is a comment in between empty lines

            """))
        exp = Chunk(Block([
            Assign(
                [Name('rate_limit')],
                [Number(192)]
            )
        ]),
        None,
        [Comment(''), Comment('-- this is a comment in between empty lines'), Comment(''), Comment('')])
        self.assertEqual(exp, tree)

    def test_comment_before_and_after_global_assign_at_chunk_end(self):
        tree = ast.parse(textwrap.dedent("""
            -- the below is a rate limit
            rate_limit = 192
            -- the above specifies is a rate limit"""))
        exp = Chunk(Block([
            Assign(
                [Name('rate_limit')],
                [Number(192)],
                [Comment('-- the below is a rate limit')]
            )
        ]),
        None,
        [Comment('-- the above specifies is a rate limit')])
        self.assertEqual(exp, tree)

    def test_comments_all_around_global_assign(self):
        tree = ast.parse(textwrap.dedent("""
            -- the below is a rate limit
            rate_limit = 192 -- this is a rate limit
            -- the above specifies is a rate limit"""))
        exp = Chunk(Block([
            Assign(
                [Name('rate_limit')],
                [Number(192)],
                [Comment('-- the below is a rate limit'), Comment('-- this is a rate limit')]
            )
        ]),
        None,
        [Comment('-- the above specifies is a rate limit')])
        self.assertEqual(exp, tree)

    def test_single_line_comment_at_chunk_start(self):
        tree = ast.parse(textwrap.dedent("""
            -- this is a comment at the start of a chunk

            -- the below is a rate limit
            rate_limit = 192"""))
        exp = Chunk(Block([
            Assign(
                [Name('rate_limit')],
                [Number(192)],
                [Comment('-- the below is a rate limit')]
            )
        ]),
        [Comment('-- this is a comment at the start of a chunk'),
        Comment('')]
        )
        self.assertEqual(exp, tree)

    def test_multi_line_comment_at_chunk_star(self):
        tree = ast.parse(textwrap.dedent("""
            -- this is a comment at the start of a chunk
            -- it has more than one line!

            rate_limit = 192"""))
        exp = Chunk(Block([
            Assign(
                [Name('rate_limit')],
                [Number(192)]
            )
        ]),
        [Comment('-- this is a comment at the start of a chunk'), 
        Comment('-- it has more than one line!'),
        Comment('')]
        )
        self.assertEqual(exp, tree)

    def test_multi_line_comment_at_chunk_start_2(self):
        tree = ast.parse(textwrap.dedent("""
            -- this is a comment at the start of a chunk
            -- it has more than one line!

            -- the below is a rate limit
            rate_limit = 192"""))
        exp = Chunk(Block([
            Assign(
                [Name('rate_limit')],
                [Number(192)],
                [Comment('-- the below is a rate limit')]
            )
        ]),
        [Comment('-- this is a comment at the start of a chunk'), 
        Comment('-- it has more than one line!'),
        Comment('')]
        )
        self.assertEqual(exp, tree)

    def test_multi_line_comment_at_chunk_start_3(self):
        tree = ast.parse(textwrap.dedent("""
            -- this is a comment at the start of a chunk
            -- it has more than one line!

            -- this comment too is part of the chunk comment

            -- the below is a rate limit
            rate_limit = 192"""))
        exp = Chunk(Block([
            Assign(
                [Name('rate_limit')],
                [Number(192)],
                [Comment('-- the below is a rate limit')]
            )
        ]),
        [Comment('-- this is a comment at the start of a chunk'), 
        Comment('-- it has more than one line!'),
        Comment(''),
        Comment('-- this comment too is part of the chunk comment'),
        Comment('')]
        )
        self.assertEqual(exp, tree)

    def test_multi_line_comment_at_chunk_start_belonging_to_statement(self):
        tree = ast.parse(textwrap.dedent("""
            -- this is a comment at the start of a chunk
            -- it has more than one line!
            -- but it actually belongs to the statement as there is no empty line between them
            rate_limit = 192"""))
        exp = Chunk(Block([
            Assign(
                [Name('rate_limit')],
                [Number(192)],
                [Comment('-- this is a comment at the start of a chunk'), 
                Comment('-- it has more than one line!'),
                Comment('-- but it actually belongs to the statement as there is no empty line between them')]
            )
        ]))
        self.assertEqual(exp, tree)
