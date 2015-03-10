#coding=utf8
class activity_op:

    def __init__(self,data):
        self.data=data
    
    def push():
        '''
        gps服务器自动获取，不由客户端发送，省去一次交互
        data的picture字段格式如下{'fname':'fbody',}
        '''
        data=self.data
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

    def update():

        '''
        先删除目录下的图片
        然后，update指定aid的数据
        '''
        data=self.data
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

    def delete():
        '''
        添加重复删除的异常检查
        '''
        data=self.data
        db.delete('activity',where="aid='%s'"%data['aid'])
        shutil.rmtree('resource/activity/%s'%data['aid'])
        res={}
        res['ret']='SUCC'
        return json.dumps(res)

    def pull():
        '''
        有了列表之后，会单独查询
        '''
        data=self.data
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

    def pay_attention():
        data=self.data
        db.insert('myactivity',aid=data['aid'],account=data['account'])
        return 'OK'

    def del_attention():
        db.delete('myactivity',where="aid='%s' and account='%s'"%(data['aid'],data['account']))
        return 'OK'


