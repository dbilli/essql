
from abc import abstractmethod

#from pyparsing import *
import pyparsing as pp

# Required for parsing
pp.ParserElement.enablePackrat()

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class AST(object):

    def __init__(self):
        return

    def __str__(self):
        return self.toString()
   
    @abstractmethod
    def toString(self):
        pass

#----------------------------------------------------------------------#
# Literals                                                             #
#----------------------------------------------------------------------#

class ASTNumericLiteral(AST):

    def __init__(self, value):
        self.value = value

    def toString(self):
        return 'Number(%s)' % (self.value)
       

class ASTStringLiteral(AST):

    def __init__(self, value):
        self.value = value
        
    def toString(self):
        return 'String(%s)' % (self.value)

class ASTBoolLiteral(AST):

    def __init__(self, value):
        self.value = value
        
    def toString(self):
        return 'Bool(%s)' % (self.value)

class ASTIdentifier(AST):

    def __init__(self, value):
        self.value = value
        
    def toString(self):
        return 'Identifier(%s)' % (self.value)

#----------------------------------------------------------------------#
# Expressions                                                          #
#----------------------------------------------------------------------#

class ASTExpr(AST):
    pass

class ASTUnaryExpr(ASTExpr):

    def __init__(self, op, expr):
        self.op = op
        self.expr1 = expr
        
    def toString(self):
            return '(%s %s)' % (self.op , self.expr1.toString())

class ASTBinaryExpr(ASTExpr):

    def __init__(self, op, expr1, expr2):
        self.op = op
        self.expr1 = expr1
        self.expr2 = expr2
        
    def toString(self):
            return '(%s %s %s)' % ( self.expr1.toString() ,  self.op , self.expr2.toString())

class ASTTernaryExpr(ASTExpr):

    def __init__(self, op, expr1, expr2, expr3):
        self.op = op
        self.expr1 = expr1
        self.expr2 = expr2
        self.expr3 = expr3
        
    def toString(self):
            return '(%s %s %s %s)' % ( self.op, self.expr1.toString() ,  self.expr2.toString() , self.expr3.toString() )        

class ASTCall(ASTExpr):

    def __init__(self, identifier, params):
        self.identifier = identifier
        self.params = params
        
    def toString(self):
        return 'CALL(%s, %s)' % (self.identifier.toString(),  ','.join([p.toString() for p in self.params]) )

class ASTQueryString(ASTExpr):

    def __init__(self, query_string):
        self.query_string = query_string
        
    def toString(self):
        return 'querystring(%s)' % (self.query_string)

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class ASTSelectColumn(AST):

    def __init__(self, expr, alias):
        self.expr  = expr
        self.alias = alias
        
    def toString(self):
        if self.alias:
            return 'Column(%s AS %s)' % (self.expr.toString(), self.alias.toString())
        else:
            return 'Column(%s)' % (self.expr.toString())

class ASTSelect(AST):

    def __init__(self, columns):
        self.columns  = columns
        
    def toString(self):
            return 'Select(%s)' % ( ','.join([c.toString() for c in self.columns]) )

#----------------------------------------------------------------------#
# FROM                                                                 #
#----------------------------------------------------------------------#

class ASTTable(AST):

    def __init__(self, name, alias):
        self.name  = name
        self.alias = alias
        
    def toString(self):
        if self.alias:
            return 'Table(%s AS %s)' % (self.name.toString(), self.alias.toString())
        else:
            return 'Table(%s)' % (self.name.toString())

class ASTFrom(AST):

    def __init__(self, sources):
        self.sources  = sources
        
    def toString(self):
            return 'From(%s)' % ( ','.join([ s.toString() for s in self.sources ]) )

#----------------------------------------------------------------------#
# WHERE                                                                #
#----------------------------------------------------------------------#

class ASTWhere(AST):

    def __init__(self, expr):
        self.expr = expr
        
    def toString(self):
            return 'Where(%s)' % ( self.expr.toString() )

#----------------------------------------------------------------------#
# GROUP / HAVING                                                       #
#----------------------------------------------------------------------#

class ASTGroup(AST):

    def __init__(self, exprs):
        self.exprs  = exprs
        
    def toString(self):
            return 'Group(%s)' % ( ','.join([ e.toString() for e in self.exprs ]) )

