# 米游社辅助签到

基于 [MihoyoBBSTools](https://github.com/Womsxd/MihoyoBBSTools) 的修改版，以支持 GitHub Actions

不定期同步原仓库

来自原作者的警告：

> ⚠️ **对于 Fork 的开发者/用户，请不要滥用 GitHub Actions，因为 GitHub 将计算您的分支 GitHub Actions 使用量并归属到上游存储库，这可能导致 GitHub 停用此上游存储库**

本仓库并非原仓库的 Fork，而是下载后重新上传而来，但此警告同样适用。

## 如何使用

- **Github Actions**

  1. 根据需求修改 `config/config.yaml.default` 文件，不必填写 `cookie` 和 `stoken`

  2. **使用[获取 Cookie](#获取米游社-cookie)里面的方法来获取米游社 Cookie**

  3. 通过[获取 Stoken](https://github.com/Womsxd/mihoyo_login) 项目获取 Stoken，或请参考[Hutao文档](https://hut.ao/zh/advanced/get-stoken-cookie-from-the-third-party.html)里的方法获取 Stoken (麻烦可以去关闭 BBS 模块 mihoyobbs.enable: false)

  4. 创建一个 `secret`，名称为 `profiles`，内容格式如下：

      ```json
      [
        {
          "name": "档案名",
          "cookie": "刚刚获取的 Cookie",
          "stoken": "刚刚获取的 Stoken",
          "config": { // 可选，覆盖默认配置
            // 结构与 config.yaml 一致
          }
        },
        {
          // 其他用户...
        }
      ]
      ```

      本修改版默认使用多用户模式，如只有一个用户填写一个即可

- **其它方式参见[原仓库](https://github.com/Womsxd/MihoyoBBSTools)**

## 获取米游社 Cookie

1. 打开你的浏览器,进入**无痕/隐身模式**

2. 由于米哈游修改了 bbs 可以获取的 Cookie，导致一次获取的 Cookie 缺失，所以需要增加步骤

3. 打开 `https://www.miyoushe.com/ys/` 并进行登入操作

4. 按下键盘上的 `F12` 或右键检查,打开开发者工具,点击 `Source` 或 `源代码`

5. 键盘按下 `Ctrl+F8` 或点击停用断点按钮，点击 ` ▌▶` 解除暂停

6. 点击 `NetWork` 或 `网络`，在 `Filter` 或 `筛选器` 里粘贴 `getUserGameUnreadCount`，同时选择 `Fetch/XHR`

7. 点击一条捕获到的结果，往下拉，找到 `Cookie:`

8. 复制Cookie部分除 `Cookie:` 的全部内容

## 海外版获取Cookie

1. 打开你的浏览器,进入**无痕/隐身模式**

2. 打开 `https://act.hoyolab.com/bbs/event/signin/hkrpg/index.html?act_id=e202303301540311` 并进行登入操作

3. 按下键盘上的 `F12` 或右键检查,打开开发者工具,在控制台输入:

    ```javascript
    document.cookie
    ```

4. 从 `ltoken=...` 开始复制到结尾

## 获取云原神的 token

1. 建议使用打开浏览器的无痕/隐私/InPrivate 模式

2. 打开 [云原神网页版](https://ys.mihoyo.com/cloud/#/)

3. 按下键盘上的 `F12` 或右键检查,打开开发者工具,在打开后登入账号

4. 在 filter 里面输入`wallet/wallet/get`,选择 `status` 为 `200` 的记录

5. 点击记录，往下拉，找到 `X-Rpc-Combo_token` ，复制对应的值，成功获取 token

