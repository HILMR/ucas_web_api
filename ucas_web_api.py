"""
国科大 校园网API接口
20200915
"""
import execjs #JS脚本执行，用于破解RSA密钥
import requests #网络接口库
import urllib.parse #URL编码库

class ucas_web_api(object):
    def __init__(self,debug=False):
        self.session=requests.Session()
        self.debug=debug
        #API接口URL
        self.url_host='http://210.77.16.21' #主站
        self.url_redir=self.url_host+'/eportal/redirectortosuccess.jsp' #设备地址获取
        self.url_login=self.url_host+'/eportal/InterFace.do?method=login' #登录
        self.url_logout=self.url_host+'/eportal/InterFace.do?method=logout' #注销
        self.url_info=self.url_host+'/eportal/InterFace.do?method=getOnlineUserInfo' #账户信息
        self.url_onlinedev='http://124.16.77.128/selfservice/module/webcontent/web/onlinedevice_list.jsf' #在线设备
        self.url_consume='http://124.16.77.128/selfservice/module/userself/web/consume.jsf' #套餐用量
        self.url_detail='http://124.16.77.128/selfservice/module/onlineuserself/web/newonlinedetailself_list.jsf' #网络详单
        

    def Get_EportalINFO(self):
        """获取Eportal设备信息"""
        reurl=self.session.get(self.url_redir,allow_redirects=False).headers['Location'] #利用重定向获取
        if(reurl.find('index')!=-1):
            laninfo=reurl[reurl.find('index')+10:]
            return (0,urllib.parse.quote(laninfo)) #0表示未登录，第二位为设备信息
        elif(reurl.find('success')!=-1):
            return (1,reurl[reurl.find('userIndex')+10:]) #1表示已登录，第二位为用户index
        else:
            return (-1,'err') #未知错误

    def Get_RSAKeyPair(self,pwd):
        """获取RSA加密密钥"""
        #加载原始页面的JS脚本
        js_BigInt=open('js/BigInt.js','r',encoding= 'utf8').read()
        js_Barrett=open('js/Barrett.js','r',encoding= 'utf8').read()
        js_RSA=open('js/RSA.js','r',encoding= 'utf8').read()
        js_Main=open('js/Main.js','r',encoding= 'utf8').read()
        js=execjs.compile(js_BigInt+js_Barrett+js_RSA+js_Main)
        return js.call('main',pwd) #执行脚本获取密钥

    def Login(self,uname,pwd):
        """登录，nname学号，pwd密码"""
        info=self.Get_EportalINFO() #检查是否需要登录
        if(info[0]==0):
            #包装登录信息，主要包括学号，RSA加密后的密码（不是明文通信），以及设备相关字符串（缺失会报设备无法识别的错误）
            data_login={'userId':uname,'password':self.Get_RSAKeyPair(pwd),
                        'queryString':info[1],'service': '',
                        'operatorUserId': '','passwordEncrypt': 'true'}
            response=self.session.post(self.url_login,data_login).json()
            if(self.debug):
                print(response)
        else:
            #已经登录
            if(self.debug):
                print(info)

    def Logout(self):
        """下线"""
        info=self.Get_EportalINFO()
        if(info[0]==1):
            #已经登录才可下线，通过userIndex识别操作
            response=self.session.post(self.url_logout,{'userIndex':info[1]}).json()
            if(self.debug):
                print(response)
        else:
            if(self.debug):
                print(info)

    def Get_OnlineUserInfo(self):
        """获取在线用户信息，初次登录信息易获取失败"""
        info=self.Get_EportalINFO()
        if(info[0]==1):
            #已经登录才可获取，通过userIndex识别操作
            response=self.session.post(self.url_info,{'userIndex':info[1]}).json()
            if(self.debug):
                print(response)
            return response
        else:
            return None
            if(self.debug):
                print(info)

    def Get_maxFlow(self):
        """获取剩余流量"""
        info=self.Get_OnlineUserInfo()
        if(info!=None):
            return info['maxFlow']

    def Get_accountFee(self):
        """获取账户余额"""
        info=self.Get_OnlineUserInfo()
        if(info!=None):
            return info['accountFee']

    def Login_selfservice(self):
        """登录自助服务系统（免验证码接口）"""
        info=self.Get_OnlineUserInfo()
        if(info!=None):
            self.session.get(info['selfUrl'])
            #进行详单获取等操作之前必须先登录自助服务系统
            print(self.session.get(self.url_consume).text)

    
if __name__ == "__main__":
    demo=ucas_web_api(False)
    demo.Login(input("学号:"),input("密码:"))
    demo.Get_OnlineUserInfo()
    print("剩余流量：%s"%(demo.Get_maxFlow()))
    print("剩余金额：%s"%(demo.Get_accountFee()))
    if(input("是否下线？Y/N")=='Y'):
        demo.Logout()
        print("下线")
        