class ASTHaving(AST):

    def __init__(self, expr):
        self.expr  = expr
        
    def toString(self):
        return 'Having(%s)' % (self.expr.toString())

#----------------------------------------------------------------------#
# SELECT BODY                                                          #
#----------------------------------------------------------------------#

class ASTSelectBody(AST):

    def __init__(self, select, frm, where, group, having): #, orderby, limit):
        self.select  = select   
        self.frm     = frm     
        self.where   = where   
        self.group   = group   
        self.having  = having  
        
    def toString(self):
            s = ''
            s += self.select.toString()
            if self.frm     : s += '\n' + self.frm    .toString()
            if self.where   : s += '\n' + self.where  .toString()
            if self.group   : s += '\n' + self.group  .toString()
            if self.having  : s += '\n' + self.having .toString()
            return s

#----------------------------------------------------------------------#
# ORDER                                                                #
#----------------------------------------------------------------------#

class ASTOrder(AST):

    def __init__(self, cols):
        self.cols  = cols
        
    def toString(self):
            return 'OrderBy(%s)' % ( ','.join([ c.toString() for c in self.cols ]) )

class ASTOrderTerm(AST):

    def __init__(self, expr, dir):
        self.expr  = expr
        self.dir   = dir
        
    def toString(self):
        return '(%s %s)' % (self.expr.toString(), self.dir)

#----------------------------------------------------------------------#
# LIMIT                                                                #
#----------------------------------------------------------------------#

class ASTLimit(AST):

    def __init__(self, expr):
        self.expr  = expr
        
    def toString(self):
            return 'Limit(%s)' % (self.expr.toString())

#----------------------------------------------------------------------#
# FULL QUERY                                                           #
#----------------------------------------------------------------------#

class ASTQuery(AST):

    def __init__(self, s, o, l):
        self.s   = s   
        self.o   = o     
        self.l   = l   
        
    def toString(self):
            s = ''
            s += self.s.toString()
            if self.o     : s += '\n' + self.o  .toString()
            if self.l     : s += '\n' + self.l  .toString()
            return s
            
