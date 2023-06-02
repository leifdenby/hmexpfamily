import pyyaml

EXPFAMILY_DEFINITION_FILENAME = "expfamily.yaml"


def _read_config():
    with open(EXPFAMILY_DEFINITION_FILENAME) as fh:
        return pyyaml.read(fh)


def main():
    _ = _read_config()


if __name__ == "__main__":
    main()
