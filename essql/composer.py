
from .parser import *

#----------------------------------------------------------------------#
# Literals                                                             #
#----------------------------------------------------------------------#

class _ASTNumericLiteral(ASTNumericLiteral):

    def composeExpr(self, expr_info):
        expr_info['expr'] = [ repr(self.value) ]

class _ASTStringLiteral(ASTStringLiteral):

    def composeExpr(self, expr_info):
        expr_info['expr'] = [ repr(self.value) ]

class _ASTBoolLiteral(ASTBoolLiteral):

    def composeExpr(self, expr_info):
        expr_info['expr'] = [ repr(self.value) ]
    
class _ASTIdentifier(ASTIdentifier):

    def composeExpr(self, expr_info):
        
        sym_name = self.value
        sym_name = sym_name.split(".")[0]
        
        if sym_name != '*':
            expr_info['used_symbols'].append(sym_name)
        
        expr_structure = []
        
        for i, key in enumerate(self.value.split('.')):
            if i == 0:
                expr_structure.append(key)
            else:
                expr_structure.append( "['%s']" % (key) )
        
        expr_info['expr'] = expr_structure

#----------------------------------------------------------------------#
# Expressions                                                          #
#----------------------------------------------------------------------#

class _ASTUnaryExpr(ASTUnaryExpr):

    def composeExpr(self, expr_info):
        self.expr1.composeExpr(expr_info)

        #
        # Create structure
        #
        _structure = []
        _structure.append('(')
        _structure.append(self.op)
        _structure.extend( expr_info['expr'])
        _structure.append(')')
        
        expr_info['expr'] = _structure

class _ASTBinaryExpr(ASTBinaryExpr):

    def composeExpr(self, expr_info):

        self.expr1.composeExpr(expr_info)        
        s1 = expr_info['expr']
        
        self.expr2.composeExpr(expr_info)
        s2 = expr_info['expr']

        #
        # Create structure
        #
        _structure = []
        _structure.append('(')
        _structure.extend( s1 )
        _structure.append(self.op)
        _structure.extend( s2 )
        _structure.append(')')
        
        expr_info['expr'] = _structure

class _ASTTernaryExpr(ASTTernaryExpr):

    def composeExpr(self, expr_info):
        self.expr1.composeExpr(expr_info)
        self.expr2.composeExpr(expr_info)
        self.expr3.composeExpr(expr_info)

class _ASTCall(ASTCall):

    def composeExpr(self, expr_info):

        fun_name = self.identifier.value
        params_exprs = []

        for param_expr in self.params:
            
            expr_info['expr'] = None
            param_expr.composeExpr(expr_info)
            
            params_exprs.append( expr_info['expr'] )

        #
        #
        #
        is_aggr_function = False
        if fun_name.upper() in ['MAX','MIN','AVG','COUNT','SUM']:
            expr_info['used_aggr_functions'].append(fun_name)
            is_aggr_function = True
            
        #
        # Create structure
        #
        _structure = []
        _structure.append('(')
        _structure.append(fun_name)
        _structure.append('(')
        
        if not is_aggr_function:
            for i, pe in enumerate(params_exprs):
     
                _structure.extend(pe)
                if i < len(params_exprs) - 1:
                    _structure.append(',')
        else:
            col_name = params_exprs[0][0]
            _structure.append("'%s'" % (col_name))
            
        _structure.append(')')
        _structure.append(')')
        
        expr_info['expr'] = _structure


class _ASTQueryString(ASTQueryString):

    def composeExpr(self, expr_info):
        raise Exception("QUERY STRING not allowed inside expression")
        
    def composeQuery(self, query_plan):
 
        dsl_obj = query_plan['dsl']
        
        dsl_obj['query'] = {
                'query_string': {
                    'query': self.query_string
                }
        }
        
#----------------------------------------------------------------------#
# SELECT ...                                                           #
#----------------------------------------------------------------------#

