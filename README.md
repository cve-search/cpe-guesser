# CPE guesser

CPE guesser is a command-line or web service to guess the CPE name based on one or more keyword(s).  Then the result can
be used against [cve-search](https://github.com/cve-search/cve-search) to do actual searches by CPE names.

## Requirements

- Redis
- Python

## Usage

To use CPE guesser, you have to initialise the Redis database with `import.py`. Then you can use
the software with `lookup.py` to find the most probable CPE matching the keywords provided.

### Installation

- `git clone https://github.com/cve-search/cpe-guesser.git`
- `cd cpe-guesser/bin`
- Download the CPE dictionary & populate the database with `python3 ./import.py`.
- Take a cup of black or green tea.
- `python3 cpe-guesser/bin/server.py` to run the local HTTP server.

If you don't want to install it locally, there is a public online version. Check below. 

## Public online version

[cpe-guesser.cve-search.org](https://cpe-guesser.cve-search.org) is public online version of CPE guesser which can be used via
a simple API. The endpoint is `/search` and the JSON is composed of a query list with the list of keyword(s) to search for.


~~~~
curl -s -X POST https://cpe-guesser.cve-search.org/search -d "{\"query\": [\"outlook\", \"connector\"]}" | jq .
[
  [
    18117,
    "cpe:2.3:a:microsoft:outlook_connector"
  ],
  [
    60947,
    "cpe:2.3:a:oracle:oracle_communications_unified_communications_suite_connector_for_microsoft_outlook"
  ],
  [
    68306,
    "cpe:2.3:a:oracle:corporate_time_outlook_connector"
  ]
]
~~~~

### Command line - `lookup.py`

~~~~
usage: lookup.py [-h] [--word WORD]

Find potential CPE names from a list of keyword(s) and return a JSON of the results

optional arguments:
  -h, --help   show this help message and exit
  --word WORD  One or more keyword(s) to lookup
~~~~


~~~~
python3 lookup.py  --word microsoft --word sql --word server | jq .
[
  [
    51076,
    "cpe:2.3:a:microsoft:sql_server_2017_reporting_services"
  ],
  [
    51077,
    "cpe:2.3:a:microsoft:sql_server_2019_reporting_services"
  ],
  [
    57612,
    "cpe:2.3:a:quest:intrust_knowledge_pack_for_microsoft_sql_server"
  ],
  [
    60090,
    "cpe:2.3:o:microsoft:sql_server"
  ],
  [
    60660,
    "cpe:2.3:a:microsoft:sql_server_desktop_engine"
  ],
  [
    64489,
    "cpe:2.3:a:microsoft:sql_server_reporting_services"
  ],
  [
    75465,
    "cpe:2.3:a:microsoft:sql_server_management_studio"
  ],
  [
    77161,
    "cpe:2.3:a:microsoft:sql_server"
  ],
  [
    77793,
    "cpe:2.3:a:ibm:tivoli_storage_manager_for_databases_data_protection_for_microsoft_sql_server"
  ]
]
~~~~

## How does this work?

A CPE entry is composed of a human readable name with some references and the structured CPE name.

~~~
  <cpe-item name="cpe:/a:10web:form_maker:1.7.17::~~~wordpress~~">
    <title xml:lang="en-US">10web Form Maker 1.7.17 for WordPress</title>
    <references>
      <reference href="https://wordpress.org/plugins/form-maker/#developers">Change Log</reference>
    </references>
    <cpe-23:cpe23-item name="cpe:2.3:a:10web:form_maker:1.7.17:*:*:*:*:wordpress:*:*"/>
  </cpe-item>
~~~

The CPE name is structured with a vendor name, a product name and some additional information.
CPE name can be easily changed due to vendor name or product name changes, some vendor/product are
sharing common names or name is composed of multiple words.


### Data

Split vendor name and product name (such as `_`) into single word(s) and then canonize the word. Building an inverse index using
the cpe vendor:product format as value and the canonized word as key.  Then cpe guesser creates a ranked set with the most common 
cpe (vendor:product)  per version to give a probability of the CPE appearance.

### Redis structure

- `w:<word>` set
- `s:<word>` sorted set with a score depending of the number of appearance

# License

Software is open source and released under a 2-Clause BSD License

Copyright (C) 2021 Alexandre Dulaunoy  
Copyright (C) 2021 Esa Jokinen  
