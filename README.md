# :mask: Report Generator for [GAL](https://gal.riodejaneiro.sus.gov.br/) ( SARS-COV-2 )

That project has been developed to support Rio de Janeiro's health professionals to control the data about PCR-RT. Generating reports, getting data, generating knowledge...

## Getting Started

The objective of that project is to generate reports from GAL (Gerenciador de Ambiente Laboratorial - Laboratory Environment Manager) to help control the administration of PCR diagnosis (SWAB).

## Requisites

This project requires only an [Python 3](https://www.python.org/) distribution, the [Urllib3](https://github.com/urllib3/urllib3) and the [requests library](https://docs.python-requests.org/en/master/).

```
* Python 3
* Requests Library
* Urllib3 Library
```

## Examples

This library is very easy to use. First, import the class.
```python
>>> from gal_crawler import get_swab_result
```

After import, the class, initialize with an id array and your GAL's PHPSESSIONID cookie. 

```python
>>> crawler = get_swab_result(["123", "456", "789"], "411SESSIONID389")
```

So, when you want to capture data from the server, call the run method and wait from the end of execution.

```python
>>> crawler.run()
True
```
> Note: That method will return **False** if an error occurred or **True** if run correctly.

After the run, you can save the captured data with the method save_output. That method receive and string which contains the name of the archive. The archive will be exported as .csv.

```python
>>> crawler.save_output("output")
```

The code will look something like this:
```python
>>> from gal_crawler import get_swab_result
>>> crawler = get_swab_result(["123", "456", "789"], "411SESSIONID389")
>>> crawler.run()
>>> crawler.save_output("output")
```

## Notes

- That project is only a beta, not a production project. Please, take care when using that solution.
- That solution has been developed for health professionals and it can expose confidential data from citizens. Please, take careful!
