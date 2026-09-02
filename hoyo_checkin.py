import time
import random
import setting
import config
from request import get_new_session
from loghelper import log

RET_CODE_ALREADY_SIGNED_IN = -5003


def get_os_game_nicknames() -> dict:
    """
    获取国际服所有游戏的游戏内昵称
    返回 {game_name: nickname} 字典，例如 {"原神": "荧", "绝区零": "东爱璃Lovely"}
    """
    http = get_new_session()
    cookie_str = config.config.get("games", {}).get("os", {}).get("cookie", "")

    # 从 Cookie 里提取 uid（支持多种字段名）
    uid = ""
    uid_fields = ["ltuid_v2", "ltuid", "account_id", "uid", "stuid"]
    for field in uid_fields:
        for item in cookie_str.split(";"):
            if field in item and "=" in item:
                value = item.split("=", 1)[1].strip()
                if value and value.isdigit():
                    uid = value
                    break
        if uid:
            break

    if not uid:
        log.warning("国际服 Cookie 中未找到 uid，无法获取游戏昵称")
        return {}

    log.info(f"国际服账号 uid：{uid}")

    # 从 Cookie 里提取 device_id（_MHYUUID 字段）
    device_id = ""
    for item in cookie_str.split(";"):
        if "_MHYUUID" in item and "=" in item:
            device_id = item.split("=", 1)[1].strip()
            break

    headers = {
        "Referer": setting.os_referer_url,
        "Origin": "https://www.hoyolab.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Cookie": cookie_str,
        "x-rpc-app_version": "4.13.0",
        "x-rpc-client_type": "4",
        "x-rpc-language": "zh-cn",
        "x-rpc-device_id": device_id,
    }

    nicknames = {}
    try:
        resp = http.get(
            f"https://bbs-api-os.hoyolab.com/game_record/card/wapi/getGameRecordCard?uid={uid}",
            headers=headers
        ).json()
        log.info(f"获取游戏卡片接口返回：retcode={resp.get('retcode')}, message={resp.get('message')}")
        game_list = resp.get("data", {}).get("list", [])
        for game in game_list:
            game_name = game.get("game_name", "")
            nickname = game.get("nickname", "")
            if game_name and nickname:
                nicknames[game_name] = nickname
        log.info(f"获取到的游戏昵称：{nicknames}")
    except Exception as e:
        log.warning(f"获取国际服游戏昵称失败：{str(e)}")
    return nicknames


