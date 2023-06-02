# commit current experiment family setup
cd base/
git add .
git commit -m 'commit changes to base'
git push origin {{ base.name }}
cd -
git add *.sh expfamily.yaml base output
git commit -m 'about to run experiment'

# launch a cold-start run as the spin-up simulation from $PERM where Harmonie
# expects it
cd $PERM/hm_home/{{ base.name }}__base
{% with spinup_start=base.meta.start_datetime-base.meta.spinup_duration %}
./config-sh/Harmonie start DTG={{ spinup_start.strftime('%Y%m%d%H') }} DTGEND={{ base.meta.start_datetime.strftime("%Y%m%d%H") }}
{% endwith %}
cd -
