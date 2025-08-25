import os
import json
import yaml

def deep_merge(dict1: dict, dict2: dict) -> dict:
    """递归合并两个字典，后者中的值会覆盖前者中的同名键值"""
    result = dict1.copy()
    for key, value in dict2.items():
        if (key in result and 
            isinstance(result[key], dict) and 
            isinstance(value, dict)):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

if __name__ == '__main__':
    if os.getenv('GITHUB_ACTIONS') == 'true':
        profiles = json.loads(os.getenv('profiles'))
    else:
        with open('config/profiles.json', 'r', encoding='utf-8') as f:
            profiles = json.load(f)

    with open('config/config.yaml.default', 'r', encoding='utf-8') as f:
        config_default = yaml.load(f, Loader=yaml.FullLoader)

    # 生成配置文件
    for profile in profiles:
        config = config_default.copy()

        config['account']['cookie'] = profile['cookie']
        config['account']['stoken'] = profile['stoken']

        if 'config' in profile:
            config = deep_merge(config, profile['config'])

        with open(f'config/{profile["name"]}.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True)

    try:
        # 运行主脚本
        os.system('python main_multi.py autorun')
    finally:
        # 删除配置文件
        for profile in profiles:
            os.remove(f'config/{profile["name"]}.yaml')