from luaparser.utils import tests
from luaparser import ast
from luaparser.astnodes import *
import textwrap


class LuaOutputTestCase(tests.TestCase):
    def test_assign(self):
        source = textwrap.dedent('''\
            a = 42
            local b = "42"''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_while(self):
        source = textwrap.dedent('''\
            while a[i] do
                print(a[i])
                i = i + 1
            end''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_repeat(self):
        source = textwrap.dedent('''\
            repeat
                print("value of a:", a)
            until a > 15''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_if(self):
        source = textwrap.dedent('''\
            if op == "+" then
                r = a + b
            elseif op == "-" then
                r = a - b
            elseif op == "*" then
                r = a * b
            elseif op == "/" then
                r = a / b
            else
                error("invalid operation")
            end''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_if_without_else(self):
        source = textwrap.dedent('''\
            if op == "+" then
                r = a + b
            end''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_goto(self):
        source = textwrap.dedent('''\
            ::label::
            goto label''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_func(self):
        source = textwrap.dedent('''\
            function nop(arg, ...)
                break
                return 1, 2, 3
            end''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_empty_func(self):
        source = textwrap.dedent('''\
            function nop(arg, ...) end''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_local_func(self):
        source = textwrap.dedent('''\
            local function nop(arg, ...)
                break
                return 1, 2, 3
            end''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_local_empty_func(self):
        source = textwrap.dedent('''\
            local function nop(arg, ...) end''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_anonymous_func(self):
        source = textwrap.dedent('''\
            ano = function()
                nop()
            end''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_empty_anonymous_func(self):
        source = textwrap.dedent('''\
            func = function() end''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_for_num(self):
        source = textwrap.dedent('''\
            for i = 1, 10 do
                print(i)
            end''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_for_in(self):
        source = textwrap.dedent('''\
            for key, value in pairs(t) do
                print(key, value)
            end''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_successive_indents(self):
        source = textwrap.dedent('''\
            for i = 1, 10 do
                for j = 1, 10 do
                    for k = 1, 10 do
                        print(i * j * k)
                    end
                end
            end''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_call_invoke(self):
        source = textwrap.dedent('''\
            call("foo")
            invoke:me("ok")''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_method(self):
        source = textwrap.dedent('''\
            function my:method(arg1, ...)
                nop()
            end''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_table(self):
        source = textwrap.dedent('''\
            local table = {
                ['ok'] = true,
                foo = bar,
            }''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_table_comments(self):
        source = textwrap.dedent('''\
            -- this is a table
            local table = {
                -- this is the first field
                ['ok'] = true,
                -- this is the second field
                foo = bar,
                foob = barb,
                -- this is the fourth field
                a = b,
            }''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_table_as_array(self):
        source = textwrap.dedent('''\
            local table = {
                true,
                bar,
            }''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))