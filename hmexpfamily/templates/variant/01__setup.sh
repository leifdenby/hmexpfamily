{% with variant_identifier="variant__" + variant.name %}
# Create a directory to store the {{ variant.name }} variant of the
# {{ base.name }} experiment
mkdir {{ variant_identifier }}

# Setup Harmonie in $PERM with this variant experiment by symlinking to the
# base experiment repo
cd {{ variant_identifier }}
ln -sf $PERM/hm_home/{{ base.name }}__base/config-sh/Harmonie
./Harmonie setup -r $PERM/hm_home/{{ base.name }}__base
cd -

# Symlink the variant experiment into hm_home on $SCRATCH where Harmone expects it
# to be
ln -s {{ cwd }}/{{ variant_identifier }} $PERM/hm_home/{{ base.name }}__{{ variant_identifier }}

# Create a symlink in output/{{ variant_identifier }} to where Harmonie will
# place the output for ease of access later
ln -s $SCRATCH/hm_home/{{ base.name }}__{{ variant_identifier }} {{ cwd }}/output/{{ variant_identifier }}

{% endwith %}
