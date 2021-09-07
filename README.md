# CPE guesser

CPE guesser is a web service to guess the CPE name based on one or more keyword(s).  Then the result can
be used against [cve-search](https://github.com/cve-search/cve-search) to do actual searches by CPE names.

## Requirements

- Redis
- Python

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
