from luaparser.utils import tests
from luaparser import ast
from luaparser.astnodes import *
import textwrap


class LuaOutputTestCase(tests.TestCase):
    def test_assign(self):
        source = textwrap.dedent('''\
            a = 42''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_local_assign(self):
        source = textwrap.dedent('''\
            local a = 42''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_multi_assign(self):
        source = textwrap.dedent('''\
            a, b = 42, 243''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_local_multi_assign(self):
        source = textwrap.dedent('''\
            local a, b = 42, 243''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_local_var(self):
        source = textwrap.dedent('''\
            local a''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_local_multi_var(self):
        source = textwrap.dedent('''\
            local a, b''')
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

    def test_func_nil_return(self):
        source = textwrap.dedent('''\
            function nop(arg, ...)
                break
                return nil
            end''')
        exp = textwrap.dedent('''\
            function nop(arg, ...)
                break
                return
            end''')
        self.assertEqual(exp, ast.to_lua_source(ast.parse(source)))

    def test_func_empty_return(self):
        source = textwrap.dedent('''\
            function nop(arg, ...)
                break
                return
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

    def test_call(self):
        source = textwrap.dedent('''\
            call("foo")''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_invoke(self):
        source = textwrap.dedent('''\
            invoke:me("ok")''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_nested_invoke(self):
        source = textwrap.dedent('''\
            func1:func2("ok"):func3("ok2")''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_nested_invoke_2(self):
        source = textwrap.dedent('''\
            func1:func2(thingy:func3("ok2"))''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_nested_invoke_3(self):
        source = textwrap.dedent('''\
            base.func1:func2(foo.bar.thingy:func3("ok2"))''')
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

    def test_table_comments_with_whitespace(self):
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

    def test_table_with_trailing_comment(self):
        source = textwrap.dedent('''\
            local table = {
                "jo",
                -- this is a trailing comment
            }''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_table_with_max_comments(self):
        source = textwrap.dedent('''\
            local table = {
                -- before comment
                "jo", -- inline comment
                -- trailing comment
            }''')
        exp = textwrap.dedent('''\
            local table = {
                -- before comment
                -- inline comment
                "jo",
                -- trailing comment
            }''')
        self.assertEqual(exp, ast.to_lua_source(ast.parse(source)))

    def test_table_with_max_comments_and_whitespace(self):
        source = textwrap.dedent('''\
            local table = {

                -- before comment


                "jo", -- inline comment

                -- trailing comment


            }''')
        exp = textwrap.dedent('''\
            local table = {

                -- before comment


                -- inline comment
                "jo",

                -- trailing comment

                
            }''')
        self.assertEqual(exp, ast.to_lua_source(ast.parse(source)))

    def test_table_with_only_comment(self):
        source = textwrap.dedent('''\
            local table = {
                -- comment
            }''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_table_as_array(self):
        source = textwrap.dedent('''\
            local table = {
                true,
                bar,
            }''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_table_as_partial_array(self):
        source = textwrap.dedent('''\
            local table = {
                "jo",
                ["joo"] = "jooooo",
                jup = "jup",
                "dude",
            }''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_table_nested_in_functions(self):
        source = textwrap.dedent('''\
            DRA0202 = Class(CAirUnit)({
                Weapons = {
                    GroundMissile = Class(CIFMissileCorsairWeapon)({
                        IdleState = State(CIFMissileCorsairWeapon.IdleState)({
                            OnGotTarget = function(self)
                                if self.unit:IsUnitState('Moving') then
                                    UnitMethodsSetSpeedMult(self.unit, 1.0)
                                else
                                    UnitMethodsSetBreakOffTriggerMult(self.unit, 2.0)
                                    UnitMethodsSetBreakOffDistanceMult(self.unit, 8.0)
                                    UnitMethodsSetSpeedMult(self.unit, 0.67)
                                    CIFMissileCorsairWeapon.IdleState.OnGotTarget(self)
                                end
                            end,
                        }),
                    }),
                },
            })''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_comment_at_chunk_start(self):
        source = textwrap.dedent('''\
            -- this is a comment at the chunk start
            
            a = 42''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_comment_at_chunk_start_2(self):
        source = textwrap.dedent('''\
            -- this is a comment at the chunk start
            
            -- this comment belongs to the statement
            a = 42''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_trailing_comment(self):
        source = textwrap.dedent('''\
            a = 42
            -- this is a trailing comment''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_comment_between_statements(self):
        source = textwrap.dedent('''\
            a = 42
            -- this is a trailing comment
            b = 12''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_whitespace_between_statements(self):
        source = textwrap.dedent('''\
            a = 42
            
            b = 12''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_whitespace_between_statements_2(self):
        source = textwrap.dedent('''\
            a = 42
            


            b = 12''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_comment_with_whitespace_between_statements(self):
        source = textwrap.dedent('''\
            a = 42

            -- this is a trailing comment


            b = 12''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_trailing_comment_with_spaces(self):
        source = textwrap.dedent('''\
            a = 42

            -- this is a trailing comment''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_trailing_comment_with_spaces_2(self):
        source = textwrap.dedent('''\
            a = 42

            -- this is a trailing comment
            
            
            ''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_trailing_comment_being_whitespace(self):
        source = textwrap.dedent('''\
            a = 42

            ''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_empty_class_1(self):
        source = textwrap.dedent('''\
            Class(DefaultProjectileWeapon)({})''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_comments_return_before(self):
        source = textwrap.dedent('''\
            -- Comment before
            return''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))
    
    def test_comments_return_after(self):
        source = textwrap.dedent('''\
            return
            -- Comment after''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))
    
    def test_comments_return_line(self):
        source = textwrap.dedent('''\
            return -- Comment line''')
        exp = textwrap.dedent('''\
            -- Comment line
            return''')
        self.assertEqual(exp, ast.to_lua_source(ast.parse(source)))
    
    def test_comments_if_statement_before(self):
        source = textwrap.dedent('''\
            if not bp then
                -- Comment before
                return
            end''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_comments_if_statement_after(self):
        source = textwrap.dedent('''\
            if not bp then
                return
                -- Comment after
            end''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))
    
    def test_comments_if_statement_line(self):
        source = textwrap.dedent('''\
            if not bp then
                return -- Comment line
            end''')
        exp = textwrap.dedent('''\
            if not bp then
                -- Comment line
                return
            end''')
        self.assertEqual(exp, ast.to_lua_source(ast.parse(source)))

    def test_comments_if_statement_all(self):
        source = textwrap.dedent('''\
            if not bp then
                -- Comment before
                return -- Comment line
                -- Comment after
            end''')
        exp = textwrap.dedent('''\
            if not bp then
                -- Comment before
                -- Comment line
                return
                -- Comment after
            end''')
        self.assertEqual(exp, ast.to_lua_source(ast.parse(source)))
    
    def test_comments_in_between_if_statement(self):
        source = textwrap.dedent('''\
            if enh == 'Teleporter' then
                self:AddCommandCap('RULEUCC_Teleport')
                -- Comment before elseif
            elseif enh == 'TeleporterRemove' then
                -- Comment in elseif, start
                self:RemoveCommandCap('RULEUCC_Teleport')
                -- Comment in elseif, trailing
            else
                -- meh
            end''')
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))