class _ASTSelectColumn(ASTSelectColumn):
    
    def composeQuery(self, query_plan):
        

        expr_info = {
            'used_symbols'        : [],
            'used_aggr_functions' : [],
            'expr': None,
            'expr_string': None,
            'alias': None,
        }
        
        self.expr.composeExpr(expr_info)
        
        #
        # Alias
        #
        if self.alias:
             alias = self.alias.value
             
        else:
             if len(expr_info['expr']) == 1:
                 alias = expr_info['expr'][0]
             else:
                 alias = None
        
        expr_info['alias'] = alias
        
        #
        # col expression
        #
        python_expr_string = ''.join(  expr_info['expr'] )
        
        expr_info['expr_string'] = python_expr_string
        
        
        query_plan['columns_processors'].append(expr_info)
        
        dsl_obj = query_plan['dsl'] 
        fields = dsl_obj.get('_source', dsl_obj.setdefault('_source', []))         
        fields.extend( expr_info['used_symbols'] )
    
class _ASTSelect(ASTSelect):

    def composeQuery(self, query_plan):

        for c in self.columns:
            c.composeQuery(query_plan)
    
#----------------------------------------------------------------------#
# FROM                                                                 #
#----------------------------------------------------------------------#

class _ASTTable(ASTTable):

    def composeQuery(self, query_plan):

       index_name = self.name.value

       query_plan['indexes'].append( index_name )
    
class _ASTFrom(ASTFrom):

    def composeQuery(self, query_plan):

       for s in self.sources:
           s.composeQuery(query_plan)
    
#----------------------------------------------------------------------#
# WHERE                                                                #
#----------------------------------------------------------------------#

class _ASTWhere(ASTWhere):

    MATCH_ALL = { "match_all": {} }

    def toString(self):
            return 'Where(%s)' % ( self.expr.toString() if self.expr else None )

    def composeQuery(self, query_plan):
        
        dsl = query_plan['dsl']

        if self.expr is None:
            o = _ASTWhere.MATCH_ALL
            dsl['query'] = o
        else:
            self.expr.composeQuery(query_plan)

#----------------------------------------------------------------------#
# ORDER                                                                #
#----------------------------------------------------------------------#

class _ASTOrderTerm(ASTOrderTerm):

    def composeQuery(self, query_plan):

       dsl_obj = query_plan['dsl']
       
       selected_fields = dsl_obj.get('fields')
     
       identifier = self.expr.value 
       
       o = {}
       o[identifier] = { "order": "desc" if self.dir == "DESC" else "asc" }
       
       
       sort_list = dsl_obj.get("sort", dsl_obj.setdefault("sort",[]))
       sort_list.append(o)

class _ASTOrder(ASTOrder):

    def composeQuery(self, query_plan):

        for c in self.cols:
            c.composeQuery(query_plan)

#----------------------------------------------------------------------#
# GROUP / HAVING                                                       #
#----------------------------------------------------------------------#

class _ASTGroup(ASTGroup):

    def composeQuery(self, query_plan):

        dsl_obj = query_plan['dsl']

        fields = [ f_expr.value for f_expr in self.exprs ]
        
        query_plan['aggregation_fields'] = fields
     
        root_body = {
            #'aggs': {}
        }
        
        aggs_body = root_body
        
        for field_name in fields:

            aggs_body['aggs'] = {}

            if field_name.endswith(".keyword"):
                aggr_name = field_name.replace(".keyword","")
            else:
                aggr_name = field_name 
            
            field_aggr_body = {
                "terms": {
                    "field": field_name,
                    "missing": 0.00000000000000001, 
                },
            }
            
            aggs_body['aggs'][aggr_name] = field_aggr_body
            
            aggs_body = field_aggr_body

        #
        # Aggregation for min,max,avg(<field>)
        #
        field_name = fields[-1]
        
        field_aggr_body = {
            "stats": { 
                "field": field_name 
            } ,
        }
        counters_name = "stats(%s)" % (field_name)
        aggs_body['aggs'] = {}
        aggs_body['aggs'][ counters_name ] = field_aggr_body






        dsl_obj.update( root_body )
        
        #dsl_obj['size'] = 0


