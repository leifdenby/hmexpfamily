# Checkout a specific revision of Harmonie soure code by adding it as a
# submodule
git init
git submodule add {{ base.source.repo }} base
cd base
git checkout {{ base.source.revision }} -b {{ base.name }}
cd -

# Add a commit to the experiment family repo to registered that we're using
# this commit
git add .
git commit -m "Use Harmonie revision {{ base.source.revision }}"

# Symlink the "base" experiment into hm_home on $PERM where Harmone expects it
# to be
ln -s {{ cwd }}/base $PERM/hm_home/{{ base.name }}__base

## Create a symlink to where Harmonie will replace the output
mkdir -p output/
ln -s $SCRATCH/hm_home/{{ base.name }}__base {{ cwd }}/output/base

# And run setup for Harmonie
cd $PERM/hm_home/{{ base.name }}__base
./config-sh/Harmonie setup -r $(pwd) -h {{ base.platform }}
cd -
