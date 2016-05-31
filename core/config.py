#-*- coding: utf-8 -*-
# 2015.11.18 by rocksea
DOMAIN = "xxx.xxx.xxx.xxx"
RETURNURL = "http://%s/danalpay/cpcgi" % DOMAIN
CANCELURL = "http://%s/danalpay/cancel" % DOMAIN
NOTIURL = "http://%s/danalpay/noti" % DOMAIN
#******************************************************
# DN_CREDIT_URL       : 결제 서버 정의
#******************************************************
DN_CREDIT_URL = "https://credit.danalpay.com/credit/"

#******************************************************
# Set Timeout
#******************************************************
DN_CONNECT_TIMEOUT = 5000
DN_TIMEOUT = 30000

ERC_NETWORK_ERROR = "-1"
ERM_NETWORK = "Network Error"

#******************************************************
# ID_MERCHANT          : 다날에서 제공해 드린 CPID
# PW_MERCHANT  : 다날에서 제공해 드린 암복호화 PW
#******************************************************
ID_MERCHANT = "xxxxx" # 실서비스를 위해서는 반드시 교체필요.
PW_MERCHANT = "xxxxxxxxxxxxxx" # 암호화KEy. 실서비스를 위해서는 반드시 교체필요.
IV_MERCHANT = "xxxxxxxxxxxxxx" # IV 고정값.

