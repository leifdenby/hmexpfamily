cd base/
{% for filename, replacement_instructions in file_replacements.items() %}
## Apply file replacements for {{ filename }}
{{ replacement_instructions }}
{% endfor %}
cd -
