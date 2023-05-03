# 导入需要用到的库和模块
from flask import Blueprint, request, session, render_template, g, redirect
from flask_socketio import send, emit, ConnectionRefusedError, join_room, close_room
from app import socketio
from app import PLAYERS
import threading, copy, random
# 注释 + 简化代码 By ChatGPT 3.5
# 创建游戏模块，并设置路由
game_bp = Blueprint('game', __name__)

def get_user_and_room():
    username = session.get('username')
    room = session.get('room')
    return username, room

# 更新在线用户数量的方法
def update_count(room):
    emit(
        'update_count',
        {'host': PLAYERS[room]['host'], 'players': list(PLAYERS[room]['players'].keys())},
        broadcast=True,
        to=room
    )

# 设置游戏状态的方法
def set_state(room, state):
    # 修改PLAYERS字典中的状态值
    PLAYERS[room]['state'] = state
    # 将状态变更广播给房间内的所有玩家
    emit(
        'state_change',
        {'state': state},
        broadcast=True,
        to=room
    )

# 游戏主页面路由
@game_bp.route('/game')
def game():
    # 获取当前用户的用户名和房间号
    g.username,g.room = get_user_and_room()

    # 如果没有登录或没有进入任何房间，则重定向到首页
    if not g.username or not g.room:
        return redirect('/')
    # 显示游戏主页面
    return render_template('game/index.html')

# 用户连接到WebSocket事件
@socketio.on('connect')
def handle_connect():
    # 获取当前用户的用户名和房间号
    username,room = get_user_and_room()
    if username:
        # 如果该房间还不存在，则创建该房间
        if not room in PLAYERS:
            PLAYERS[room] = {
                'players': {},
                'host': username,
                'painter': username,
                'answer': None,
                'state': '选词中...'
            }
        # 如果该房间已满，则拒绝该用户的连接请求
        if len(PLAYERS[room]['players']) >= 4:
            raise ConnectionRefusedError('Room is full')
        # 将该用户加入到该房间中
        PLAYERS[room]['players'][username] = {
            'sid': request.sid
        }
        join_room(room)
        # 更新在线用户数量
        update_count(room) 
    else:
        raise ConnectionRefusedError('No Name')

# 用户从WebSocket断开事件
@socketio.on('disconnect')
def handle_disconnect():
    # 获取当前用户所在房间的房间号
    username,room = get_user_and_room()

    # 如果该房间存在
    if room in PLAYERS:
        # 如果该用户是该房间的房主，则关闭该房间并删除PLAYERS字典中该房间对应的值
        if PLAYERS[room]['host'] == username:
            emit('close_room', broadcast=True, to=room)
            del PLAYERS[room]
            close_room(room)
        # 否则，将该用户从该房间中删除
        del PLAYERS[room]['players'][username]
        # 更新在线用户数量
        update_count(room) 

# 获取游戏状态
@socketio.on('game_state')
def game_state():
    # 获取当前用户所在房间的房间号
    username,room = get_user_and_room()
    # 返回JSON格式的游戏状态
    return {'painter': PLAYERS[room]['painter'], 'state': PLAYERS[room]['state']}

# 设置画家要画的内容事件
@socketio.on('set_answer')
def set_answer(data):
    username,room = get_user_and_room()
    # 如果该用户是当前游戏的画家，则将其要画的内容存入PLAYERS字典中，并设置游戏状态为“绘画中...”
    if username == PLAYERS[room]['painter']:
        PLAYERS[room]['answer'] = data
        set_state(room, '绘画中...')

# 画图事件
@socketio.on('paint')
def paint(data):
    username,room = get_user_and_room()
    # 如果该用户是当前游戏的画家，则将其绘画的路径广播给该房间内的其他用户
    if username == PLAYERS[room]['painter']:
        emit('new_paths', data, broadcast=True, to=room)

# 猜测事件
@socketio.on('guess')
def guess(data):
    username,room = get_user_and_room()

    # 如果猜测的答案与当前游戏的答案相同，则通知所有房间内的用户该猜测者猜对了
    if data == PLAYERS[room]['answer']:
        emit(
            'msg',
            '<' + username + '>' + '猜对了！',
            broadcast=True,
            to=room
        ) 
        return '猜对了'
    # 否则告诉所有房间内的用户该猜测者猜错了
    else:
        emit(
            'msg',
            '<' + username + '>' + '猜“' + data + '”但是猜错了！',
            broadcast=True,
            to=room
        ) 
        return '猜错了'

# 画家结束画图事件
@socketio.on('painter_over')
def painter_over():
    # 如果该用户是当前游戏的画家
    username,room = get_user_and_room()

    if username == PLAYERS[room]['painter']:
        # 删除PLAYERS字典中该用户，并从剩余用户中随机选择一个用户作为新的画家
        p = copy.deepcopy(PLAYERS[room]['players'])
        del p[username]
        if len(p.keys()) > 0:
            PLAYERS[room]['painter'] = random.choice(list(p.keys()))
            # 广播新的画家给所有房间内的用户，并将游戏状态设置为“选词中...”
            emit(
                'change_painter',
                {'painter': PLAYERS[room]['painter']},
                broadcast=True,
                to=room
            ) 
            set_state(room, '选词中...')