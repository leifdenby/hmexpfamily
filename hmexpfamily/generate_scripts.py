import os
import stat
from pathlib import Path

import jinja2
import jinja2.meta
from loguru import logger

from .config import read_config

SCRIPT_TEMPLATES = dict(
    base=[
        "01__base__checkout_and_setup.sh",
        "02__base__config.sh",
        "03__base__run_spinup.sh",
    ]
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


def main():
    config = read_config()
    cwd = Path.cwd()

    for script_kind, templates_filename in SCRIPT_TEMPLATES.items():
        for template_filename in templates_filename:
            template = ENV_TEMPLATES.get_template(f"{script_kind}/{template_filename}")
            template_context = dict(config)
            template_context["cwd"] = cwd
            template_context["file_replacements"] = {
                filename: _render_file_replacements_template(
                    target_filename=filename, replacements=replacements
                )
                for (filename, replacements) in config["base"]["files"].items()
            }

            script_content = template.render(
                **template_context, undefined=jinja2.StrictUndefined
            )

            script_path = Path(cwd) / template_filename
            with open(script_path, "w") as fh:
                fh.write(script_content)

            st = os.stat(template_filename)
            os.chmod(template_filename, st.st_mode | stat.S_IEXEC)
            logger.info(f"Wrote script {template_filename}")


if __name__ == "__main__":
    main()
