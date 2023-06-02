import os
import stat
from pathlib import Path

import jinja2
import jinja2.meta
from loguru import logger

from .config import read_config

SCRIPT_TEMPLATES = dict(
    base=[
        "01__checkout_and_setup.sh",
        "02__config.sh",
        "03__run_spinup.sh",
    ],
    variant=[
        "01__setup.sh",
    ],
)

ENV_TEMPLATES = jinja2.Environment(
    loader=jinja2.PackageLoader("hmexpfamily"),
    autoescape=jinja2.select_autoescape(),
)

# TODO: rather than blindly use these we should parse the current value and
# check that the `sed` operation works...
DEFAULT_VALUES = {
    "ecf/config_exp.h": dict(DOMAIN="DKCOEXP", CAERO="tegenaod", USEAERO="climaero")
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


def _write_scripts_for_collection(
    template, template_filename, script_kind, collection, config
):
    cwd = Path.cwd()
    template_context = dict(config)
    template_context["cwd"] = cwd

    if collection == "base":
        collection_file_replacements = config[collection].get("files", {})
    else:
        collection_file_replacements = config["variants"][collection].get("files", {})

    template_context["file_replacements"] = {
        filename: _render_file_replacements_template(
            target_filename=filename, replacements=replacements
        )
        for (filename, replacements) in collection_file_replacements.items()
    }

    script_content = template.render(**template_context)

    if collection == "base":
        # hacky, but for the "base" we don't need to add the variant to the filename
        script_identifier = collection
    else:
        script_identifier = f"{script_kind}__{collection}"
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
                collections = ["base"]
            else:
                collections = list(config["variants"].keys())

            for collection in collections:
                _write_scripts_for_collection(
                    template=template,
                    template_filename=template_filename,
                    script_kind=script_kind,
                    collection=collection,
                    config=config,
                )


if __name__ == "__main__":
    main()
