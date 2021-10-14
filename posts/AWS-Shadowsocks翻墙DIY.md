---
title: AWS + Shadowsocks翻墙DIY
date: 2015-09-14 09:43:23
category: "tech"
tags: ["index", "AWS", "proxy", "tutorial"]
---
- 前两天终于从加州回来，除了和家人进行了感动人心的重逢以及吃啥都觉得好吃的体验，还愈发的感觉到国内网络环境的糟糕。在家连 Gmail 都上不去，已然到了不能忍受的程度。于是昨天在摸哥的帮助下在 AWS 上搭了一个 Shadowsocks 服务器，本地用 Shadowsocks 的命令行工具就可以实现科学上网。虽然有一些比较 tricky 的地方需要注意，但还是成功搞定，和室友们愉快的欣赏了“怒斥香港记者”、“二院讲话”、“人民代表大会答记者问”等经典片段。

#### 申请和启动 AWS 虚拟机

- 首先到 AWS 主页 [aws.amazon.com/cn/](aws.amazon.com/cn/)， 点击注册，新用户登陆，填写信息，付款信息（除了银联的借记卡以外其他好像都可以，反正免费使用一年^q^），电话，然后是身份验证（只要把电脑上的四位数用手机键盘输入就好了），支持方案选择基本就好，然后就可以确认并登陆控制台。
- 可以发现 AWS 实际上提供了相当全面而强大的各种网络服务。我们只需要最基本的EC2就可以了。
- 这时可以发现服务需要24小时才能完全激活，所以可以等着了 ^q^
- 为了达到最好的网络速度，最好在控制面板的右上角将地区改变为“亚太地区（东京）”
- 第二天再回来，点击 EC2 可以进入 EC2控制面板。然后点击“启动实例”
    - 选择 Amazon 系统映像（AMI）：我们就用一个 `Ubuntu Server 14.04 LTS (HVM)` 就好了。
    - 实例类型：如果是自己用的话，选择 `t2.nano` 就够用了。不过如果是刚刚注册的账号可以用 `t2.micro`，可以免费用一年。
    - 核查实例并启动：直接点击启动，随后会弹出要选择密钥对的框，点击创建新的密钥对，名字随便起（比如 `foo`），然后下载密钥对，会得到名为 `foo.pem` 的文件，这时进入命令行，修改权限：
    ```Bash
    $ sudo chmod 400 foo.pem
    ```
    然后就可以启动实例啦。
    - 您的实例正在启动：点击查看实例，等到实例状态变成 running 之后，记录下公有IP（比如 `1.2.3.4`）
    - 从命令行登陆：用密钥对和公有IP登陆实例
    ```Bash
    $ ssh -i foo.pem ubuntu@1.2.3.4
    Welcome to Ubuntu 14.04.2 LTS (GNU/Linux 3.13.0-48-generic x86_64)

     * Documentation:  https://help.ubuntu.com/

      System information as of Sun Sep 13 15:36:41 UTC 2015

      System load:  0.0               Processes:           100
      Usage of /:   12.3% of 7.74GB   Users logged in:     0
      Memory usage: 9%                IP address for eth0: 172.31.19.130
      Swap usage:   0%

      Graph this data and manage this system at:
        https://landscape.canonical.com/

      Get cloud support with Ubuntu Advantage Cloud Guest:
        http://www.ubuntu.com/business/services/cloud

    Last login: Sun Sep 13 15:36:42 2015 from 4.3.2.1
    ubuntu@ip-172-31-19-130:~$
    ```
    这样就登陆成功啦

#### 设置 Shadowsocks Server 端

- 安装 `pip`
```Bash
$ sudo apt-get update
$ sudo apt-get install python-pip
```
- 安装 Shadowsocks
```Bash
$ sudo pip install shadowsocks
```
- 启动 shadowsocks server
```Bash
$ sudo ssserver -p 443 -k password -m aes-256-cfb
```
    - 其中 `-p` 指定了服务器的端口
    - `-k` 指定了服务器的登陆密码
    - `-m` 指定了 `method` 即加密方法

