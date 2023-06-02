cd $PERM/{{ name }}__base
{% with spinup_start=base.meta.start_datetime-base.meta.spinup_duration %}
# launch a cold-start run as the spin-up simulation
./Harmonie start DTG={{ spinup_start.strftime('%Y%m%d%H') }} DTGEND={{ base.meta.start_datetime.strftime("%Y%m%d%H") }}
{% endwith %}
