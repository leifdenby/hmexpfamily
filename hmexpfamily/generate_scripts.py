import datetime
import os
import stat
from pathlib import Path

import jinja2
import jinja2.meta
from loguru import logger

from . import __version__
from .config import read_config

SCRIPT_TEMPLATES = dict(
    base=[
        "01__checkout_and_setup.sh",
        "02__config.sh",
        "03__run_spinup.sh",
    ],
    variant=[
        "01__setup.sh",
        "02__config.sh",
    ],
)

ENV_TEMPLATES = jinja2.Environment(
    loader=jinja2.PackageLoader("hmexpfamily"),
    autoescape=jinja2.select_autoescape(),
)

# TODO: rather than blindly use these we should parse the current value and
# check that the `sed` operation works...
DEFAULT_VALUES = {
    "ecf/config_exp.h": dict(DOMAIN="DKCOEXP", CAERO="tegenaod", USEAERO="climaero"),
    "Env_system": dict(CLEANING_LEVEL="fast"),
    "scr/Fldextr": dict(lprintrad="F"),
}


def _render_file_replacements_template(target_filename, replacements):
    default_values = DEFAULT_VALUES[target_filename]

    missing_default_values = set(replacements.keys()).difference(default_values.keys())
    if len(missing_default_values) > 0:
        raise NotImplementedError(
            f"Missing default values for file {target_filename} for the "
            f"following parameters: {', '.join(missing_default_values)}"
        )

    replacements = {k: v for (k, v) in replacements.items() if default_values[k] != v}

    template = ENV_TEMPLATES.get_template(f"file_replacements/{target_filename}")
    template_context = dict(
        default_values=default_values,
        replacements=replacements,
        target_filename=target_filename,
    )

    return template.render(**template_context)


def _render_header():
    header_template = ENV_TEMPLATES.get_template("common_header")
    config_yaml = read_config(raw=True)
    config_yaml = "# ---\n# " + "\n# ".join(config_yaml.splitlines()) + "\n# ---"
    header_content = header_template.render(
        t_now=datetime.datetime.now(),
        hmexpfamily_version=__version__,
        config_yaml=config_yaml,
    )

    return header_content


def _write_scripts_for_experiment(
    template, template_filename, script_kind, global_config, variant_name=None
):
    cwd = Path.cwd()
    template_context = dict(base=global_config["base"])
    if variant_name is not None:
        template_context["variant"] = dict(global_config["variants"][variant_name])
        template_context["variant"]["name"] = variant_name

    experiment_file_replacements = template_context[script_kind].get("files", {})

    template_context["cwd"] = cwd

    template_context["file_replacements"] = {
        filename: _render_file_replacements_template(
            target_filename=filename, replacements=replacements
        )
        for (filename, replacements) in experiment_file_replacements.items()
    }

    script_content = template.render(**template_context)

    header_content = _render_header()
    script_content = "\n\n".join([header_content, script_content])

    if variant_name is None:
        script_identifier = "base"
    else:
        script_identifier = f"variant__{variant_name}"
    script_filename = f"{script_identifier}__{template_filename}"

    script_path = Path(cwd) / script_filename
    with open(script_path, "w") as fh:
        fh.write(script_content)

    st = os.stat(script_path)
    os.chmod(script_filename, st.st_mode | stat.S_IEXEC)
    logger.info(f"Wrote script {script_filename}")


def main():
    config = read_config()
    for script_kind, templates_filename in SCRIPT_TEMPLATES.items():
        for template_filename in templates_filename:
            template = ENV_TEMPLATES.get_template(f"{script_kind}/{template_filename}")

            if script_kind == "base":
                variant_names = [None]
            else:
                variant_names = list(config["variants"].keys())

            for variant_name in variant_names:
                _write_scripts_for_experiment(
                    template=template,
                    template_filename=template_filename,
                    script_kind=script_kind,
                    variant_name=variant_name,
                    global_config=config,
                )


if __name__ == "__main__":
    main()
