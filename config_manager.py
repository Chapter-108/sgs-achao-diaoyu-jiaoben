from typing import Dict, Any, Tuple
import yaml

from setting import Config


class ConfigManager:
    """配置管理类，处理配置文件与配置档的读写。"""

    @staticmethod
    def write_yaml(data: Dict[str, Any]) -> None:
        Config.GENERATE_DIR.mkdir(exist_ok=True)
        with open(str(Config.CONFIG_FILE), "w", encoding="utf-8") as f:
            yaml.safe_dump(
                ConfigManager._to_yaml_safe_data(data),
                f,
                allow_unicode=True,
                sort_keys=True,
            )

    @staticmethod
    def read_yaml() -> Dict[str, Any]:
        with open(str(Config.CONFIG_FILE), "r", encoding="utf-8") as f:
            content = f.read()
        if not content.strip():
            return {}

        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError:
            data = yaml.load(content, Loader=yaml.FullLoader)
        return data or {}

    @staticmethod
    def read_profiles() -> Dict[str, Dict[str, Any]]:
        default_profiles = {
            "default": {
                "window_title": Config.WINDOW_TITLE,
                "window_size": list(Config.WINDOW_SIZE),
            }
        }

        Config.GENERATE_DIR.mkdir(exist_ok=True)
        if not Config.PROFILES_FILE.exists():
            with open(str(Config.PROFILES_FILE), "w", encoding="utf-8") as f:
                yaml.safe_dump(default_profiles, f, allow_unicode=True, sort_keys=True)
            return default_profiles

        with open(str(Config.PROFILES_FILE), "r", encoding="utf-8") as f:
            content = f.read()
        if not content.strip():
            return default_profiles

        data = yaml.safe_load(content) or {}
        if not isinstance(data, dict):
            raise ValueError("profiles.yaml 格式错误，顶层必须是对象映射")
        return data

    @staticmethod
    def write_profiles(profiles: Dict[str, Dict[str, Any]]) -> None:
        Config.GENERATE_DIR.mkdir(exist_ok=True)
        with open(str(Config.PROFILES_FILE), "w", encoding="utf-8") as f:
            yaml.safe_dump(
                ConfigManager._to_yaml_safe_data(profiles),
                f,
                allow_unicode=True,
                sort_keys=True,
            )

    @staticmethod
    def save_profile(
        profile_name: str,
        window_title: str,
        window_size: Tuple[int, int, int, int],
    ) -> None:
        if not profile_name.strip():
            raise ValueError("配置名称不能为空")
        profiles = ConfigManager.read_profiles()
        profiles[profile_name] = {
            "window_title": window_title,
            "window_size": list(window_size),
        }
        ConfigManager.write_profiles(profiles)

    @staticmethod
    def _to_yaml_safe_data(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: ConfigManager._to_yaml_safe_data(v) for k, v in obj.items()}
        if isinstance(obj, tuple):
            return [ConfigManager._to_yaml_safe_data(v) for v in obj]
        if isinstance(obj, list):
            return [ConfigManager._to_yaml_safe_data(v) for v in obj]
        return obj
