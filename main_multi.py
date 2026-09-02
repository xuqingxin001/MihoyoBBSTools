import os
import sys
import main
import time
import push
import config
import random
from loghelper import log
from error import CookieError, StokenError


def find_config(ext: str) -> list:
    """
    搜索指定扩展名的配置文件
    """
    file_name = []
    for files in os.listdir(config.path):
        if os.path.splitext(files)[1] == ext:
            if config.config_prefix == "" or files.startswith(config.config_prefix):
                file_name.append(files)
    return file_name


def ql_config(config_list: list) -> list:
    """
    筛选青龙多用户配置文件（头部匹配）
    """
    config_list_ql = []
    for files in config_list:
        if 'mhy_' == files[:4]:
            config_list_ql.append(files)
    return config_list_ql


def get_config_list() -> list:
    """
    获取所有可用的配置文件列表
    """
    config_list = find_config('.yaml')
    config_list.extend(find_config('.yml'))
    config_prefix = os.getenv("AutoMihoyoBBS_config_prefix")
    config_multi = os.getenv("AutoMihoyoBBS_config_multi", "0")
    ql_dir = os.getenv("QL_DIR")

    if config_prefix is None and config_multi == '1':
        if ql_dir is not None:
            config_list = ql_config(config_list)
    if len(config_list) == 0:
        log.warning("未检测到配置文件，请确认 config 文件夹存在 .yaml/.yml 后缀名的配置文件！")
        exit(1)
    return config_list


def main_multi(autorun: bool) -> tuple:
    """
    多用户模式主执行函数
    """
    log.info("AutoMihoyoBBS Multi User mode")
    log.info("正在搜索配置文件！")
    config_list = get_config_list()
    if autorun:
        log.info(f"已搜索到 {len(config_list)} 个配置文件，正在开始执行！")
    else:
        log.info(f"已搜索到 {len(config_list)} 个配置文件，请确认是否无多余文件！\r\n{config_list}")
        try:
            input("请输入回车继续，需要重新搜索配置文件请 Ctrl+C 退出脚本")
        except KeyboardInterrupt:
            exit(0)

    # 新增 detail 字段，保存每个配置文件的详细执行结果
    results = {"ok": [], "close": [], "error": [], "captcha": [], "detail": {}}

    for i in config_list:
        log.info(f"正在执行 {i}")
        config.config_Path = os.path.join(config.path, i)
        try:
            run_code, run_message = main.main()
        except (CookieError, StokenError) as e:
            results["error"].append(i)
            # 出错时也记录详细信息
            results["detail"][i] = "账号 Cookie/Stoken 出错，未执行具体任务"
            if config.config.get("push", "") != "":
                push_handler = push.PushHandler(config.config["push"])
                error_msg = "账号 Cookie 出错！" if isinstance(e, CookieError) else "账号 Stoken 有问题！"
                push_handler.push(1, error_msg)
        else:
            # 保存每个配置文件的详细执行结果
            results["detail"][i] = run_message

            if run_code == 0:
                results["ok"].append(i)
            elif run_code == 1 or run_code == 2:
                results["error"].append(i)
            elif run_code == 3:
                results["captcha"].append(i)
            else:
                results["close"].append(i)
        log.info(f"{i} 执行完毕")

        time.sleep(random.randint(3, 10))
    print("")

    # 配置文件只显示名字（去掉.yaml/.yml后缀），用顿号分隔
    def format_config_names(name_list):
        if not name_list:
            return "无"
        names = [os.path.splitext(n)[0] for n in name_list]
        return "、".join(names)

    # 分类收集国服和国际服结果（配置文件只显示名字，不带后缀）
    cn_results = []
    os_results = []

    for config_name, detail_msg in results["detail"].items():
        if not detail_msg or not detail_msg.strip():
            continue
        # 配置文件只显示名字（去掉.yaml/.yml后缀）
        short_name = os.path.splitext(config_name)[0]
        if "海外版：" in detail_msg:
            # 同时包含国服和国际服，按前缀拆分
            parts = detail_msg.split("海外版：", 1)
            cn_part = parts[0].strip()
            os_part = parts[1].strip() if len(parts) > 1 else ""
            if cn_part:
                cn_results.append(f"【{short_name}】\r\n{cn_part}")
            if os_part:
                os_results.append(f"【{short_name}】\r\n{os_part}")
        else:
            # 纯国服内容
            cn_results.append(f"【{short_name}】\r\n{detail_msg.strip()}")

    # 构建推送消息
    push_message = f'脚本执行完毕，共执行{len(config_list)}个配置文件，成功{len(results["ok"])}个，' \
                   f'没执行{len(results["close"])}个，失败{len(results["error"])}个' \
                   f'\r\n没执行的配置文件：{format_config_names(results["close"])}' \
                   f'\r\n执行失败的配置文件：{format_config_names(results["error"])}' \
                   f'\r\n触发游戏签到验证码的配置文件：{format_config_names(results["captcha"])}'

    if cn_results:
        push_message += f'\r\n\r\n===== 国服 =====\r\n\r\n' + "\r\n\r\n".join(cn_results)
    if os_results:
        push_message += f'\r\n\r\n===== 国际服 =====\r\n\r\n' + "\r\n\r\n".join(os_results)

    log.info(push_message)

    status = 0
    if len(results["error"]) == len(config_list):
        status = 1
    elif len(results["error"]) != 0:
        status = 2
    elif len(results["captcha"]) != 0:
        status = 3

    return status, push_message


if __name__ == "__main__":
    if (len(sys.argv) >= 2 and sys.argv[1] == "autorun") or os.getenv("AutoMihoyoBBS_autorun") == "1":
        autorun_flag = True
    else:
        autorun_flag = False
    task_status, task_push_message = main_multi(autorun_flag)
    push_handler = push.PushHandler()
    push_handler.push(task_status, task_push_message)
    exit(0)
