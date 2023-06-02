# Checkout Harmonie soure code by adding it as a submodule
git init
git submodule add {{ source.repo }} base
cd base
git checkout {{ source.revision }}
cd -
git add . -m "Use Harmonie revision {{ source.revision }}"
./config-sh/Harmonie setup -r $(pwd) -h {{ platform }}