class _ASTHaving(ASTHaving):
    pass

#----------------------------------------------------------------------#
# LIMIT                                                                #
#----------------------------------------------------------------------#

class _ASTLimit(ASTLimit):

    def composeQuery(self, query_plan):

        dsl = query_plan['dsl']

        val = self.expr.value

        dsl['size'] = val

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class _ASTSelectBody(ASTSelectBody):

    def __init__(self, select, frm, where, group, having): #, orderby, limit):
        self.select  = select   
        self.frm     = frm     
        self.where   = where or _ASTWhere(None)
        self.group   = group   
        self.having  = having  

    def composeQuery(self, query_plan):

        if self.frm:
            self.frm    .composeQuery(query_plan)
        
        if self.where:
            self.where  .composeQuery(query_plan)

        if self.group:
            self.group  .composeQuery(query_plan)
    
        if self.having:
            self.having .composeQuery(query_plan)

        self.select .composeQuery(query_plan)

        return

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class _ASTQuery(ASTQuery):

    def composeQuery(self):

        query_plan = {
            #
            'indexes': [],

            #
            'dsl': { 
                "query": {} 
            },
            
            # Columns
            'columns_processors': []
        }
        
        self.s.composeQuery(query_plan)
        
        if self.o:
            self.o.composeQuery(query_plan)
        
        if self.l:
            self.l.composeQuery(query_plan)
        
        return query_plan

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class ComposerParser(Parser):

    def __init__(self):
        return super().__init__()

    # LITERALS
    
    def createBoolLiteral(self, b):
        return _ASTBoolLiteral(b)
    
    def createStringLiteral(self, s):
        return _ASTStringLiteral(s)

    def createNumericLiteral(self, s):
        return _ASTNumericLiteral(s)

    def createIdentifier(self, s):
        return _ASTIdentifier(s)

    # EXPRESSIONS
        
    def createASTUnaryExpr(self, op, e1):
        return _ASTUnaryExpr(op, e1)
        
    def createBinaryExpr(self, op, e1, e2):
        return _ASTBinaryExpr(op, e1, e2)

    def createASTTernaryExpr(self, op, e1, e2, e3):
        return _ASTTernaryExpr(op, e1, e2, e3)

    def createCall(self, name, params):
        return _ASTCall(name, params)

    def createQueryString(self, s):
        return _ASTQueryString(s)

    # SELECT col.....        

    def createASTSelect(self, col_exprs):
        return _ASTSelect(col_exprs)

    def createASTSelectColumn(self, expr, alias):
        return _ASTSelectColumn(expr, alias)

    # FROM

    def createASTFrom(self, tables):
        return _ASTFrom( tables )

    def createASTTable(self, table, table_alias):
        return _ASTTable(table, table_alias)

    # WHERE

    def createASTWhere(self, expr):
        return _ASTWhere(expr)

    def createOrderTerm(self, expr, direction):
        return _ASTOrderTerm(expr, direction)

    # ORDER

    def createASTOrder(self, expr_list):
        return _ASTOrder(expr_list)

    # GROUP HAVING 

    def createASTGroup(self, expr_list):
        return _ASTGroup(expr_list)
        
    def createASTHaving(self, expr ):
        return _ASTHaving( expr )

    # LIMIT
    
    def createASTLimit(self, expr):
        return _ASTLimit( expr )

    # FULL QUERY
        
    def createSelectBody(self, s,f, w, g, h):
        return _ASTSelectBody(s, f, w, g, h)
    
    def createQuery(self, s, o, l):
        return _ASTQuery(s, o, l)

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

if __name__ == "__main__":
    
    import sys
    import pprint
    
    s = sys.argv[1]
    
    parser = ComposerParser()

    tree = parser.parse(s)
    
    print("-" * 80)
    print("AST STRUCTURE")
    print("-" * 80)

    print(tree)

    print("-" * 80)
    print("query_descriptor")
    print("-" * 80)
    
    query_descriptor = tree.composeQuery()
    
    pprint.pprint(query_descriptor)
    
