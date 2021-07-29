# -*- coding: utf-8 -*-
# @Time    : 2021/7/7 22:29
# @Author  : XQX
# @File    ：blacklist_creater.py
import os
import re
import sys
ip_black_list_url_1 = "https://raw.githubusercontent.com/gitzixun/ipblacklist/master/ip"


def get_ips(content):
    compile_rule = re.compile(r'\d+[\.]\d+[\.]\d+[\.]\d+')
    result = re.findall(compile_rule, content)
    return result


def do_shell(shell_str):
    if sys.version_info.major == 2:
        import commands
        (status,output) = commands.getstatusoutput(shell_str)

        print (output)
        return output
    else:
        import subprocess
        (status,output) = subprocess.getstatusoutput(shell_str)
        print(output)
        return output

def do_for_ip():
    if sys.version_info.major == 2:
        import urllib2

        try:
            res = urllib2.urlopen(ip_black_list_url_1,timeout=10.0)
        except:
            return
    else:
        import urllib.request
        try:
            res = urllib.request.urlopen(ip_black_list_url_1,timeout=10.0)
        except:
            return

    black_content = res.read().decode("utf-8")

    black_set =set(get_ips(black_content))

    check_content = do_shell("sudo dpkg-query -l ipset")
    if "no packages" in check_content:
        do_shell("sudo apt update")
        do_shell("sudo apt install ipset -y")

    content = do_shell("sudo ipset list blacklist")
    if "given name does not exist" in content:
        do_shell("sudo ipset create blacklist hash:ip")
        current_set = set()
    else:
        current_set = set(get_ips(content))

    black_add_set = black_set - current_set

    black_del_set = current_set - black_set

    # 需添加
    for ip in black_add_set:
        do_shell("sudo ipset add blacklist %s"%(ip))

    # 需删除
    for ip in black_del_set:
        do_shell("sudo ipset del blacklist %s"%(ip))

    if "match-set blacklist src" not in do_shell("sudo iptables -L"):
        do_shell("sudo iptables -I INPUT -m set --match-set blacklist src -j DROP")

    do_shell("sudo ipset save")


if __name__ == '__main__':
    do_for_ip()
