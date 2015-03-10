#-*- coding:utf-8 -*- 
#!/usr/bin/python

import web
from web import form
from urllib import quote
from _mysql_exceptions import IntegrityError
import json,base64,hashlib,time
import os,shutil

from  infs import *
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
    def GET(self):
        print "aaaaaaa##########"
        return show_comment(1,db)

class friend:
    def POST(self):
        data=web.input()
        friends=list(db.select('myfriend',what="he",where="me='%s'"%data['account']))
        #还没有实现分屏亲
        res=[]
        tmp={}
        for fnd in friends:
            info=list(db.select('userinfo',what="account,,nickname,picpath",where="account='%s'"%fnd['he']))[0]
            tmp['account']=info['account']
            tmp['nickname']=info['nickname']
            f=open(info['picpath'],'r')
            tmp['portrait']=base64.b64encode(f.read())
            result.append(tmp)
        return json.dump(result)


class friend_detail:
    def POST(self):
        data=web.input()
        friend=list(db.select('userifno',where="account='%s'"%data['account']))[0]
        tmp={}
        for k in friend.keys():
            tmp[k]=friend[k]
            f=open(friend['picpath'],'r')
            tmp['portrait']=base64.b64encode(f.read())
        return json.dump(tmp)


class group:
    def POST(self):
        data=web.input()
        groups=list(db.select('mygroup',what="gid",where="account='%s'"%data['account']))
        #还没有实现分屏亲
        res=[]
        tmp={}
        for grp in groups:
            info=list(db.select('groups',what="name",where="gid='%s'"%grp['gid']))[0]
            tmp['name']=info['name']
            result.append(tmp)
        return json.dump(result)
    
class group_detail:
    def POST(self):
        data=web.input()
        grp=list(db.select('groups',where="gid='%s'"%data['gid']))[0]
        
        tmp={}
        for k in grp.keys():
            tmp[k]=grp[k]
        return json.dump(result)

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
                #it['ctime']=str(it['ctime'].strftime("%Y-%m-%d-%H-%M-%S"))
                for k in ['title','city','body']:
                    it[k]=it[k].encode('utf8')
            
            
        res=[]
        acts=list(db.query("select * from activity"))
        utf8(acts)
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
        res=str(res)
        print json.dumps(res,ensure_ascii=False)
            

class activity:
    '''
    发起，修改，获取，一个具体的活动
    '''
    def POST(self):
        data=json.loads(list(web.input())[0],strict=False)
        
        def push(data):
            '''
            gps服务器自动获取，不由客户端发送，省去一次交互
            data的picture字段格式如下{'fname':'fbody',}
            '''
            lt,ln=list(db.select('userinfo',what="lat,lng",where="account='%s'"%(data['account'])))[0]
            db.insert('activity',author=data['account'],title=data['title'],cate=data['classfication'],body=data['content'],city=data['city'],lat=lt,lng=ln)
            maxid=find_last_id(db,'activity','author',data['account'],'aid')
            db.query("update activity set picture='resource/activity/%s/'"%maxid)
            #改了有无问题，之前是 二次json.loads()
            pics=data['image_list']

            for idx in pics.keys():
                path="resource/activity/%d/"%(maxid)
                if not os.path.exists(path):
                   os.makedirs(path)
                f=open(path+idx,'wb')
                f.write(base64.b64decode(pics[idx]))

            db.insert('myactivity',account=data['account'],aid=maxid,mine=1)
            res={}
            res['aid']=maxid
            res['ret']='SUCC'
            return json.dumps(res)

        def pay_atn(data):
            db.insert('myactivity',aid=data['aid'],account=data['account'])
            return 'OK'

        def rvk_atn():
            db.delete('myactivity',where="aid='%s' and account='%s'"%(data['aid'],data['account']))
            return 'OK'

        def update(data):

            '''
            先删除目录下的图片
            然后，update指定aid的数据
            '''

            lt,ln=list(db.select('userinfo',what="lat,lng",where="account='%s'"%(data['account'])))[0]
            db.update('activity',where="aid='%s'"%data['aid'],author=data['account'],title=data['title'],cate=data['classfication'],body=data['content'],city=data['city'],picture="resource/activity/%s/"%data['account'],lat=lt,lng=ln)
            shutil.rmtree('resource/activity/%s'%data['aid'])
            
            pics=json.loads(data['image_list'])
            print data
            print pics
            for idx in pics.keys():
                path="resource/activity/%s/"%(data['aid'])
                if not os.path.exists(path):
                   os.makedirs(path)
                f=open(path+idx,'wb')
                f.write(base64.b64decode(pics[idx]))

            res={}
            res['aid']=data['aid']
            res['ret']='SUCC'
            return json.dumps(res)

           
        def delete(data):
            '''
            添加重复删除的异常检查
            '''
            db.delete('activity',where="aid='%s'"%data['aid'])
            shutil.rmtree('resource/activity/%s'%data['aid'])
            res={}
            res['ret']='SUCC'
            return json.dumps(res)

        def pull(data):
            '''
            有了列表之后，会单独查询
            '''
            aid=data['aid']
            res=list(db.select('activity',where="aid='%s'"%aid))[0]
            js={}
            tmp={}
            for k in res:
                js[k]=res[k]
            pics=os.listdir(res['picture'])
            for pic in pics:
                f=open('%s/%s'%(res['picture'],pic),'r')
                tmp[pic]=base64.b64encode(f.read())
            js['picture']=tmp
            return json.dump(js)

        #分类操作
        return {
           'pull'	:lambda x:pull(x),
           'push'	:lambda x:push(x),
           'update'	:lambda x:update(x),
           'delete'	:lambda x:delete(x),
           'rvk_atn'	:lambda x:rvk_atn(x),
           'pay_atn'	:lambda x:pay_atn(x),

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
    app.run()

