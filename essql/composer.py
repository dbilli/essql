
from .parser import *

#----------------------------------------------------------------------#
# Literals                                                             #
#----------------------------------------------------------------------#

def EXPR_INFO_DATA():

    return  {
        'used_symbols'       : [],
        'used_aggr_functions': [],
        'expr'               : None,
        'expr_python'        : None,
        #'expr_literal'       : None,
        'alias'              : None,
    }

class _ASTNumericLiteral(ASTNumericLiteral):

    def composeExpr(self, expr_info):
        expr_info['expr'       ] = [ str(self.value)  ]        
        expr_info['expr_python'] = [ repr(self.value) ]
        

class _ASTStringLiteral(ASTStringLiteral):

    def composeExpr(self, expr_info):
        expr_info['expr'       ] = [ str(self.value)  ]        
        expr_info['expr_python'] = [ repr(self.value) ]

class _ASTBoolLiteral(ASTBoolLiteral):

    def composeExpr(self, expr_info):
        expr_info['expr'       ] = [ str(self.value)  ]        
        expr_info['expr_python'] = [ repr(self.value) ]
    
class _ASTIdentifier(ASTIdentifier):

    def composeExpr(self, expr_info):
        
        sym_name = self.value
        sym_name = sym_name.split(".")[0]
        
        if sym_name != '*':
            expr_info['used_symbols'].append(sym_name)
        
        expr        = []
        expr_python = []
        
        for i, key in enumerate(self.value.split('.')):
            
            
            
            if i == 0:
                expr.append(key)
                expr_python.append(key)
            else:
                expr       .append( '.%s'    % (key) )
                expr_python.append( "['%s']" % (key) )
        
        print(__file__, '_ASTIdentifier', expr, expr_python)
        
        expr_info['expr'       ] = expr
        expr_info['expr_python'] = expr_python

#----------------------------------------------------------------------#
# Expressions                                                          #
#----------------------------------------------------------------------#

class _ASTUnaryExpr(ASTUnaryExpr):

    def composeExpr(self, expr_info):
        self.expr1.composeExpr(expr_info)

        expr_info['expr'       ] = ['(', self.op, expr_info['expr'       ], ')' ]
        expr_info['expr_python'] = ['(', self.op, expr_info['expr_python'], ')' ]

class _ASTBinaryExpr(ASTBinaryExpr):

    def composeExpr(self, expr_info):

        self.expr1.composeExpr(expr_info)        
        expr1         = expr_info['expr']
        expr_python1  = expr_info['expr_python']
        
        self.expr2.composeExpr(expr_info)
        expr2         = expr_info['expr']
        expr_python2  = expr_info['expr_python']

        #
        # Create structure
        #

        expr_info['expr'       ] = ['(', ] + expr1        + [ self.op ] + expr2        + [ ')' ]
        expr_info['expr_python'] = ['(', ] + expr_python1 + [ self.op ] + expr_python2 + [ ')' ]

class _ASTTernaryExpr(ASTTernaryExpr):

    def composeExpr(self, expr_info):
        self.expr1.composeExpr(expr_info)
        self.expr2.composeExpr(expr_info)
        self.expr3.composeExpr(expr_info)