- 这里为了让它在后台启动，可以使用 Ubuntu 自带的后台bash管理工具 `screen`
    - 运行 `screen`，然后回车，就进入了一个新的bash，在这里我们可以启动 `ssserver`。
    - 用 ctrl+A ctrl+D 可以 detach 这个 bash。
    - 用下面命令可以查看有哪些后台的 bash 在运行
    ```Bash
    $ screen -list
    There is a screen on:
    	7160.pts-3.ip-172-31-19-130	(09/13/15 13:50:07)	(Detached)
    1 Socket in /var/run/screen/S-ubuntu.
    ```
    - 用下面命令可以重新进入（atach）后台bash
    ```Bash
    $ screen -R pts-3.ip-172-31-19-130
    ```
- AWS 默认只允许 22 端口的外网访问（即只能 ssh 连接），我们需要给安全组添加规则以允许来自 443 端口的访问。
    - 在查看实例中找到你的实例，点击最右面的安全组
    - 在下面点击入站，编辑
    - 在弹出框中点击添加规则，自定义tcp规则，端口范围为 443，保存。

- 事实上 `ssserver` 自己也支持后台启动。只要在自后添加上 `-d start` 的参数，就可以在后台启动相同的服务器程序。运行的 log 被储存在 `/var/log/shadowsocks.log` 中，可用如下命令随时查看。
    ```Bash
    $ tail -f /var/log/shadowsocks.log
    ```

- `ssserver` 也可以用配置文件来启动，这样可以保证 server 和 client 的配置统一：
    ```Bash
    $ sudo ssserver -c shadowsocks-libev.json
    ```
    注意其中的 `server` 配置最好填写 `0.0.0.0`.

#### Mac 上的 Shadowsocks 客户端（命令行工具）

- 安装 Homebrew：见 [brew.sh](http://brew.sh/)
- 更新列表
```Bash
$ brew update
```
- 安装 shadowsocks-libev
```Bash
$ brew install shadowsocks-libev
```
- 修改客户端的配置文件 `/usr/local/etc/shadowsocks-libev.json`，使其能够连接到相应的 Shadowsocks server：
```JSON
{
    "server":"1.2.3.4",
    "server_port":443,
    "local_port":1080,
    "password":"password",
    "timeout":600,
    "method":"aes-256-cfb"
}
```
- 根据安装后的信息，可以有以下几种方式
    - 将客户端以服务的形式添加进启动项里：
    ```Bash
    $ ln -sfv /usr/local/opt/shadowsocks-libev/*.plist ~/Library/LaunchAgents
    ```
    - 单次启动服务
    ```Bash
    $ launchctl load ~/Library/LaunchAgents/homebrew.mxcl.shadowsocks-libev.plist
    ```
    - 直接启动客户端
    ```Bash
    $ /usr/local/opt/shadowsocks-libev/bin/ss-local -c /usr/local/etc/shadowsocks-libev.json
    ```
- 启动之后，进入 系统设置 -> 网络 -> 高级 -> 代理（Proxies），勾选 SOCKS代理，在代理服务器里填上 `127.0.0.1:1080`。如果有什么不想用代理访问的域名，比如 `localhost`、校园网什么的，可以添加在最下面的框里（支持正则表达）。
- 打开浏览器，在地址栏中输入 `youtube.com`，在搜索框中输入 “怒斥” 并搜索。

#### Trouble Shooting

- 在安装和启动 `ssserver` 的时候，可能会出现这样的问题：
```
AttributeError: /usr/lib/x86_64-Linux-gnu/libcrypto.so.1.1: undefined symbol: EVP_CIPHER_CTX_cleanup
```
    - 这个问题是由于在openssl1.1.0版本中，废弃了EVP_CIPHER_CTX_cleanup函数。我们可以用以下命令找到 `openssl.py` 的源文件，然后将其中的 `EVP_CIPHER_CTX_cleanup` 修改为新的命名 `EVP_CIPHER_CTX_reset` 即可。
    ``` Bash
    $ find / -name openssl.py
    ```
    - [Reference](https://blog.csdn.net/blackfrog_unique/article/details/60320737)
