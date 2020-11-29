
if __name__ == "__main__":

    import sys
    import pprint

    from essql.composer import ComposerParser
    from essql.execution import Executor

    s = sys.argv[1]
    
    base_uri = 'http://127.0.0.1:9200/'
    
    
    parser = ComposerParser()

    tree = parser.parse(s)

    query_descriptor = tree.composeQuery()
    
    executor = Executor(base_uri, query_descriptor)

    data = executor.execute()

    pprint.pprint(data)
