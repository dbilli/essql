
# essql

Perform SQL queries against ElasticSearch.

1. [Introduction](#introduction)
2. [Examples](#examples)


## 1. Introduction<a name="introduction"></a>

ESSQL can perform queries against Elasticsearch indices and return results in tabular format by using a custom SQL dialect.

**NOTE**: ESSQL is not compatible with the SQL dialect provided by the X-Pack for ElasticSearch.


## 2. Examples<a name="examples"></a>

### 2.1. Query example

```
SELECT
       fun1(x)               AS fun_x,
       y,
       sum(x)                AS SUM
  FROM
       "test-index"
 WHERE
       QUERYSTRING `  x:>1000  AND  log.level.descr:3  `
GROUP BY
       x,y
HAVING 
       SUM(z) > 100
ORDER BY
       x, y DESC

LIMIT 10000
```

### 2.2. Test example

```
python -m 'essql.tests.test' 'SELECT x,y,z,log.level WHERE QUERYSTRING `x:>=1003 and y:<1002` '
```

## Authors

* **Diego Billi**

## License

This project is licensed under the GNUv3 License - see the [LICENSE](LICENSE) file for details