#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class Parser(object):

    def __init__(self):
        self._parser = self.create_parser()
    
    def parse(self, s):
        return self._parser.parseString(s)[0]
    
    #
    # Factory methods
    #

    # LITERALS
    
    def createBoolLiteral(self, b):
        return ASTBoolLiteral(b)
    
    def createStringLiteral(self, s):
        return ASTStringLiteral(s)

    def createNumericLiteral(self, s):
        return ASTNumericLiteral(s)

    def createIdentifier(self, symbol):
        return ASTIdentifier(symbol)

    # EXPRESSIONS

    def createASTUnaryExpr(self, op, e1):
        return ASTUnaryExpr(op, e1)
        
    def createBinaryExpr(self, op, e1, e2):
        return ASTBinaryExpr(op, e1, e2)

    def createASTTernaryExpr(self, op, e1, e2, e3):
        return ASTTernaryExpr(op, e1, e2, e3)
    
    def createCall(self, name, params):
        return ASTCall(name, params)
    
    def createQueryString(self, s):
        return ASTQueryString(s)

    # SELECT col.....        

    def createASTSelect(self, col_exprs):
        return ASTSelect(col_exprs)

    def createASTSelectColumn(self, expr, alias):
        return ASTSelectColumn(expr, alias)
        
    # FROM
    
    def createASTFrom(self, tables):
        return ASTFrom( tables )

    def createASTTable(self, table, table_alias):
        return ASTTable(table, table_alias)
    
    # WHERE

    def createASTWhere(self, expr):
        return ASTWhere(expr)
    
    # ORDER
    
    def createOrderTerm(self, expr, direction):
        return ASTOrderTerm(expr, direction)

    def createASTOrder(self, expr_list):
        return ASTOrder(expr_list)

    # GROUP HAVING
    
    def createASTGroup(self, expr_list):
        return ASTGroup(expr_list)
        
    def createASTHaving(self, expr ):
        return ASTHaving( expr )
    
    # LIMIT
    
    def createASTLimit(self, expr):
        return ASTLimit( expr )

    # FULL QUERY

    def createQuery(self, s, o, l):
        return ASTQuery(s, o, l)
        
    def createSelectBody(self, s, f, w, g, h):
        return ASTSelectBody(s,f, w, g, h)
    
    
    #
    # SQL Parser taken from pyparsing/examples/select_parser.py 
    #
    def create_parser(self):
        
        LPAR, RPAR, COMMA = map(pp.Suppress, "(),")
        
        DOT, STAR = map(pp.Literal, ".*")
        
        #select_stmt = Forward().setName("select statement")
        
    
        #UNION             = CaselessKeyword('UNION')
        #ALL               = CaselessKeyword('ALL') 
        AND               = pp.CaselessKeyword('AND') 
        #INTERSECT         = CaselessKeyword('INTERSECT') 
        #EXCEPT            = CaselessKeyword('EXCEPT') 
        #COLLATE           = CaselessKeyword('COLLATE') 
        ASC               = pp.CaselessKeyword('ASC') 
        DESC              = pp.CaselessKeyword('DESC') 
        #ON                = CaselessKeyword('ON') 
        #USING             = CaselessKeyword('USING') 
        NATURAL           = pp.CaselessKeyword('NATURAL') 
        #INNER             = CaselessKeyword('INNER') 
        #CROSS             = CaselessKeyword('CROSS') 
        #LEFT              = CaselessKeyword('LEFT') 
        #OUTER             = CaselessKeyword('OUTER') 
        #JOIN              = CaselessKeyword('JOIN') 
        AS                = pp.CaselessKeyword('AS').suppress() 
        #INDEXED           = CaselessKeyword('INDEXED') 
        NOT               = pp.CaselessKeyword('NOT')
        SELECT            = pp.CaselessKeyword('SELECT').suppress() 
        TOP               = pp.CaselessKeyword('TOP').suppress()
        #DISTINCT          = CaselessKeyword('DISTINCT') 
        FROM              = pp.CaselessKeyword('FROM').suppress() 
        WHERE             = pp.CaselessKeyword('WHERE').suppress()
        GROUP             = pp.CaselessKeyword('GROUP') 
        BY                = pp.CaselessKeyword('BY').suppress()  
        HAVING            = pp.CaselessKeyword('HAVING') 
        ORDER             = pp.CaselessKeyword('ORDER').suppress() 
        LIMIT             = pp.CaselessKeyword('LIMIT').suppress()
        #OFFSET            = CaselessKeyword('OFFSET') 
        OR                = pp.CaselessKeyword('OR') 
        #CAST              = CaselessKeyword('CAST') 
        ISNULL            = pp.CaselessKeyword('ISNULL') 
        NOTNULL           = pp.CaselessKeyword('NOTNULL') 
        
        NULL              = pp.CaselessKeyword('NULL') 
        
        IS                = pp.CaselessKeyword('IS') 
        BETWEEN           = pp.CaselessKeyword('BETWEEN') 
        
        #ELSE              = CaselessKeyword('ELSE') 
        #END               = CaselessKeyword('END')
        #CASE              = CaselessKeyword('CASE') 
        #WHEN              = CaselessKeyword('WHEN') 
        #THEN              = CaselessKeyword('THEN') 
        
        #EXISTS            = CaselessKeyword('EXISTS') 
        
        IN                = pp.CaselessKeyword('IN') 
        LIKE              = pp.CaselessKeyword('LIKE') 
        GLOB              = pp.CaselessKeyword('GLOB') 
        REGEXP            = pp.CaselessKeyword('REGEXP') 
        MATCH             = pp.CaselessKeyword('MATCH') 
        ESCAPE            = pp.CaselessKeyword('ESCAPE') 
        
        QUERYSTRING        = pp.CaselessKeyword('QUERYSTRING') 
        
        #CURRENT_TIME      = CaselessKeyword('CURRENT_TIME') 
        #CURRENT_DATE      = CaselessKeyword('CURRENT_DATE') 
        #CURRENT_TIMESTAMP = CaselessKeyword('CURRENT_TIMESTAMP') 
        
        TRUE              = pp.CaselessKeyword('TRUE')                     #.setParseAction( lambda s, loc, toks: True  ) 
        FALSE             = pp.CaselessKeyword('FALSE')                    #.setParseAction( lambda s, loc, toks: False ) 
    
        keywords = [
            #UNION             , 
            #ALL               , 
            
            AND               , 
            
            #INTERSECT         , 
            #EXCEPT            , 
            #COLLATE           , 
            
            ASC               , 
            DESC              , 
            
            #ON                , 
            #USING             , 
            NATURAL           , 
            #INNER             , 
            #CROSS             , 
            #LEFT              , 
            #OUTER             , 
            #JOIN              , 
            AS                , 
            #INDEXED           , 
            NOT               , 
            SELECT            , 
            #DISTINCT          , 
            FROM              , 
            WHERE             , 
            GROUP             , 
            BY                , 
            HAVING            , 
            ORDER             , 
            LIMIT             , 
            #OFFSET            , 
            OR                , 
            #CAST              , 
            ISNULL            , 
            NOTNULL           , 
            NULL              , 
            IS                , 
            BETWEEN           , 
            
            #ELSE              , 
            #END               , 
            #CASE              , 
            #WHEN              , 
            #THEN              , 
            
            #EXISTS            , 
            
            IN                , 
            LIKE              , 
            GLOB              , 
            REGEXP            , 
            MATCH             , 
            ESCAPE            , 
            
            #CURRENT_TIME      , 
            #CURRENT_DATE      , 
            #CURRENT_TIMESTAMP , 
            
            QUERYSTRING       ,
            
            TRUE              , 
            FALSE             , 
        ]
        
        keywords = [k.suppress() for k in keywords]
        
        any_keyword = pp.MatchFirst(keywords)
        
        quoted_identifier = pp.QuotedString('"', escQuote='""')
        
        identifier = (~any_keyword + pp.Word(pp.alphas + '@', pp.alphanums + "_"))     .setParseAction( pp.pyparsing_common.downcaseTokens) | quoted_identifier
        
        
        #collation_name = identifier.copy()

        column_name    = identifier.copy()                              .setParseAction( lambda s, loc, toks: self.createStringLiteral(toks[0]) )

        column_alias   = identifier.copy()                              .setParseAction( lambda s, loc, toks: self.createStringLiteral(toks[0]) )

        table_name     = identifier.copy()                              .setParseAction( lambda s, loc, toks: self.createStringLiteral(toks[0]) )
        table_alias    = identifier.copy()                              .setParseAction( lambda s, loc, toks: self.createStringLiteral(toks[0]) )
        
        index_name     = identifier.copy()
        
        function_name  = identifier.copy()
        
        parameter_name = identifier.copy()
        
        #database_name  = identifier.copy()
        
        comment = "--" + pp.restOfLine
        
        # expression
        expr = pp.Forward().setName("expression")
        
        numeric_literal = pp.pyparsing_common.number                           
        
        string_literal = pp.QuotedString("'", escQuote="''")         
        
        query_string_literal = pp.QuotedString("`", escQuote='\\`')                    
        
        #blob_literal = Regex(r"[xX]'[0-9A-Fa-f]+'")
        
        literal_value = (
              numeric_literal                                           .setParseAction( lambda s, loc, toks: self.createNumericLiteral(toks[0])  )                                      
            | string_literal                                            .setParseAction( lambda s, loc, toks: self.createStringLiteral(toks[0])   )
        #    | blob_literal                                             
            | TRUE                                                      .setParseAction( lambda s, loc, toks: self.createBoolLiteral(True)  )
            | FALSE                                                     .setParseAction( lambda s, loc, toks: self.createBoolLiteral(False) )
            | NULL                    
  
            #| CURRENT_TIME            .setParseAction( lambda s, loc, toks: self.createIdentifier(toks[0])  )
            #| CURRENT_DATE            .setParseAction( lambda s, loc, toks: self.createIdentifier(toks[0])  )
            #| CURRENT_TIMESTAMP       .setParseAction( lambda s, loc, toks: self.createIdentifier(toks[0])  )
        )
        
        #bind_parameter = Word("?", nums) | Combine(oneOf(": @ $") + parameter_name)
        
        #type_name = oneOf("TEXT REAL INTEGER BLOB NULL")
        
        
        
        def _op_function( s, loc, toks ):
            # 0            1
            # <identifier> <p1> <p2> ... 
            toks = list(toks)
            name   = toks.pop(0)
            params = toks
            
            return self.createCall(name, params)
        
        def _op_query_string(s, loc, toks):
            #              0            
            # QUERY_STRING `....`
            toks = list(toks)
            query_string = toks[0]
            return self.createQueryString(query_string)

        expr_term = (
            #CAST + LPAR + expr + AS + type_name + RPAR
            #| 
            # EXISTS + LPAR + select_stmt + RPAR
            #| 
            (function_name.setName("function_name")                     .setParseAction( lambda s, loc, toks: self.createIdentifier(toks[0])  )
                 + LPAR 
                 + pp.Optional(
                     STAR                                               .setParseAction( lambda s, loc, toks: self.createIdentifier(toks[0])  )
                     | pp.delimitedList(expr) 
                   ).setName('params') 
                 + RPAR
            )                                                           .setParseAction( _op_function  )
            |
            (pp.Optional(QUERYSTRING).suppress() + query_string_literal)   .setParseAction( _op_query_string  )
            | 
            literal_value
            #| bind_parameter
            | 
            
            #Group(
            #    identifier("col_db") + DOT + identifier("col_tab") + DOT + identifier("col")
            #)
            #| 
            #Group(identifier("col_tab") + DOT + identifier("col"))
            #| 
            #Group(identifier("col"))                                   .setParseAction( lambda s, loc, toks: ASTIdentifier(toks[0])  )
            
            # <identifier>.<identifier>.<identifier>
            pp.delimitedList(identifier, delim='.', combine=True)          .setParseAction( lambda s, loc, toks: self.createIdentifier(toks[0])  )
              
        )
        
        NOT_NULL    = pp.Group(NOT + NULL)
        NOT_BETWEEN = pp.Group(NOT + BETWEEN)
        NOT_IN      = pp.Group(NOT + IN)
        NOT_LIKE    = pp.Group(NOT + LIKE)
        NOT_MATCH   = pp.Group(NOT + MATCH)
        NOT_GLOB    = pp.Group(NOT + GLOB)
        NOT_REGEXP  = pp.Group(NOT + REGEXP)
        
        UNARY, BINARY, TERNARY = 1, 2, 3



        def _op_handle_unary(s, loc, toks):
            toks = list(toks[0])
            
            op = toks.pop(0)
            e1 = toks.pop(0)
            
            expr = self.createASTUnaryExpr(op, e1)

            return [ expr ]
            
        def _op_handle_binary(s, loc, toks):
            toks = list(toks[0])

            # e1 op e2 op e3 op e3
            expr1 = toks.pop(0)
            if not toks:
                return expr1
                
            while toks:
                op = toks.pop(0)
                expr2 = toks.pop(0)
                expr1 = self.createBinaryExpr(op, expr1, expr2)
            
            return [ expr1 ]

        def _op_handle_ternary(s, loc, toks):
            toks = list(toks[0])
            
            # 0  1       2  3   4
            # e1 between e2 and e3
            expr1 = toks[0]
            expr2 = toks[2]
            expr3 = toks[4]
            
            expr = self.createASTTernaryExpr('between', expr1, expr2, expr3)
            return [ expr ]


        expr << pp.infixNotation(
            expr_term                                                       
            ,
            [
                (pp.oneOf("- + ~") | NOT       , UNARY , pp.opAssoc.RIGHT     , _op_handle_unary ),
                (ISNULL | NOTNULL | NOT_NULL   , UNARY , pp.opAssoc.LEFT      , _op_handle_unary ),
                ("||"                          , BINARY, pp.opAssoc.LEFT      , _op_handle_binary),
                (pp.oneOf("* / %")             , BINARY, pp.opAssoc.LEFT      , _op_handle_binary),
                (pp.oneOf("+ -")               , BINARY, pp.opAssoc.LEFT      , _op_handle_binary),
                (pp.oneOf("<< >> & |")         , BINARY, pp.opAssoc.LEFT      , _op_handle_binary),
                (pp.oneOf("< <= > >=")         , BINARY, pp.opAssoc.LEFT      , _op_handle_binary),
                (
                    pp.oneOf("= == != <>")
                    | IS
                    | IN
                    | LIKE
                    | GLOB
                    | MATCH
                    | REGEXP
                    | NOT_IN
                    | NOT_LIKE
                    | NOT_GLOB
                    | NOT_MATCH
                    | NOT_REGEXP,
                                               BINARY, pp.opAssoc.LEFT     , _op_handle_binary ),
                ((BETWEEN | NOT_BETWEEN, AND), TERNARY, pp.opAssoc.LEFT    , _op_handle_ternary),       
                (
                    (IN | NOT_IN) + 
                    LPAR + 
                    pp.Group(
                     #select_stmt | 
                     pp.delimitedList(expr)
                    ) + 
                    RPAR
                                            , UNARY, pp.opAssoc.LEFT       , _op_handle_unary ),
                (AND                        , BINARY, pp.opAssoc.LEFT      , _op_handle_binary),
                (OR                         , BINARY, pp.opAssoc.LEFT      , _op_handle_binary),
            ],
        )                                                              
        
        #compound_operator = UNION + Optional(ALL) | INTERSECT | EXCEPT
        
        #
        # ORDER BY
        #
        def _opt_ordering_term(s, loc, toks):
            toks = list(toks[0])

            # expr DESC|ASC
            direction = None 
            expr      = toks.pop(0)
            if toks:
                direction = toks.pop(0)

            return self.createOrderTerm(expr, direction)
            
        ordering_term = pp.Group(
            (expr("order_key"))
            #+ Optional(COLLATE + collation_name("collate"))
            + (pp.Optional(ASC | DESC)("direction"))
        )                                                               .setParseAction( _opt_ordering_term )
        
        #join_constraint = Group(
        #    Optional(ON + expr | USING + LPAR + Group(delimitedList(column_name)) + RPAR)
        #)
        
        #join_op = COMMA | Group(
        #    Optional(NATURAL) + Optional(INNER | CROSS | LEFT + OUTER | LEFT | OUTER) + JOIN
        #)
        
        def _op_single_source(s, loc, toks):
            toks = list(toks)
            
            table_alias      = None
            table_identifier = toks.pop(0)[0]
            if toks:
                table_alias = toks.pop(0)
            
            return self.createASTTable(table_identifier, table_alias)
        
        #join_source = Forward()
        single_source = (
            pp.Group(
                  #database_name("database") + DOT + table_name("table*") 
                  #| 
                  table_name("table*")
                 ) 
                 + pp.Optional(pp.Optional(AS) + table_alias("table_alias*"))  
            #     + Optional(INDEXED + BY + index_name("name") | NOT + INDEXED)("index")
            #| 
            #(LPAR + select_stmt + RPAR + Optional(Optional(AS) + table_alias))
            #| (LPAR + join_source + RPAR)
        )                                                               .setParseAction( _op_single_source )
        #
        #join_source <<= (
        #    #Group(single_source + OneOrMore(join_op + single_source + join_constraint))
        #    #| 
        #    single_source
        #)
        join_source = single_source
        
        
        
        
        def _op_col_alias_callback(s, loc, toks):
            expr   = toks.get('expr')
            alias  = toks.get('alias')           
            return self.createASTSelectColumn(expr, alias) 
        
        # result_column = "*" | table_name + "." + "*" | Group(expr + Optional(Optional(AS) + column_alias))
        result_column = (
            STAR("expr")                                                   
            | 
            #table_name("col_table") + DOT + STAR("col")                .setParseAction( _op_col_alias_callback )
            #| 
            (
             (
              expr("expr") + pp.Optional(pp.Optional(AS) + column_alias("alias") )
             )             
             .setParseAction( _op_col_alias_callback )
            )
        )                                                                   
        
        def _op_columns_stmt(s, loc, toks):
            col_exprs = list(toks)
            #col_exprs = [ e for e in col_exprs]

            return self.createASTSelect(col_exprs)
        
        #columns_stmt = Optional(DISTINCT | ALL) + Group(delimitedList(result_column))("columns")
        columns_stmt = pp.delimitedList(result_column)                     .setParseAction( _op_columns_stmt )
        
        #
        # FROM
        #
        def _op_from_callback(s, loc, toks):
            tables = list(toks.get("from")) 
            return self.createASTFrom( tables )
        
        
        
        #from_stmt  = (FROM + join_source("from*"))                      .setParseAction( _op_from_callback ) 
        
        from_stmt = (FROM + pp.delimitedList(join_source, delim=',')("from"))          .setParseAction( _op_from_callback ) 
    
        #
        # TOP
        #
        
        #def _op_top_stmt(s, loc, toks):
        #    expr = toks.get("top_expr")
        #    o = {
        #        'TOP': expr
        #    }
        #    return o
        #
        #top_stmt  = (TOP + expr("top_expr"))                            .setParseAction( _op_top_stmt ) 
        
        #
        # WHERE
        #
        
        def _op_where_callback(s, loc, toks):
            expr = toks.get("where_expr")
            return  self.createASTWhere(expr)
        
        where_stmt = (WHERE + expr("where_expr"))                       .setParseAction( _op_where_callback ) 
        
        #
        # GROUP
        #
        def _op_group_stmt(s, loc, toks):
            expr_list = list(toks['group_by_terms'])
            return self.createASTGroup(expr_list)

        def _op_having_stmt(s, loc, toks):
            expr = toks['having_expr']
            return self.createASTHaving( expr )
            
        group_stmt = (
            GROUP + BY + 
            #Group(delimitedList(ordering_term))("group_by_terms") 
            pp.Group(pp.delimitedList(column_name))("group_by_terms") 
        )                                                               .setParseAction( _op_group_stmt ) 
        
        #
        # HAVING
        #        
        having_stmt = (
            HAVING + expr("having_expr")
        )                                                               .setParseAction( _op_having_stmt ) 
        
        #
        # ORDER
        #
        def _op_order_stmt(s, loc, toks):
            expr_list = list(toks['ordering_terms'])
            return self.createASTOrder(expr_list)
            
        order_stmt = (
            ORDER + BY + 
            pp.Group( pp.delimitedList(ordering_term) )('ordering_terms')  
           
        )                                                               .setParseAction( _op_order_stmt ) 
        
        #
        # LIMIT
        #
        def _op_limit_stmt(s, loc, toks):
            expr = toks['limit_value']
            return self.createASTLimit(expr)
            
        limit_stmt = (LIMIT + 
            #Group(expr + OFFSET + expr) 
            #| 
            #Group(expr + COMMA + expr) 
            #| 
            expr('limit_value')                                                     
        )                                                               .setParseAction( _op_limit_stmt ) 
    
    
    
    
        #
        # SELECT ... FROM ... WHERE .... GROUP BY... HAVING .....
        #
        def _op_select_core(s, loc, toks):
            s = toks.get('COLUMNS')
            f = toks.get('FROM'   )
            w = toks.get('WHERE'  )
            g = toks.get('GROUP'  )
            h = toks.get('HAVING' )
            return self.createSelectBody(s,f, w, g, h)
    
        select_core = (
            SELECT
            #+ Optional(top_stmt('TOP'))
            + columns_stmt('COLUMNS')         
            + pp.Optional(from_stmt ('FROM' ))  
            + pp.Optional(where_stmt('WHERE')) 
            + pp.Optional(
                  group_stmt('GROUP')
                + pp.Optional(having_stmt('HAVING'))
            )
        )                                                                   .setParseAction( _op_select_core ) 
        
        #
        #
        #
        def _opt_select_stmt(s, loc, toks):
            s = toks['SELECT_BODY']
            o = toks.get('ORDER')
            l = toks.get('LIMIT')
            return self.createQuery(s, o, l)
            
        #select_stmt << (
        #    select_core              ("select_core")
        #    #+ ZeroOrMore(compound_operator + select_core)
        #    #+ Optional(order_stmt)   ("order_stmt")
        #    + Optional(limit_stmt("limit_stmt"))   
        #)                                                                   .setParseAction( _opt_select_stmt ) 
        select_stmt = (
            select_core          ("SELECT_BODY")
            #+ ZeroOrMore(compound_operator + select_core)
            + (pp.Optional(order_stmt("ORDER")))
            + (pp.Optional(limit_stmt("LIMIT")))
        )                                                                   .setParseAction( _opt_select_stmt ) 
            
        #
        #
        #
        START = pp.StringStart().suppress()
        END   = pp.StringEnd().suppress()
        
        query_stm = START + select_stmt + END
        
        query_stm.ignore(comment)
        
        return query_stm
    
#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

if __name__ == "__main__":

    import sys
    
    s = sys.argv[1]
    
    parser = Parser()

    r = parser.parse(s)
    
    print(r)
