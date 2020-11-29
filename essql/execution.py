
import json
import requests

from .composer import ComposerParser

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class Executor(object):

    def __init__(self, base_uri, query_descriptor):

        self.base_uri         = base_uri
        self.query_descriptor = query_descriptor

    def execute(self):
        
        query_descriptor = self.query_descriptor

        
        # Search query
        #
        dsl_obj = query_descriptor['dsl']
        
        
        # Index Name
        index = ','.join( query_descriptor['indexes'] )
        
        # Source fields
        fields = []
        for column_processor in query_descriptor['columns_processors']:
            symbols = column_processor['used_symbols']
            fields.extend(symbols)
            
        
        #
        # PERFORM REQUEST
        #
        
        uri = self.base_uri + '/' + index + '/_search'
    
        response = requests.get(uri, json=dsl_obj)
        
        results = json.loads(response.text)
        
        # FIX: handle errors
        
        results = results['hits']['hits']
    
        #
        # PROCESS RESPONSE
        #            
        
        results = self.process_result(results, query_descriptor)
        
        return results
        

    def compile_expr(self, expr_str):
            return compile( expr_str, '<string>', 'eval')
    
    def evaluate_expr(self, exec_context, expr_str):
            return eval(expr_str, {}, exec_context)
   

    def create_column_expr_contex(self, symbols=None):
    
            context = {
            }
            for symbol in dir(__builtins__):
                    context[ symbol ] = None
            context['abs'   ] = abs
            context['divmod'] = divmod
            context['int'   ] = int
            context['pow'   ] = pow
            context['float' ] = float
            #context['long'  ] = long
            context['max'   ] = max
            context['min'   ] = min
            context['fun1'  ] = lambda n: n * 1.5
            #context['ceil'  ] = math.ceil
            
            #context['log'   ] = math.log
            #context['sqrt'  ] = math.sqrt
            
            #context['sin'   ] = math.sin
            #context['cos'   ] = math.cos
            #context['radians'] = math.radians
            
            #context['iftrue'] = _fun_iftrue
            #context['ifnull'] = _fun_ifnull
            
            #context['NONE'  ] = SafeNoneType()
            #context['None'  ] = SafeNoneType()
            
            #context['sma'  ]  = _fun_sma
            if symbols is not None:
                    context.update(symbols)
            
            return context
            
    def process_result(self, results, query_descriptor):
                
        results2 = []
        
        headers = []
        
        # STEP 1: compile expressions
        for column_processor in query_descriptor['columns_processors']:
                expr_string = column_processor['expr_string']
                #print(expr_string)
                column_processor['compiled_expr'] = self.compile_expr( expr_string  )
                
                headers.append( column_processor['alias'] )
                
        results2.append( headers )
        
        # STEP2: Process data
        c = {}
        column_expr_contex = self.create_column_expr_contex(c)
        
        for row in results:
        
                #print(row)
        
                column_values = []
        
                for colum_num, column_processor in enumerate(query_descriptor['columns_processors']):
        
                                compiled_expr = column_processor['compiled_expr']
                                
                                symbols = column_processor['used_symbols']
        
                                try:
                                        for sym_name in symbols:                                                
                                                v = row['_source'][sym_name]
                                                
                                                column_expr_contex[ sym_name ] = v
                                                
                                        computed_val = self.evaluate_expr(column_expr_contex, compiled_expr)
        
                                except Exception as e:
                                        print(__file__, colum_num, type(e), str(e))
                                        computed_val = None
        
                                column_values.append(computed_val)
        
                results2.append( column_values )
        
        return results2


#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

'''
{'_shards': {'failed': 0, 'skipped': 0, 'successful': 1, 'total': 1},
 'aggregations': {'x': {'buckets': [{'doc_count': 9,
                                     'key': 1000,
                                     'y': {'buckets': [{'doc_count': 3,
                                                        'key': 2000,
                                                        'y': {'avg': 2000.0,
                                                              'count': 3,
                                                              'max': 2000.0,
                                                              'min': 2000.0,
                                                              'sum': 6000.0}},
                                                       {'doc_count': 3,
                                                        'key': 2001,
                                                        'y': {'avg': 2001.0,
                                                              'count': 3,
                                                              'max': 2001.0,
                                                              'min': 2001.0,
                                                              'sum': 6003.0}},
                                                       {'doc_count': 3,
                                                        'key': 2002,
                                                        'y': {'avg': 2002.0,
                                                              'count': 3,
                                                              'max': 2002.0,
                                                              'min': 2002.0,
                                                              'sum': 6006.0}}],
                                           'doc_count_error_upper_bound': 0,
                                           'sum_other_doc_count': 0}},
                                    {'doc_count': 9,

'''


def _process_aggregations(result):

    aggregation_fields = query_descriptor['aggregation_fields']
    
    aggregations = results['aggregations']
    
    def _f(aggr_data, aggr_fields, level=0, field_values=[]):
    
        if level < (len(aggr_fields)):
    
            field_name = aggr_fields[level]
                
            field_data = aggr_data[field_name]
                    
            buckets = field_data['buckets']
            
            table = []
            for b in buckets:
                field_value = b['key']
            
                #print(field_name, field_value)
                
                table += _f(b, aggr_fields, level+1, field_values + [ (field_name, field_value), ] )
    
            return table
    
        else:
            #field_name = aggr_fields[-1]
            
            #stats = aggr_data[ field_name ]
            
            #row = dict( field_values + [ ( field_name + '_' + k, v) for k,v in stats.items() ] )
            
            count = aggr_data['doc_count']
            
            row = dict( field_values + [ ('_count', count) ] )
            
            return [ row ]

    ret = _f(aggregations, aggregation_fields)
