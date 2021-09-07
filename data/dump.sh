#!/bin/sh

wget https://nvd.nist.gov/feeds/xml/cpe/dictionary/official-cpe-dictionary_v2.3.xml.gz
gzip -d official-cpe-dictionary_v2.3.xml.gz
