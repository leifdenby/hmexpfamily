import isodate
import yaml
from loguru import logger

EXPFAMILY_DEFINITION_FILENAME = "expfamily.yaml"


def _validate_name(s):
    if sum(not c.isalnum() and not c == "_" for c in s) > 0:
        raise Exception(
            "Only alphanumeric characters and undescores are allowed "
            f"in experiment identifiers (`{s}` cannot be used)"
        )
    return s


CONFIG_SCHEMA = dict(
    base=dict(
        name=_validate_name,
        platform=str,
        meta=dict(
            start_datetime=isodate.parse_datetime,
            end_datetime=isodate.parse_datetime,
            spinup_duration=isodate.parse_duration,
            disable_sanidisk=bool,
            write_irridiance_vfld=bool,
        ),
        source=dict(
            repo=str,
            revision=str,
        ),
        files={"ecf/config_exp.h": dict, "scr/Fldextr": dict, "Env_system": dict},
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

        if k in node:
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


def read_config(raw=False):
    with open(EXPFAMILY_DEFINITION_FILENAME) as fh:
        if raw:
            return fh.read()
        config = yaml.load(fh, Loader=yaml.FullLoader)
    logger.info(f"Read config from {EXPFAMILY_DEFINITION_FILENAME}")

    config = _validate_config_node(config, CONFIG_SCHEMA, CONFIG_REQUIRED_VARS)

    for variant_name in config.get("variants", {}).keys():
        _validate_name(variant_name)

    return config
