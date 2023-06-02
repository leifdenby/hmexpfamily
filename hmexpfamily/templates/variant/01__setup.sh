{% with variant_identifier="variant__" + variant.name %}
mkdir {{ variant_identifier }}

# Symlink the "variant" experiment into hm_home on $SCRATCH where Harmone expects it
# to be
ln -s {{ cwd }}/{{ variant_identifier }} $PERM/hm_home/{{ base.name }}__{{ variant_identifier }}

## Create a symlink to where Harmonie will place the output
ln -s $SCRATCH/hm_home/{{ base.name }}__{{ variant_identifier }} {{ cwd }}/output/{{ variant_identifier }}

{% endwith %}
