#coding=utf8
import json

'''
回帖不带图片
不支持删帖
'''
def find_last_id(db,table,refer,val,col):
    cur=db.query("select %s from %s where %s='%s' order by %s desc limit 1"%(col,table,refer,val,col)) 
    return list(cur)[0]["%s"%col]

def make_comment(db,dt):
    '''
    依赖客户端字段较多
    需要提供
        1.是否是回复活动 if_activity
        2.被回复帖子的fid
        3.新帖子的 author title body
    '''
    if dt['if_activity']:
       db.insert('reply',aid=dt['fid'],author=dt['author'],title=dt['title'],body=dt['body'])
    else:
       db.insert('reply',fid=dt['fid'],author=dt['author'],title=dt['title'],body=dt['body'])

    last_id=find_last_id(db,'reply','author',dt['author'],'rid')

    flag=dt['if_activity'] and 'Y' or 'N'
    db.query("insert into unread_reply (author_f,fid,rid,if_activity) values (%s,%s,%s,%s)" % \
            (data['author_f'],dt['fid'],last_id,flag))

def comment(rid,db):
    #deal a reply itself
    tmp={}
    myself=list(db.query('select * from reply where rid="%s"'%rid))[0]
    tmp['time']=myself['ctime'].strftime("%Y-%m-%d-%H")
    tmp['author']=myself['author']
    tmp['body']=myself['body']

    #deal with it's children
    outer=list(db.query('select * from reply where fid="%s"'%rid))
    sons=[]
    for son in outer:
        sons.append(comment(son['rid'],db))
    tmp['reply']=sons
    return tmp
 
def show_comment(aid,db):
    '''	主贴不同于回复贴，这里只查其回贴信息
	主贴本身的信息在上层调用处理，因其可能含图片
    '''
    outer=list(db.query('select * from reply where aid="%s"'%aid))
    sons=[]
    for son in outer:
        sons.append(comment(son['rid'],db))
    #return json.dumps(res)
    return sons

def get_unread(db,dt):
    '''
    个人中心，未读消息
    ''' 
    unread=list(db.query("select * from unread_reply where author_f ='%s'" % (dt['account'])))
    res=[]
    for ur in unread:
        tmp={}
        if ur['if_activity']=='Y':
           f=list(db.query("select author,title from activity where aid='%s'"%ur['fid']))[0]
           tmp['father']={'author':f['author'],'body':f['title'],'fid':ur['fid']}
        else:
           f=list(db.query("select author,body from reply where rid='%s'"%ur['fid']))[0]
           tmp['father']={'author':f['author'],'body':f['body'],'fid':ur['fid']}

        s=list(db.query("select author,body from reply where rid='%s'"%ur['rid']))[0]
        tmp['son']={'author':s['author'],'body':s['body'],'rid':ur['rid']}
        res.append(tmp)
    return res

def read_unread(db,dt):
    '''
    客户端应处理好读帖事件何时出发
    是在消息中心还是在活动界面(含回复列表)
    '''
    db.query("delete  from unread_reply where fid='%s' and rid='%s' and if_activity='%s'" % \
            (dt['fid'],dt['rid'],dt['if_activity']))


