def hoyo_checkin(event_base_url: str, act_id: str) -> str:
    """
    国际服游戏签到

    :param event_base_url: 基础Url
    :param act_id: 活动id
    :return: 签到结果
    """
    os_lang = config.config["games"]["os"]["lang"]
    reward_url = f"{event_base_url}/home?lang={os_lang}" \
                 f"&act_id={act_id}"
    info_url = f"{event_base_url}/info?lang={os_lang}" \
               f"&act_id={act_id}"
    sign_url = f"{event_base_url}/sign?lang={os_lang}"

    http = get_new_session()

    cookie_str = config.config.get("games", {}).get("os", {}).get("cookie", "")

    headers = {
        "Referer": setting.os_referer_url,
        "Accept-Encoding": "gzip, deflate, br",
        "Cookie": cookie_str,
    }
    if act_id == setting.os_zzz_act_id:
        headers['x-rpc-signgame'] = "zzz"

    info_list = http.get(info_url, headers=headers).json()

    today = info_list.get("data", {}).get("today")
    total_sign_in_day = info_list.get("data", {}).get("total_sign_day")
    already_signed_in = info_list.get("data", {}).get("is_sign")
    first_bind = info_list.get("data", {}).get("first_bind")

    # 提前获取奖励列表（已签到时也要显示今天的奖励）
    awards_data = http.get(reward_url, headers=headers).json()
    awards = awards_data.get("data", {}).get("awards")

    if already_signed_in:
        # 已签到时，也显示连续签到天数和今天的奖励
        if awards and total_sign_in_day > 0:
            reward = awards[total_sign_in_day - 1]
            ret_msg = f"已连续签到 {total_sign_in_day} 天\n今天获得的奖励是「{reward['name']}」x{reward['cnt']}"
        else:
            ret_msg = "今天已经签到过"
        log.info(ret_msg)
        return ret_msg

    if first_bind:
        log.info("请手动签到一次")
        ret_msg = "请手动签到一次"
        return ret_msg

    log.info(f"准备签到：{today} ")

    # a normal human can't instantly click, so we wait a bit
    sleep_time = random.uniform(2.0, 10.0)
    log.debug(f"等待 {sleep_time}")
    time.sleep(sleep_time)

    response = http.post(sign_url, headers=headers, json={"act_id": act_id}).json()

    code = response.get("retcode", 99999)

    log.debug(f"return code {code}")

    if code == RET_CODE_ALREADY_SIGNED_IN:
        if awards and total_sign_in_day > 0:
            reward = awards[total_sign_in_day - 1]
            ret_msg = f"已连续签到 {total_sign_in_day} 天\n今天获得的奖励是「{reward['name']}」x{reward['cnt']}"
        else:
            ret_msg = "今天已经签到过"
        log.info(ret_msg)
        return ret_msg
    elif code != 0:
        log.error(response['message'])
        ret_msg = response['message']
        return ret_msg

    reward = awards[total_sign_in_day]

    log.info("签到成功")
    log.info(f"\t已连续签到 {total_sign_in_day + 1} 天")
    log.info(f"\t今天获得的奖励是：{reward['cnt']}x 「{reward['name']}」")
    ret_msg = f"已连续签到 {total_sign_in_day + 1} 天\n今天获得的奖励是「{reward['name']}」x{reward['cnt']}"
    return ret_msg


def genshin():
    log.info(f"正在进行「原神」签到")
    ret_msg = '原神：\n' + hoyo_checkin("https://sg-hk4e-api.hoyolab.com/event/sol",
                                     setting.os_genshin_act_id)
    return ret_msg


def honkai_sr():
    log.info(f"正在进行「崩坏：星穹铁道」签到")
    ret_msg = '崩坏：星穹铁道：\n' + hoyo_checkin("https://sg-public-api.hoyolab.com/event/luna/os",
                                          setting.os_honkai_sr_act_id)
    return ret_msg


def honkai3rd():
    log.info(f"正在进行「崩坏3」签到")
    ret_msg = '崩坏3：\n' + hoyo_checkin("https://sg-public-api.hoyolab.com/event/mani",
                                      setting.os_honkai3rd_act_id)
    return ret_msg


def tears_of_themis():
    log.info(f"正在进行「未定事件簿」签到")
    ret_msg = '未定事件簿：\n' + hoyo_checkin("https://sg-public-api.hoyolab.com/event/luna/os",
                                        setting.os_tearsofthemis_act_id)
    return ret_msg

def zzz():
    log.info(f"正在进行「绝区零」签到")
    ret_msg = '绝区零：\n' + hoyo_checkin("https://sg-act-nap-api.hoyolab.com/event/luna/zzz/os",
                                      setting.os_zzz_act_id)
    return ret_msg


def run_task():
    ret_msg = ''
    games = config.config['games']['os']

    if games['cookie'] == '':
        log.warning("国际服未配置 Cookie！")
        games['enable'] = False
        config.save_config()
        return ''

    # 获取国际服所有游戏的游戏内昵称
    nickname_dict = get_os_game_nicknames()

    for game, data in games.items():
        if isinstance(data, dict) and data.get('checkin', False):
            try:
                game_result = globals()[game]()
                # 在游戏名后面加上游戏内昵称，比如 "原神（荧）："
                if nickname_dict:
                    for game_name, nickname in nickname_dict.items():
                        prefix = f"{game_name}："
                        if game_result.startswith(prefix):
                            game_result = game_result.replace(
                                prefix, f"{game_name}（{nickname}）：", 1
                            )
                            break
                ret_msg += f"\n\n{game_result}"
            except KeyError:
                pass

    return ret_msg
