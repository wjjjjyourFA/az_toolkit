# az_toolkit/config.py
import os

PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))

GLOBAL_CONFIG = {
    "version": "1.0",
    "author": "HuangWei",
    "debug": False,
    "simple_path": os.path.join(PACKAGE_ROOT, "..", "..", "test_data"),
}


def set_config(**kwargs):
    """
    修改全局配置
    :param kwargs: 要修改的配置项，比如 set_config(debug=False)
    """
    for key, value in kwargs.items():
        if key in GLOBAL_CONFIG:
            GLOBAL_CONFIG[key] = value
        else:
            raise KeyError(f"Invalid config key: {key}")


if __name__ == "__main__":
    print("PACKAGE_ROOT =", PACKAGE_ROOT)
    print("simple_path =", GLOBAL_CONFIG["simple_path"])
