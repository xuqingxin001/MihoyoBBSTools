import random
import time

import tools
import config
import setting
from request import http
from loghelper import log


class CloudGameBase:
    def __init__(self, game_name, sign_url, coin_name, clear_cookie_func) -> None:
        self.headers = {}
        self.game_name = game_name
        self.sign_url = sign_url
        self.coin_name = coin_name
        self.clear_cookie_func = clear_cookie_func

    def sign_account(self) -> str:
        log.info(f"{self.game_name}:")
        ret_msg = f"{self.game_name}:\r\n"
        
        try:
            req = http.get(url=self.sign_url, headers=self.headers)
            data = req.json()

            if data['retcode'] == 0:
                free_time_data = data["data"]["free_time"]
                free_time = int(free_time_data["free_time"])
                send_free_time = int(free_time_data["send_freetime"])

                if send_free_time > 0:
                    log.info(f'签到成功，已获得 {send_free_time} 分钟免费时长')
                    ret_msg += f'签到成功，已获得 {send_free_time} 分钟免费时长\n'
                else:
                    if free_time < 600:
                        time.sleep(random.randint(3, 6))
                        data2 = http.get(url=self.sign_url, headers=self.headers).json()
                        free_time2 = int(data2["data"]["free_time"]["free_time"])
                        if free_time2 > free_time:
                            get_free_time = free_time2 - free_time
                            log.info(f'签到成功，已获得 {get_free_time} 分钟免费时长')
                            ret_msg += f'签到成功，已获得 {get_free_time} 分钟免费时长\n'
                        else:
                            log.info('签到失败，未获得免费时长，可能是已经签到过了或者超出免费时长上限')
                            ret_msg += '签到失败，未获得免费时长，可能是已经签到过了或者超出免费时长上限\n'
                ret_msg += f'你当前拥有免费时长 {tools.time_conversion(int(data["data"]["free_time"]["free_time"]))}，' \
                           f'畅玩卡状态为 {data["data"]["play_card"]["short_msg"]}，拥有{self.coin_name} {data["data"]["coin"]["coin_num"]} 枚'
                log.info(ret_msg)
            elif data['retcode'] == -100:
                ret_msg += f"token 失效/防沉迷"
                log.warning(ret_msg)
                self.clear_cookie_func()
            else:
                ret_msg += f'脚本签到失败，json 文本：{req.text}'
                log.warning(ret_msg)
        except Exception as e:
            log.error(f'{self.game_name} 签到异常：{str(e)}')
            ret_msg += '脚本签到发生异常，请查看日志'
        
        return ret_msg


class CloudGenshin(CloudGameBase):
    def __init__(self, token) -> None:
        super().__init__("云原神", setting.cloud_genshin_sgin, "米云币", config.clear_cookie_cloudgame_genshin)
        self.headers = {
            'Host': 'api-cloudgame.mihoyo.com',
            'Accept': '*/*',
            'Referer': 'https://app.mihoyo.com',
            'x-rpc-combo_token': token,
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/99.0.4844.84 Safari/537.36',
        }


class CloudZZZ(CloudGameBase):
    def __init__(self, token) -> None:
        super().__init__("云绝区零", setting.cloud_zzz_sgin, "邦邦点", config.clear_cookie_cloudgame_zzz)
        self.headers = {
            'Host': 'cg-nap-api.mihoyo.com',
            'Accept': '*/*',
            'x-rpc-combo_token': token,
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/99.0.4844.84 Safari/537.36',
        }


def run_task() -> str:
    ret_msg = ""
    cg_cn = config.config['cloud_games']['cn']
    if not cg_cn['enable']:
        return ""
    # 云原神签到
    if cg_cn['genshin']['enable'] and cg_cn['genshin']['token'] != "":
        cg_genshin = CloudGenshin(cg_cn['genshin']['token'])
        ret_msg += cg_genshin.sign_account() + "\n\n"
    # 云绝区零签到
    if cg_cn['zzz']['enable'] and cg_cn['zzz']['token'] != "":
        cg_zzz = CloudZZZ(cg_cn['zzz']['token'])
        ret_msg += cg_zzz.sign_account() + "\n\n"
    return ret_msg


if __name__ == '__main__':
    pass
