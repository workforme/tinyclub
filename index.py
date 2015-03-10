#-*- coding:utf-8 -*- 
#!/usr/bin/python

import web
from web import form
from urllib import quote
from _mysql_exceptions import IntegrityError
import json,base64,hashlib,time
import os,shutil

from  plugin import *
#web.config.debug = False

urls=(
'/regist','regist',
'/login','login',
'/logout','logout',
'/main','main',

'/user_detail','mydetail',
'/friend_detail','friend_detail',
'/group_detail','group_detail',
'/activity','activity',
'/my_act','myact',
#附近的活动，不做附近的人，因为是兴趣社交，不是
'/nearby_activity','nearby_activity',
'/updategps','updategps',


'/testing','testing',
)

app= web.application(urls,globals())
db = web.database(dbn='mysql', user='root', pw='qwe123root', db='tinyclub')


class testing:
    def __init__(self):
        self.logger=web.ctx.environ['wsgilog.logger']
    def GET(self):
        self.logger.info("hahahahasdfasfew")
        res=db.query("select * from userinfo limit 1")
        return res

class nearby_activity:
    def GET(self):
        '''data=web.input()
        tp=data['act_type']
        dst=data['dst_city']
        cur=data['cur_city']#如果未开gps就是注册城市，否则是最新城市,这个由前端计算
        lt=data['lat']
        lg=data['lng']

        if tp!='':
           res=list(db.select('activity',where="cate='%s' and city='%s'"%(tp,cur),what="aid,timestamp,lat,lng"))
           #返回格式是{aid:[timestamp,lat,lng]...}
           sortlist=comp_sort(res,dst==cur,kind=True)
           return
        else:
           res=list(db.select('activity',where="city='%s'"%(tp,cur),what="aid,timestamp,lat,lng"))
           sortlist=comp_sort(res,dst==cur,kind=False)
           return
        res=[]
'''
        def utf8(lt):
            for it in lt:
                for k in ['city','title','body']:
                    it[k]=it[k].encode('utf8')
            return lt
        res=[]
        acts=list(db.query("select * from activity"))
        #acts=utf8(acts)
        '''
        捕获文件不存在或目录不存在的异常
        '''
        for act in acts:
            tmp=act.copy()
            path=act['picture']
            fname=os.listdir(act['picture'])[0]
            f=open(path+fname,'r')
            tmp['picture']={fname:base64.b64encode(f.read())}
            tmp['ctime']=act['ctime'].strftime("%Y-%m-%d-%H-%M-%S")
            res.append(tmp)
        #res=str(res)
        return json.dumps(res,ensure_ascii=False)
        #return json.dumps(res)
            

class activity:
    '''
    发起，修改，获取,删除
    关注，取消关注
    '''
    def POST(self):
        data=json.loads(list(web.input())[0],strict=False)
        actop=activity_op(data) 
        
        return {
           'pull'	:actop.pull,
           'push'	:actop.push,
           'update'	:actop.update,
           'delete'	:actop.delete,
           'rvk_atn'	:actop.del_attention,
           'pay_atn'	:actop.pay_attention,

        }[data['optype']](data)

class my_activity:
    '''
    我关注的和我发起的活动
    客户端这时显示的是列表，故活动图片暂不返回（至少不全返回）
    除非单独看活动详情
    '''
    def POST(self):
        '''
        活动按时间由近及远返回，不考虑其他排序因素
        '''
        what=web.input()['todo']
        user=web.input()['account']
        
        actlist =list(db.select('myactivity',order="time DESC",where="account='%s' and aid='%d'"%(user,what=='mime' and 1 or 0)))
        result=[]
        for act in actlist:
            js={}
            act=list(db.select('activity',where="aid='%s'"%act['aid']))[0]
            for k in act.keys():
                js[k]=act[k]
                tmp={}
                pics=os.listdir(act['picture'])
                for pic in pics:
                    f=open(act['picture']+pic)
                    tmp[pic]=base64.b64encode(f.read())
                js['picture']=tmp
            result.append(js)
        return json.dump(result)

class mydetail:
    '''
    用户信息的获取和设置(不含安全设置/密码/手机)
    '''     
    def GET(self):
        '''
        只有一个头像/虽然按多头像处理
        '''
        data= web.input()
        res={}
        info=list(db.select('userinfo',where="account='%s'"%(data['account'])))[0]
        for k in info.keys():
            res[k]=info[k]

        pics=os.listdir(res['picture'])
        for pic in pics:
            f=open(info['picture']+pic)
            tmp[pic]=base64.b64encode(f.read())
        res['picture']=tmp
        return json.dumps(res)

    def POST(self):
        '''
        不是按最小修改集发送，而是粗略地全发送
        文件名须前端另辟一字段发过来，主要是考虑到图片格式问题
        '''
        data= web.input()
        db.update('userinfo',where="account='%s'" %data['account'],
          nickname=data['nick'],
          gender=data['gender'],
          birth=data['age'],
          city=data['city'],
          brief=data['brief'],
        )
        f=open('resource/portrait/%s/%s'%(data['account'],data['pic_name']),'w+')
        f.write(base64.b64decode(data['picture']))

        return 'SET_USER_OK'

class security:
    def POST(self):
        
          #picpath=data['picpath']
          #hobby=data['hobby'],
          #telephone=data['telephone'],
          #password=data['password'],
      pass

class regist:
    def POST(self):
        data=web.input()
        mydir='resource/portrait/%s/'%data['account']
        os.makedirs(mydir)
        try:
           db.insert('userinfo',account=data.account,password=data.password,telephone=data.telephone,
              picpath=mydir
           )
        except IntegrityError:
           return 'ERR_DUP_ACCOUNT'
        return 'OK'


class updategps:
    def POST(self):
        data=web.input()
        update('userinfo',where="account='%s'"%data['account'],lat=data['lat'],lng=data['lng'])
        return 'OK'

class login:
    def POST(self):
        js=json.loads(list(web.input())[0])
        res=db.select('userinfo',where="account='%s'"%(js['account']))
        if not res:
           return 'ERR_NOT_EXIST'
        else:
           who=list(res)[0]['password']
           if not who == js['password']:
              return 'ERR_PASS_FAIL'
        return 'OK'

if __name__== "__main__":
    app.run(Log)