class _ASTCall(ASTCall):

    def composeExpr(self, expr_info):

        fun_name = self.identifier.value
        
        is_aggr_function = fun_name.upper() in ['MAX','MIN','AVG','COUNT','SUM']
        
        #
        #
        #
        params_exprs = []

        for param_expr in self.params:
            
            # Analyze expression   
            expr_info['expr'       ] = None
            expr_info['expr_python'] = None
            param_expr.composeExpr(expr_info)
        
            params_exprs.append( (expr_info['expr'], expr_info['expr_python']) )
            
            # Get informations about aggregation function used
            if is_aggr_function:
                column_name = expr_info['expr'][0]
                expr_string = '%s(%s)' % (fun_name, column_name)
                
                expr_info['used_aggr_functions'].append( (fun_name, expr_string, column_name)  )

        #
        # Create structure
        #
        expr        = [ '(', fun_name, '(' ]
        expr_python = [ '(', fun_name, '(' ]
         
        print(__file__, "XXXX", params_exprs)
        
        if not is_aggr_function:
            for i, pe in enumerate(params_exprs):
                
                e  = pe[0]
                pe = pe[1]
     
                expr       .extend(e)
                expr_python.extend(pe)
                
                if i < len(params_exprs) - 1:
                    expr       .append(',')
                    expr_python.append(',')
        else:
            col_expr, col_expr_python = params_exprs[0]
            
            print(__file__, "Y", col_expr, col_expr_python)
            
            expr       .append( "%s"   % (col_expr[0]       ) )
            expr_python.append( "'%s'" % (col_expr_python[0]) )
            
        expr        += [ ')', ')' ]
        expr_python += [ ')', ')' ]
        
        expr_info['expr'       ] = expr
        expr_info['expr_python'] = expr_python


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
        

        expr_info = EXPR_INFO_DATA()
        
        self.expr.composeExpr(expr_info)
        
        print(expr_info)
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
        expr_info['expr'        ] = ''.join(  expr_info['expr'] )
        expr_info['expr_python' ] = ''.join(  expr_info['expr_python'] )
        #expr_info['expr_literal'] = ''.join(  expr_info['expr_literal'] )
        
        
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

        aggs_body['aggs'] = {}
        
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
        aggs_body['aggs'][ counters_name ] = field_aggr_body


        
        for col_info in query_plan['columns_processors']:
            
            for fun_name, expr_str, col_name,  in col_info['used_aggr_functions']:

                field_aggr_body = {}
                field_aggr_body[ fun_name ] =  { 
                    "field": col_name 
                }
                exprid = expr_str #"stats(%s)" % (field_name)
                aggs_body['aggs'][ exprid ] = field_aggr_body
  
  
  
                    #b_filter = {}
                    #
                    #script_expr = having_expr.replace( expr_str, 'params.val')
                    #
                    #b_filter = {
                    #    "bucket_selector": {
                    #        "buckets_path": {
                    #            "val": exprid
                    #        },
                    #        "script": script_expr
                    #    }
                    #}
                    #
                    #aggs_body['aggs'][ "%s_filter" % (expr_str) ] = b_filter


   
        if 'having_conditions' in query_plan:


            for having_condition in query_plan['having_conditions']:
                print( having_condition )
                
                having_expr = having_condition['expr']
                
                for fun_name, expr_str, col_name,  in having_condition['used_aggr_functions']:

                    field_aggr_body = {}
                    field_aggr_body[ fun_name ] =  { 
                        "field": col_name 
                    }
                    exprid = expr_str #"stats(%s)" % (field_name)
                    aggs_body['aggs'][ exprid ] = field_aggr_body
  
  
  
                    b_filter = {}
                    
                    script_expr = having_expr.replace( expr_str, 'params.val')
                    
                    b_filter = {
                        "bucket_selector": {
                            "buckets_path": {
                                "val": exprid
                            },
                            "script": script_expr
                        }
                    }
                    
                    aggs_body['aggs'][ "%s_filter" % (expr_str) ] = b_filter
                    


        dsl_obj.update( root_body )
        
        #dsl_obj['size'] = 0


class _ASTHaving(ASTHaving):

    def composeQuery(self, query_plan):

        having_conditions = []

        
        
        for having_expr in self.exprs:
            
            expr_info = EXPR_INFO_DATA()
            
            print(__file__, "Z", expr_info)
            
            having_expr.composeExpr(expr_info)

            expr_info['expr']        = ''.join(  expr_info['expr'] )
            expr_info['expr_python'] = ''.join(  expr_info['expr_python'] )
           
            having_conditions.append( expr_info )
        
        query_plan['having_conditions'] = having_conditions

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

        self.select .composeQuery(query_plan)

        if self.frm:
            self.frm    .composeQuery(query_plan)
        
        if self.where:
            self.where  .composeQuery(query_plan)

        if self.having:
            self.having .composeQuery(query_plan)

        if self.group:
            self.group  .composeQuery(query_plan)
    


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
    
    print(sys.argv)
    
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
    
