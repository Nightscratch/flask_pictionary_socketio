from flask import Blueprint, render_template, session, jsonify, g, redirect
from app.forms.user import set_username_form
from app import models
from app import PLAYERS
# 注释 + 简化代码 By ChatGPT 3.5
user_bp = Blueprint('user', __name__)

# 设置用户名路由
@user_bp.route('/set_username', methods=["POST"])
def set_username():
    # 获取表单数据并验证表单
    form = set_username_form()
    if not form.validate():
        return jsonify({"code":-1,"msg":form.errors})
    # 获取用户名和房间号
    username = form.data['username']
    room = form.data['room']
    # 检查是否已经有相同的用户名存在于房间内
    if room in PLAYERS and username in PLAYERS[room]['players']:
        return jsonify({"code":-1,"msg":{"username":["游戏内存在重复名称"]}})
    # 如果没有，则将用户名和房间号存入session中
    session['username'] = username
    session['room'] = room
    return jsonify({"code":1,"msg":{"msg":"success"}})

# 退出登录路由
@user_bp.route('/logout', methods=["GET"])
def logout():
    # 将session中的用户名清空
    session['username'] = None
    return redirect('/')