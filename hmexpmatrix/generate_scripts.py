import os
import stat
from pathlib import Path

import jinja2
from loguru import logger

from .config import read_config

SCRIPT_TEMPLATES = dict(
    base=["01__base__checkout_and_setup.sh", "03__base__run_spinup.sh"]
)


def main():
    config = read_config()
    cwd = Path.cwd()

    env_templates = jinja2.Environment(
        loader=jinja2.PackageLoader("hmexpmatrix"),
        autoescape=jinja2.select_autoescape(),
    )

    for script_kind, templates_filename in SCRIPT_TEMPLATES.items():
        for template_filename in templates_filename:
            template = env_templates.get_template(f"{script_kind}/{template_filename}")
            template_context = dict(config)
            template_context["cwd"] = cwd
            script_path = Path(cwd) / template_filename
            with open(script_path, "w") as fh:
                script_content = template.render(**template_context)
                fh.write(script_content)

            st = os.stat(template_filename)
            os.chmod(template_filename, st.st_mode | stat.S_IEXEC)
            logger.info(f"Wrote script {template_filename}")


if __name__ == "__main__":
    main()
