from pathlib import Path

import isodate
import jinja2
import rich
import yaml
from loguru import logger

EXPFAMILY_DEFINITION_FILENAME = "expfamily.yaml"
SCRIPT_TEMPLATES = dict(base=["01__base__checkout.sh"])

CONFIG_SCHEMA = dict(
    base=dict(
        name=str,
        platform=str,
        meta=dict(
            start=isodate.parse_datetime,
            end=isodate.parse_datetime,
            spinup=isodate.parse_duration,
            disable_sanidisk=bool,
            write_irridiance_vfld=bool,
        ),
        source=dict(
            repo=str,
            revision=str,
        ),
        files={"ecf/config_exp.h": dict},
    ),
    variants=dict,
)

CONFIG_REQUIRED_VARS = dict(
    base=dict(
        name=True,
        platform=True,
        meta=dict(
            start=True,
            end=True,
            spinup=True,
        ),
        source=dict(
            repo=True,
            revision=True,
        ),
    ),
    variants=True,
)


def _validate_config_node(node, schema, reqd_vars, level=[]):
    level_s = ".".join(level)
    output = {}
    parsed = []
    for (k, v) in schema.items():
        if reqd_vars.get(k) and k not in node:
            raise Exception(f"{k} missing in config (at {level_s})")

        if isinstance(v, dict):
            output[k] = _validate_config_node(
                node[k],
                v,
                reqd_vars.get(k, {}),
                level=level
                + [
                    k,
                ],
            )
        else:
            try:
                output[k] = v(node[k])
            except Exception as ex:
                raise Exception(
                    f"There was an issue parsing value {node[k]} at level {level_s}"
                ) from ex
        parsed.append(k)

    unknown_params = set(node.keys()).difference(parsed)
    if len(unknown_params) > 0:
        raise NotImplementedError(
            f"The following config parameters weren't recognised at level {level_s}"
            f" {', '.join(unknown_params)}"
        )
    return output


def _read_config():
    with open(EXPFAMILY_DEFINITION_FILENAME) as fh:
        config = yaml.load(fh, Loader=yaml.FullLoader)
    logger.info(f"Read config from {EXPFAMILY_DEFINITION_FILENAME}")

    config = _validate_config_node(config, CONFIG_SCHEMA, CONFIG_REQUIRED_VARS)

    return config


def main():
    config = _read_config()
    rich.print(config)
    _ = Path.cwd()

    env_templates = jinja2.Environment(
        loader=jinja2.PackageLoader("hmexpmatrix"),
        autoescape=jinja2.select_autoescape(),
    )

    for script_kind, templates_filename in SCRIPT_TEMPLATES.items():
        for template_filename in templates_filename:
            template = env_templates.get_template(f"{script_kind}/{template_filename}")
            template_context = config[script_kind]
            print(template.render(**template_context))


if __name__ == "__main__":
    main()
