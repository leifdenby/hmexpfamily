{% for (key, new_value) in replacements.items() %}{% with default_value=default_values[key] %}
# {{ key }}: {{ default_value }} -> {{ new_value }}
sed -i 's/^{{ key }}={{ default_value }}/{{ key }}={{ new_value }}/' {{ target_filename }}
{% endwith %}{% endfor %}
