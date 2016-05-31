#-*- coding: utf-8 -*-
#
# Danal  - Python interface to Danal Payment Tool
# Copyright (c) 2015 rocksea
#   https://github.com/rocksea/danal-core
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
from django.http import QueryDict
import urllib, urlparse
from Crypto.Cipher import AES
import base64
import binascii
import pycurl, json
from StringIO import StringIO
class DanalPay :
  def __init__(self, config):
    """
    Create DanalPay

    """
    self.config = config
    self.BS = 16
    self.PAD = lambda s: s + (self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS) 
    self.UNPAD = lambda s : s[0:-ord(s[-1])]
  def request(self, **paydata) :
    # Payment Data
    REQ_DATA = {}
    REQ_DATA["CPID"] = self.config.ID_MERCHANT
    REQ_DATA["SUBCPID"] = ""
    REQ_DATA["AMOUNT"] = paydata['AMOUNT']
    REQ_DATA["CURRENCY"] = "410"
    REQ_DATA["ITEMNAME"] = paydata["ITEMNAME"]
    REQ_DATA["USERAGENT"] = paydata["USERAGENT"]
    REQ_DATA["ORDERID"] = paydata["ORDERID"]
    REQ_DATA["OFFERPERIOD"] = ""
  
    # Customer Infomation
    REQ_DATA["USERNAME"] = paydata["USERNAME"] # 구매자 이름
    REQ_DATA["USERID"] = paydata["USERID"] # 사용자 ID
    REQ_DATA["USEREMAIL"] = paydata["USEREMAIL"] # 소보법 email수신처
  
    # URL Infomation
    REQ_DATA["CANCELURL"] = self.config.CANCELURL
    REQ_DATA["RETURNURL"] = self.config.RETURNURL
    REQ_DATA["NOTIURL"] = self.config.NOTIURL
  
    # Basic Infomation
    REQ_DATA["TXTYPE"] = "AUTH"
    REQ_DATA["SERVICETYPE"] = "DANALCARD"
    REQ_DATA["ISNOTI"] = "N"
    REQ_DATA["BYPASSVALUE"] = "this=is;a=test;bypass=value" # BILL응답 또는 Noti에서 돌려받을 값. '&'를 사용할 경우 값이 잘리게되므로 유의.
  
    RES_DATA = self.callCredit(**REQ_DATA)
    return RES_DATA
  #******************************************************
  # 다날 서버와 통신함수 CallTrans
  #    - 다날 서버와 통신하는 함수입니다.
  #    - Debug가 true일경우 웹브라우져에 debugging 메시지를 출력합니다.
  #******************************************************
  def callCredit(self, **kwargs ) :
    sent_headers = []
    received_headers = []
    def collect_headers(debug_type, debug_msg):
      if debug_type == pycurl.INFOTYPE_HEADER_OUT:
        sent_headers.append(debug_msg)
      if debug_type == pycurl.INFOTYPE_HEADER_IN:
        received_headers.append(debug_msg)
  
    REQ_STR = self.toEncrypt( self.data2str( **kwargs ) )
    REQ_STR = urllib.quote_plus( REQ_STR )
    REQ_STR = "CPID=%s&DATA=%s" % ( self.config.ID_MERCHANT, REQ_STR )
    #print "######## REQ_STR : %s" % REQ_STR
    buffer = StringIO()
  
    c = pycurl.Curl()
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.setopt(pycurl.CONNECTTIMEOUT, self.config.DN_CONNECT_TIMEOUT)
    c.setopt(pycurl.TIMEOUT, self.config.DN_TIMEOUT)
    c.setopt(pycurl.URL, self.config.DN_CREDIT_URL)
    c.setopt(pycurl.HTTPHEADER, ['Content-type:application/x-www-form-urlencoded; charset=euc-kr'])
    c.setopt(pycurl.POSTFIELDS,REQ_STR );
    #c.setopt(pycurl.RETURNTRANSFER,1 );
    c.setopt(pycurl.DEBUGFUNCTION, collect_headers)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
  
    # HTTP response code, e.g. 200.
    #print '######## Status: %d' % c.getinfo(c.RESPONSE_CODE)
    # Elapsed time for the transfer.
    #print '######## Status: %d' % c.getinfo(c.TOTAL_TIME)
    #print '######## Response Body: %s' % buffer.getvalue()
  
    #RES_STR = urllib.unquote_plus(buffer.getvalue())
    RES_STR = buffer.getvalue()
    RES_STR = urlparse.parse_qs(RES_STR)
    RES_STR = self.toDecrypt(RES_STR['DATA'][0])
    #print '######## RES_STR : %s' % RES_STR
    c.close()
    RES_DATA = self.str2data(str(RES_STR))
    return RES_DATA
  
  def str2data(self, string) :
    data = {}
    pairs = string.split("&");
    for value in pairs :
      parsed = value.split("=")
      if(len(parsed) == 2) :
        data[parsed[0]] = urllib.unquote(parsed[1])
    return data
  
  def data2str(self, **kwargs) :
    args = []
    for key, value in kwargs.iteritems() :
      args.append( "%s=%s" % (key, value) )
    string = "&".join(args)
    return string
  
  def toEncrypt(self, plaintext) :
    key = binascii.unhexlify(self.config.PW_MERCHANT)
    iv = binascii.unhexlify(self.config.IV_MERCHANT)
    mode = AES.MODE_CBC
    plaintext = self.PAD(plaintext)
    #print "KEY : %s " % key
    #print "MODE : %s " % mode
    #print "IV : %s " % iv
    #print "PLAIN TEXT : %s " % plaintext
    encryptor = AES.new(key, mode, IV=iv)
    ciphertext = encryptor.encrypt(plaintext)
    ciphertext = base64.b64encode(ciphertext)
    return ciphertext
  
  def toDecrypt(self, ciphertext) :
    key = binascii.unhexlify(self.config.PW_MERCHANT)
    iv = binascii.unhexlify(self.config.IV_MERCHANT)
    mode = AES.MODE_CBC
    ciphertext = base64.b64decode(ciphertext)
    #print "KEY : %s " % key
    #print "MODE : %s " % mode
    #print "IV : %s " % iv
    #print "PLAIN TEXT : %s " % plaintext
    encryptor = AES.new(key, mode, IV=iv)
    plaintext = encryptor.decrypt(ciphertext)
    #plaintext = UNPAD(plaintext)
    return plaintext
