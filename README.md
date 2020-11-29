
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
       x                     AS Xz,
       fun1(z)               AS Z,
       int(log.level.descr)  AS log1
  FROM
       "test-index"
 WHERE
       QUERYSTRING `  x:>1000  AND  log.level.descr:3  `
ORDER BY
       z DESC,
       x ASC

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
