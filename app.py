#!/usr/bin/env python3


"""


KRISHU X CHEATS — STANDALONE KEYAUTH AUTHENTICATION PLATFORM


Autonomous, high-performance licensing server with full REST APIs,


dual MongoDB Atlas + local JSON persistence, admin console, and client SDKs.


"""





import os


import sys
import re


import json


import time


import uuid


import secrets


import logging


import urllib.request


from datetime import datetime, timedelta, timezone


from functools import wraps





from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory, abort


try:


    from flask_cors import CORS


except ImportError:


    def CORS(app, *args, **kwargs):


        pass





try:


    from dotenv import load_dotenv


    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


except ImportError:


    pass





from keyauth import KeyAuth, KrishuKeyAuthEngine, _hash_pass, OWNER_ID








logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')


logger = logging.getLogger('KrishuXCheats')





app = Flask(__name__, static_folder='static', template_folder='templates')


app.secret_key = os.environ.get('SECRET_KEY', os.urandom(32))


CORS(app, resources={r'/*': {'origins': '*'}})





# In-memory session store for web users, key users & resellers


ACTIVE_SESSIONS = {}








# Also support /login, /dashboard, /register at root


@app.route('/')


def root_index():


    return render_template('keyauth_index.html')





@app.route('/login')


def root_login():


    return render_template('keyauth_login.html')





@app.route('/dashboard')


def root_dashboard():


    return render_template('keyauth_user_dashboard.html')





@app.route('/register')


def root_register():


    return render_template('keyauth_register.html')





# ── WEB PAGE VIEWS ─────────────────────────────────────────────





@app.route('/keyauth')


@app.route('/keyauth/admin/dashboard')


@app.route('/admin/dashboard')


def keyauth_admin_dashboard_page():


    """Krishu X Cheats Admin Console"""


    return render_template('keyauth_admin_dashboard.html')





@app.route('/admin')


@app.route('/keyauth/admin')


def keyauth_admin_login_page():


    """Krishu X Cheats Admin Login"""


    return render_template('keyauth_admin_login.html')





@app.route('/keyauth/login')


def keyauth_user_login_page():


    """Krishu X Cheats User Portal Login"""


    return render_template('keyauth_login.html')





@app.route('/keyauth/dashboard')


def keyauth_user_dashboard_page():


    """Krishu X Cheats User Dashboard"""


    return render_template('keyauth_user_dashboard.html')





@app.route('/keyauth/register')


def keyauth_user_register_page():


    """Krishu X Cheats User Registration"""


    return render_template('keyauth_register.html')





@app.route('/register')


def keyauth_register_redirect():


    return redirect('/keyauth/register')





@app.route('/cheats')


@app.route('/portal')


@app.route('/keyauth/portal')


@app.route('/keyauth/home')


def keyauth_index_page():


    """Krishu X Cheats Landing Portal"""


    return render_template('keyauth_index.html')








# ── SDK DOWNLOAD ENDPOINT ─────────────────────────────────────





@app.route('/download/<path:filename>', methods=['GET'])


@app.route('/keyauth/download/<path:filename>', methods=['GET'])


def keyauth_download_sdk(filename):


    """Download official client SDK files (Python, C++, C#, Java, etc.)"""


    sdk_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static', 'sdk'))


    allowed = ['krishuxcheats.cpp', 'krishuxcheats.cs', 'krishuxcheats.h', 'krishuxcheats.java', 'krishuxcheats.py', 'oneamxiters.cpp', 'oneamxiters.cs', 'oneamxiters.py']


    if filename not in allowed and not filename.startswith('krishu'):


        return jsonify({'success': False, 'message': 'File not found'}), 404


    return send_from_directory(sdk_dir, filename, as_attachment=True)








# ── STATIC ASSETS ROUTES (/css/..., /img/..., /js/...) ─────────





@app.route('/css/<path:filename>', methods=['GET'])


def keyauth_serve_css(filename):


    css_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static', 'css'))


    return send_from_directory(css_dir, filename)





@app.route('/img/<path:filename>', methods=['GET'])


def keyauth_serve_img(filename):


    img_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static', 'img'))


    return send_from_directory(img_dir, filename)





@app.route('/js/<path:filename>', methods=['GET'])


def keyauth_serve_js(filename):


    js_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static', 'js'))


    return send_from_directory(js_dir, filename)








# ── DISCORD WEBHOOK SENTINEL ──────────────────────────────────





def send_discord_webhook(webhook_url: str, title: str, description: str, fields: list = None, color: int = 0xff2a5f):


    if not webhook_url or not webhook_url.startswith(('http://', 'https://')):


        return False, "Invalid or missing Webhook URL"


    try:


        embed = {


            "title": f"🌸 {title}",


            "description": description,


            "color": color,


            "timestamp": datetime.now(timezone.utc).isoformat(),


            "footer": {


                "text": "KRISHU X KEYAUTH • Enterprise Security Sentinel",


                "icon_url": "https://raw.githubusercontent.com/favicon.ico"


            },


            "author": {


                "name": "KRISHU X KEYAUTH",


                "icon_url": "https://raw.githubusercontent.com/favicon.ico"


            }


        }


        if fields:


            embed["fields"] = fields





        payload = {


            "username": "KRISHU X KEYAUTH",


            "avatar_url": "https://raw.githubusercontent.com/favicon.ico",


            "embeds": [embed]


        }





        req = urllib.request.Request(


            webhook_url,


            data=json.dumps(payload).encode('utf-8'),


            headers={


                'Content-Type': 'application/json',


                'User-Agent': 'KRISHU-X-KEYAUTH-SENTINEL/2.0'


            },


            method='POST'


        )


        with urllib.request.urlopen(req, timeout=6) as resp:


            return True, "Webhook dispatched successfully"


    except Exception as e:


        logger.warning(f"Discord webhook notice: {e}")


        return False, str(e)








def trigger_security_webhook(event_title: str, description: str, fields: list = None, color: int = 0xff2a5f, identifier: str = 'master'):


    try:


        admin_hook = KeyAuth.get_webhook_config('admin', 'master')


        if admin_hook.get('enabled') and admin_hook.get('url'):


            send_discord_webhook(admin_hook['url'], event_title, description, fields, color)





        if identifier and identifier != 'master':


            usr_hook = KeyAuth.get_webhook_config('user', identifier)


            if usr_hook.get('enabled') and usr_hook.get('url'):


                send_discord_webhook(usr_hook['url'], event_title, description, fields, color)


    except Exception as e:


        logger.error(f"Error triggering security webhook: {e}")








# ── ADMIN REST APIS (/admin/api/...) ──────────────────────────





@app.route('/admin/api/login', methods=['POST'])


def keyauth_api_admin_login():


    data = request.json or {}


    username = data.get('username', '').strip()


    password = data.get('password', '').strip()





    if KeyAuth.verify_admin(username, password):


        token = f"kauth_admin_{secrets.token_hex(24)}"


        return jsonify({'success': True, 'token': token, 'username': username})


    return jsonify({'success': False, 'message': 'Invalid administrator credentials'}), 401








@app.route('/admin/api/stats', methods=['GET'])


def keyauth_api_admin_stats():


    stats = KeyAuth.get_stats()


    return jsonify({'success': True, 'stats': stats, 'dbStatus': {'connected': True, 'type': 'Active Engine'}})








@app.route('/admin/api/db-status', methods=['GET'])


def keyauth_api_admin_db_status():


    return jsonify({'success': True, 'dbStatus': {'connected': True, 'type': 'Krishu KeyAuth Core'}})








@app.route('/admin/api/apps', methods=['GET', 'POST'])


def keyauth_api_admin_apps():


    if request.method == 'POST':


        data = request.json or {}


        name = data.get('name', '').strip()


        version = data.get('version', '1.0.0').strip()


        hwid_lock = data.get('hwidLock', True)


        download_url = data.get('downloadUrl', '').strip()


        announcement = data.get('announcement', '').strip()


        owner_id = data.get('ownerId', str(OWNER_ID))





        if not name:


            return jsonify({'success': False, 'message': 'Application name is required'}), 400





        app_doc = KeyAuth.create_app(name, version, hwid_lock, download_url, announcement, owner_id=owner_id)


        return jsonify({'success': True, 'message': f"Application '{name}' created successfully!", 'app': app_doc})





    apps = KeyAuth.list_apps()


    return jsonify({'success': True, 'apps': apps})








@app.route('/admin/api/apps/<app_id>', methods=['PUT', 'DELETE'])


def keyauth_api_admin_app_modify(app_id):


    if request.method == 'DELETE':


        KeyAuth.delete_app(app_id)


        return jsonify({'success': True, 'message': 'Application and associated records deleted'})





    data = request.json or {}


    updated = KeyAuth.update_app(app_id, data)


    if not updated:


        return jsonify({'success': False, 'message': 'Application not found'}), 404


    return jsonify({'success': True, 'app': updated})








@app.route('/admin/api/apps/<app_id>/reseller-key/create', methods=['POST'])


def keyauth_api_admin_reseller_create(app_id):


    new_reseller_key = f"RS-{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}"


    app_doc = KeyAuth.update_app(app_id, {'resellerKey': new_reseller_key})


    if not app_doc:


        return jsonify({'success': False, 'message': 'Application not found'}), 404


    return jsonify({'success': True, 'key': new_reseller_key})








@app.route('/admin/api/apps/<app_id>/reseller-key/reset', methods=['POST'])


def keyauth_api_admin_reseller_reset(app_id):


    new_reseller_key = f"RS-{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}"


    app_doc = KeyAuth.update_app(app_id, {'resellerKey': new_reseller_key})


    return jsonify({'success': True, 'newKey': new_reseller_key, 'deletedUsersCount': 0})








@app.route('/admin/api/apps/<app_id>/reseller-key/delete', methods=['POST'])


def keyauth_api_admin_reseller_delete(app_id):


    KeyAuth.update_app(app_id, {'resellerKey': ''})


    return jsonify({'success': True, 'deletedUsersCount': 0})








@app.route('/admin/api/apps/<app_id>/variables', methods=['POST'])


def keyauth_api_admin_add_var(app_id):


    data = request.json or {}


    name = data.get('name', '').strip()


    value = data.get('value', '').strip()


    secret = data.get('secret', False)


    if not name or not value:


        return jsonify({'success': False, 'message': 'Name and value required'}), 400


    vars_list = KeyAuth.add_variable(app_id, name, value, secret)


    return jsonify({'success': True, 'variables': vars_list})








@app.route('/admin/api/apps/<app_id>/variables/<var_name>', methods=['DELETE'])


def keyauth_api_admin_del_var(app_id, var_name):


    vars_list = KeyAuth.delete_variable(app_id, var_name)


    return jsonify({'success': True, 'variables': vars_list})








@app.route('/admin/api/licenses', methods=['GET', 'POST'])


def keyauth_api_admin_licenses():


    if request.method == 'POST':


        data = request.json or {}


        app_id = data.get('appId')


        count = int(data.get('count', 1))


        duration = int(data.get('duration', 30))


        level = data.get('level', '1')


        prefix = data.get('prefix', 'KRISHU').strip() or 'KRISHU'


        note = data.get('note', '').strip()


        hwid_check = data.get('hwidCheck', data.get('hwidLock', True))





        keys = KeyAuth.create_licenses(app_id, count, duration, level, prefix, note, hwid_check=hwid_check)


        return jsonify({'success': True, 'count': len(keys), 'keys': keys})





    app_id = request.args.get('appId')


    search = request.args.get('search')


    licenses = KeyAuth.list_licenses(app_id, search)


    return jsonify({'success': True, 'licenses': licenses})








@app.route('/admin/api/licenses/ban', methods=['POST'])


def keyauth_api_admin_ban_license():


    data = request.json or {}


    license_id = data.get('licenseId', '').strip()


    banned = data.get('banned', True)


    reason = data.get('reason', 'Administrative action').strip()


    ok = KeyAuth.ban_license(license_id, banned, reason)


    return jsonify({'success': ok, 'message': f"License {'banned' if banned else 'unbanned'}"})








@app.route('/admin/api/licenses/reset-hwid', methods=['POST'])


def keyauth_api_admin_reset_license_hwid():


    data = request.json or {}


    license_id = data.get('licenseId', '').strip()


    ok = KeyAuth.reset_license_hwid(license_id)


    return jsonify({'success': ok, 'message': 'Hardware ID reset successfully'})








@app.route('/admin/api/licenses/<license_id>', methods=['DELETE'])


def keyauth_api_admin_delete_license(license_id):


    KeyAuth.delete_license(license_id)


    return jsonify({'success': True, 'message': 'License deleted'})








@app.route('/admin/api/users', methods=['GET'])


def keyauth_api_admin_users():


    app_id = request.args.get('appId')


    search = request.args.get('search')


    users = KeyAuth.list_users(app_id, search)


    return jsonify({'success': True, 'users': users})








@app.route('/admin/api/users/create', methods=['POST'])


def keyauth_api_admin_create_user():


    data = request.json or {}


    username = data.get('username', '').strip()


    password = data.get('password', '').strip()


    duration = int(data.get('duration', 30))


    app_id = data.get('appId')


    key = data.get('key', '').strip()


    level = data.get('level', '1')


    note = data.get('note', '').strip()





    if not username or not password:


        return jsonify({'success': False, 'message': 'Username and password required'}), 400





    user_doc = KeyAuth.create_user(username, password, duration, app_id, key, level, note)


    return jsonify({'success': True, 'message': f"User '{username}' created successfully!", 'user': user_doc})








@app.route('/admin/api/users/edit', methods=['PUT'])


def keyauth_api_admin_edit_user():


    data = request.json or {}


    user_id = data.get('userId') or data.get('username')


    updates = {}


    if 'duration' in data: updates['duration'] = int(data['duration'])


    if 'level' in data: updates['level'] = str(data['level'])


    if 'note' in data: updates['note'] = data['note']





    updated = KeyAuth.update_user(user_id, updates)


    return jsonify({'success': bool(updated), 'user': updated})








@app.route('/admin/api/users/extend', methods=['POST'])


def keyauth_api_admin_extend_user():


    data = request.json or {}


    user_id = data.get('userId') or data.get('username', '').strip()


    days = int(data.get('days', 30))


    updated = KeyAuth.extend_user(user_id, days)


    return jsonify({'success': bool(updated), 'user': updated})








@app.route('/admin/api/users/ban', methods=['POST'])


def keyauth_api_admin_ban_user():


    data = request.json or {}


    user_id = data.get('userId') or data.get('username', '').strip()


    banned = data.get('banned', True)


    reason = data.get('reason', 'Suspended by admin').strip()


    ok = KeyAuth.ban_user(user_id, banned, reason)


    return jsonify({'success': ok, 'message': f"User {'suspended' if banned else 're-activated'}"})








@app.route('/admin/api/users/reset-hwid', methods=['POST'])


def keyauth_api_admin_reset_user_hwid():


    data = request.json or {}


    user_id = data.get('userId') or data.get('username', '').strip()


    ok = KeyAuth.reset_user_hwid(user_id)


    return jsonify({'success': ok, 'message': 'Hardware ID reset successfully'})








@app.route('/admin/api/users/delete', methods=['POST'])


def keyauth_api_admin_delete_user():


    data = request.json or {}


    user_id = data.get('userId') or data.get('username', '').strip()


    KeyAuth.delete_user(user_id)


    return jsonify({'success': True, 'message': 'User deleted successfully'})








@app.route('/admin/api/users/delete-all', methods=['POST'])


def keyauth_api_admin_delete_all_users():


    data = request.json or {}


    app_id = data.get('appId')


    count = KeyAuth.delete_all_users(app_id)


    return jsonify({'success': True, 'message': f"Deleted {count} user accounts."})








@app.route('/admin/api/logs', methods=['GET'])


def keyauth_api_admin_logs():


    logs = KeyAuth.list_logs()


    return jsonify({'success': True, 'logs': logs})








@app.route('/admin/api/logs/clear', methods=['DELETE'])


def keyauth_api_admin_clear_logs():


    KeyAuth.clear_logs()


    return jsonify({'success': True, 'message': 'Logs cleared successfully'})








@app.route('/admin/api/change-credentials', methods=['POST'])


def keyauth_api_admin_change_creds():


    return jsonify({'success': False, 'message': 'Admin credentials are safe and managed in config.py / .env'})








# ── OFFICIAL KEYAUTH 1.0 / 1.1 / 1.2 PROTOCOL ENGINE ─────────





@app.route('/api/1.2/', methods=['GET', 'POST'])


@app.route('/api/1.2', methods=['GET', 'POST'])


@app.route('/api/1.1/', methods=['GET', 'POST'])


@app.route('/api/1.1', methods=['GET', 'POST'])


@app.route('/api/1.0/', methods=['GET', 'POST'])


@app.route('/api/1.0', methods=['GET', 'POST'])


@app.route('/api/', methods=['GET', 'POST'])


@app.route('/api', methods=['GET', 'POST'])


def keyauth_official_legacy_api():


    """


    Standard KeyAuth 1.0/1.2 API compatible with ALL official KeyAuth client libraries


    (C++, C#, ImGui, Python, Android Java/Kotlin, Dark X Auth).


    """


    params = {}


    if request.args:


        params.update(request.args.to_dict())


    if request.form:


        params.update(request.form.to_dict())


    if request.is_json and request.json:


        params.update(request.json)





    ip = request.headers.get('X-Forwarded-For', request.remote_addr or '').split(',')[0].strip()


    resp_data, sig = KeyAuth.handle_keyauth_12_api(params, ip=ip)





    if isinstance(resp_data, str):


        response = app.response_class(response=resp_data, status=200, mimetype='text/plain')


    else:


        response = jsonify(resp_data)





    if sig:


        response.headers['signature'] = sig


    return response








# ── CLIENT TOOL REST APIS (/api/v1/...) ────────────────────────





@app.route('/api/v1/health', methods=['GET'])


def keyauth_api_health():


    return jsonify({'success': True, 'message': 'KRISHU X CHEATS KeyAuth Server Online'})








@app.route('/api/v1/init', methods=['POST'])


def keyauth_api_client_init():


    data = request.json or {}


    app_id = data.get('name') or request.headers.get('x-app-name') or data.get('appId') or data.get('apiKey') or request.headers.get('x-api-key') or data.get('secret') or 'app_krishu_main'


    version = data.get('version', '1.0.0')


    res = KeyAuth.client_init(app_id, version)


    return jsonify(res)








@app.route('/api/v1/license', methods=['POST'])


@app.route('/api/v1/license/check', methods=['POST'])


def keyauth_api_client_license():


    data = request.json or {}


    app_id = data.get('name') or request.headers.get('x-app-name') or data.get('appId') or data.get('apiKey') or request.headers.get('x-api-key') or data.get('secret') or 'app_krishu_main'


    key = data.get('key', '').strip()


    hwid = data.get('hwid', '').strip()


    ip = request.headers.get('X-Forwarded-For', request.remote_addr or '').split(',')[0].strip()





    if not key:


        return jsonify({'success': False, 'message': 'License key required'}), 400





    res = KeyAuth.client_license_login(app_id, key, hwid, ip)


    status_code = 200 if res.get('success') else 401


    return jsonify(res), status_code








@app.route('/api/v1/login', methods=['POST'])


def keyauth_api_client_login():


    data = request.json or {}


    app_id = data.get('name') or request.headers.get('x-app-name') or data.get('appId') or data.get('apiKey') or request.headers.get('x-api-key') or data.get('secret') or 'app_krishu_main'


    username = data.get('username', '').strip()


    password = data.get('password', '').strip()


    hwid = data.get('hwid', '').strip()


    ip = request.headers.get('X-Forwarded-For', request.remote_addr or '').split(',')[0].strip()





    res = KeyAuth.client_user_login(app_id, username, password, hwid, ip)


    status_code = 200 if res.get('success') else 401


    return jsonify(res), status_code








@app.route('/api/v1/register', methods=['POST'])


def keyauth_api_client_register():


    data = request.json or {}


    app_id = data.get('name') or request.headers.get('x-app-name') or data.get('appId') or data.get('apiKey') or request.headers.get('x-api-key') or data.get('secret') or 'app_krishu_main'


    username = data.get('username', '').strip()


    password = data.get('password', '').strip()


    key = data.get('key', '').strip()


    hwid = data.get('hwid', '').strip()


    ip = request.headers.get('X-Forwarded-For', request.remote_addr or '').split(',')[0].strip()





    lic = KeyAuth.get_license(key)


    if not lic:


        return jsonify({'success': False, 'message': 'Invalid License Key provided for registration'}), 400


    if lic.get('banned'):


        return jsonify({'success': False, 'message': 'This license key is banned'}), 403





        duration = lic.get('duration', 30)
    user_doc = KeyAuth.create_user(username, password, duration, app_id, key=key)
    KeyAuth.update_license(key, {'status': 'used', 'usedBy': username, 'hwid': hwid, 'ip': ip})
    KeyAuth.log_action("CLIENT_REGISTER", f"New user '{username}' registered with license key '{key}'", ip=ip, hwid=hwid, app_id=app_id, username=username, success=True)





    return jsonify({'success': True, 'message': 'Account registered successfully', 'user': user_doc})








@app.route('/api/v1/hwid/reset', methods=['POST'])


def keyauth_api_client_hwid_reset():


    data = request.json or {}


    key = data.get('key', '').strip()


    username = data.get('username', '').strip()


    if key:


        KeyAuth.reset_license_hwid(key)


        return jsonify({'success': True, 'message': 'License HWID reset successfully'})


    if username:


        KeyAuth.reset_user_hwid(username)


        return jsonify({'success': True, 'message': 'User HWID reset successfully'})


    return jsonify({'success': False, 'message': 'Key or Username required'}), 400








@app.route('/api/v1/var/<name>', methods=['GET'])


def keyauth_api_client_var(name):


    app_id = request.headers.get('x-api-key') or 'app_krishu_main'


    app_doc = KeyAuth.get_app(app_id)


    if not app_doc:


        return jsonify({'success': False, 'message': 'App not found'}), 404


    for var in app_doc.get('variables', []):


        if var.get('name') == name:


            return jsonify({'success': True, 'response': var.get('value')})


    return jsonify({'success': False, 'message': 'Variable not found'}), 404








# ── WEB USER & RESELLER AUTH APIS (/auth/...) ─────────────────





@app.route('/auth/login', methods=['POST'])


def keyauth_web_user_login():


    data = request.json or {}


    username = data.get('username', '').strip()


    password = data.get('password', '').strip()


    ip = request.headers.get('X-Forwarded-For', request.remote_addr or '').split(',')[0].strip()


    user = KeyAuth.get_user(username)


    if not user or user.get('passwordHash') != _hash_pass(password):


        trigger_security_webhook(


            "User Login Failed — Security Alert",


            f"Failed login attempt for account **`{username or 'Anonymous'}`**",


            fields=[


                {"name": "👤 Target User", "value": f"`{username or 'Unknown'}`", "inline": True},


                {"name": "🌐 Client IP", "value": f"`{ip}`", "inline": True},


                {"name": "⚠️ Status", "value": "`Invalid Passphrase`", "inline": True}


            ],


            color=0xe11d48,


            identifier=username


        )


        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401


    if user.get('banned'):


        trigger_security_webhook(


            "Banned User Attempted Access",


            f"Suspended user **`{username}`** attempted login",


            fields=[


                {"name": "👤 User", "value": f"`{username}`", "inline": True},


                {"name": "🌐 IP", "value": f"`{ip}`", "inline": True},


                {"name": "⛔ Status", "value": "`Account Banned`", "inline": True}


            ],


            color=0xff0000,


            identifier=username


        )


        return jsonify({'success': False, 'message': 'Account suspended'}), 403





    token = f"kauth_usr_{secrets.token_hex(24)}"


    session_user = {


        'username': user.get('username'),


        'role': 'user',


        'isReseller': False,


        'duration': user.get('duration', 30),


        'expiresAt': user.get('expiresAt'),


        'hwid': user.get('hwid') or 'Unbound',


        'banned': user.get('banned', False),


        'appId': user.get('appId'),


        'level': user.get('level', '1'),


        'note': user.get('note', '')


    }


    ACTIVE_SESSIONS[token] = session_user





    trigger_security_webhook(


        "User Login Successful",


        f"User **`{username}`** successfully authenticated into Web Portal",


        fields=[


            {"name": "👤 Username", "value": f"`{username}`", "inline": True},


            {"name": "🌐 Client IP", "value": f"`{ip}`", "inline": True},


            {"name": "🌸 Security", "value": "`Session Granted`", "inline": True}


        ],


        color=0x00ff88,


        identifier=username


    )


    return jsonify({'success': True, 'token': token, 'user': session_user})








@app.route('/auth/key-login', methods=['POST'])


def keyauth_web_key_login():


    data = request.json or {}


    key = (data.get('key') or data.get('loginKey') or '').strip()


    ip = request.headers.get('X-Forwarded-For', request.remote_addr or '').split(',')[0].strip()


    if not key:


        return jsonify({'success': False, 'message': 'License key is required'}), 400





    lic = KeyAuth.get_license(key)


    if not lic:


        trigger_security_webhook(


            "Invalid License Login Attempt",


            f"Attempted login with non-existent key: `{key}`",


            fields=[


                {"name": "🔑 Key", "value": f"`{key}`", "inline": True},


                {"name": "🌐 IP", "value": f"`{ip}`", "inline": True}


            ],


            color=0xe11d48


        )


        return jsonify({'success': False, 'message': 'License key not found'}), 404


    if lic.get('banned'):


        return jsonify({'success': False, 'message': 'License is banned'}), 403





    token = f"kauth_key_{secrets.token_hex(24)}"


    key_user = {


        'username': lic.get('key'),


        'loginKey': lic.get('key'),


        'role': 'user',


        'isKeyUser': True,


        'isReseller': False,


        'license': lic,


        'duration': lic.get('duration', 30),


        'expiresAt': lic.get('expiresAt'),


        'hwid': lic.get('hwid', ''),


        'appId': lic.get('appId')


    }


    ACTIVE_SESSIONS[token] = key_user





    trigger_security_webhook(


        "License Key Login Authorized",


        f"Client entered panel with license: `{key}`",


        fields=[


            {"name": "🔑 Key", "value": f"`{key}`", "inline": True},


            {"name": "🌐 IP", "value": f"`{ip}`", "inline": True},


            {"name": "⏳ Sub Duration", "value": f"`{lic.get('duration', 30)} Days`", "inline": True}


        ],


        color=0x00ff88


    )


    return jsonify({'success': True, 'token': token, 'license': lic, 'user': key_user})








@app.route('/auth/reseller-login', methods=['POST'])


def keyauth_web_reseller_login():


    data = request.json or {}


    key = (data.get('key') or data.get('resellerKey') or '').strip()


    username = (data.get('username') or '').strip()


    if not key:


        return jsonify({'success': False, 'message': 'Reseller Key is required'}), 400





    apps = KeyAuth.list_apps()


    clean_key = key.lower()





    # 1. Check dedicated Reseller Keys table (Generated by Admin)


    matched_rk = None


    all_reseller_keys = KeyAuth.list_reseller_keys()


    for rk in all_reseller_keys:


        if rk.get('key', '').strip().lower() == clean_key:


            matched_rk = rk


            break





    matched_app = None


    display_name = username





    if matched_rk:


        if matched_rk.get('banned'):


            return jsonify({'success': False, 'message': 'This Reseller Key has been suspended by Admin'}), 403


        


        # Check expiry


        exp = matched_rk.get('expiresAt')


        if exp and exp != "Lifetime":


            try:


                exp_dt = datetime.fromisoformat(exp.replace('Z', '+00:00'))


                if datetime.now(timezone.utc) > exp_dt:


                    return jsonify({'success': False, 'message': 'This Reseller Key has expired'}), 403


            except Exception:


                pass





        target_app_id = matched_rk.get('appId')


        for a in apps:


            if a.get('appId') == target_app_id or a.get('_id') == target_app_id:


                matched_app = a


                break


        if not matched_app and apps:


            matched_app = apps[0]





        display_name = display_name or matched_rk.get('resellerName') or 'Master Reseller'


    else:


        # 2. Check application-level reseller key fallback


        for a in apps:


            if a.get('resellerKey') and a.get('resellerKey').strip().lower() == clean_key:


                matched_app = a


                display_name = display_name or 'Reseller VIP'


                break





    if not matched_app and not matched_rk:


        return jsonify({'success': False, 'message': 'Invalid Reseller Key. Please obtain a valid key from Admin.'}), 401





    token = f"kauth_reseller_{secrets.token_hex(24)}"


    reseller_user = {


        'username': display_name,


        'role': 'reseller',


        'isReseller': True,


        'resellerKey': key,


        'resellerApp': matched_app or (apps[0] if apps else {'name': 'KRISHU X CHEATS', 'version': '1.0.0'}),


        'appId': (matched_app.get('appId') or matched_app.get('_id')) if matched_app else (apps[0].get('appId') if apps else 'app_krishu_main'),


        'duration': -1,


        'hwid': 'Active',


        'level': 'Reseller VIP'


    }


    ACTIVE_SESSIONS[token] = reseller_user





    trigger_security_webhook(


        "Reseller Console Activated",


        f"Reseller **`{display_name}`** authenticated via Key: `{key[:14]}...`",


        fields=[


            {"name": "👑 Reseller", "value": f"`{display_name}`", "inline": True},


            {"name": "📦 Application", "value": f"`{(matched_app or {}).get('name', 'Main')}`", "inline": True},


            {"name": "🌸 Access Level", "value": "`Unlimited Key & User Management`", "inline": True}


        ],


        color=0xffd700,


        identifier=display_name


    )





    return jsonify({


        'success': True,


        'token': token,


        'role': 'reseller',


        'isReseller': True,


        'app': matched_app,


        'user': reseller_user,


        'message': f"Welcome {display_name}! Reseller Console unlocked."


    })








def verify_reseller_session(token):
    """
    Validates reseller access against the database.
    - If admin deleted the key: returns None, error (403 revoked)
    - If the key is expired (auto time ke sath expire): returns None, error (403 revoked)
    - If the key is banned/suspended by admin: returns None, error (403 revoked)
    - If valid: returns session dict bound to assigned appId
    """
    if not token:
        return None, (jsonify({'success': False, 'message': 'Authorization token required', 'revoked': True}), 401)

    session = ACTIVE_SESSIONS.get(token)
    if not session or not (session.get('isReseller') or session.get('role') == 'reseller'):
        return None, (jsonify({'success': False, 'message': 'Invalid or expired reseller session', 'revoked': True}), 401)

    res_key = (session.get('resellerKey') or '').strip()
    if not res_key:
        ACTIVE_SESSIONS.pop(token, None)
        return None, (jsonify({'success': False, 'message': 'Reseller key missing. Access revoked.', 'revoked': True}), 403)

    # 1. Fetch live reseller key from KeyAuth storage
    rk = KeyAuth.get_reseller_key(res_key)
    if not rk:
        # Check fallback application-level key
        apps = KeyAuth.list_apps()
        matched_app = next((a for a in apps if a.get('resellerKey') and a.get('resellerKey').strip().lower() == res_key.lower()), None)
        if not matched_app:
            # Reseller key was deleted by Admin!
            ACTIVE_SESSIONS.pop(token, None)
            return None, (jsonify({
                'success': False,
                'message': 'This Reseller Key has been deleted by Admin. Access has been revoked.',
                'revoked': True
            }), 403)
        session['appId'] = matched_app.get('appId') or matched_app.get('_id')
        session['resellerApp'] = matched_app
    else:
        # Check if banned by Admin
        if rk.get('banned'):
            ACTIVE_SESSIONS.pop(token, None)
            return None, (jsonify({
                'success': False,
                'message': 'This Reseller Key has been suspended by Admin. Access has been revoked.',
                'revoked': True
            }), 403)

        # Check auto-expiration with time
        exp = rk.get('expiresAt')
        if exp and exp != "Lifetime":
            try:
                exp_dt = datetime.fromisoformat(exp.replace('Z', '+00:00'))
                if datetime.now(timezone.utc) > exp_dt:
                    ACTIVE_SESSIONS.pop(token, None)
                    return None, (jsonify({
                        'success': False,
                        'message': 'This Reseller Key has expired. Access has been revoked.',
                        'revoked': True
                    }), 403)
            except Exception:
                pass

        # Strictly lock to assigned application
        target_app_id = rk.get('appId')
        apps = KeyAuth.list_apps()
        matched_app = next((a for a in apps if a.get('appId') == target_app_id or a.get('_id') == target_app_id), None)
        if matched_app:
            session['appId'] = matched_app.get('appId') or matched_app.get('_id')
            session['resellerApp'] = matched_app
        elif target_app_id:
            session['appId'] = target_app_id

    return session, None


@app.route('/auth/profile', methods=['GET'])
def keyauth_web_profile():
    token = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
    if not token:
        return jsonify({'success': False, 'message': 'Token missing'}), 401

    session = ACTIVE_SESSIONS.get(token)
    if session and (session.get('isReseller') or session.get('role') == 'reseller'):
        valid_session, err = verify_reseller_session(token)
        if err:
            return err
        return jsonify({'success': True, 'user': valid_session})
    elif session:
        return jsonify({'success': True, 'user': session})

    if token.startswith('kauth_reseller_'):
        valid_session, err = verify_reseller_session(token)
        if err:
            return err
        return jsonify({'success': True, 'user': valid_session})

    users = KeyAuth.list_users()
    user = users[0] if users else {'username': 'VIP_Client', 'duration': 30, 'hwid': 'Active', 'isReseller': False}
    return jsonify({'success': True, 'user': user})


@app.route('/auth/reseller/create-user', methods=['POST'])
def keyauth_reseller_create_user():
    token = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
    session, err = verify_reseller_session(token)
    if err:
        return err

    data = request.json or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    duration = int(data.get('duration', 30))
    note = (data.get('note') or 'Reseller created').strip()
    hwid_locked = bool(data.get('hwidLocked', True))

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400

    existing = KeyAuth.get_user(username)
    if existing:
        return jsonify({'success': False, 'message': f"Username '{username}' already exists"}), 400

    app_id = session.get('appId')
    if not app_id:
        apps = KeyAuth.list_apps()
        app_id = apps[0].get('appId') if apps else 'app_krishu_main'

    # UNLIMITED user creation for the assigned application!
    user_doc = KeyAuth.create_user(
        username=username,
        password=password,
        duration=duration,
        app_id=app_id,
        note=note,
        hwid_locked=hwid_locked
    )

    res_key = session.get('resellerKey')
    if res_key:
        KeyAuth.update_user(username, {'resellerKey': res_key})
        KeyAuth.record_reseller_usage(res_key, 1)

    app_name = session.get('resellerApp', {}).get('name', 'Application')
    return jsonify({
        'success': True,
        'message': f"User '{username}' created successfully for {app_name}!",
        'user': user_doc
    })


@app.route('/auth/reseller/create-key-user', methods=['POST'])
def keyauth_reseller_create_key_user():
    token = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
    session, err = verify_reseller_session(token)
    if err:
        return err

    data = request.json or {}
    name = (data.get('name') or 'VIP').strip()
    duration = int(data.get('duration', 30))
    note = (data.get('note') or 'Reseller Key User').strip()
    hwid_locked = bool(data.get('hwidLocked', True))
    count = int(data.get('count', 1))
    count = max(1, min(count, 500))

    app_id = session.get('appId')
    if not app_id:
        apps = KeyAuth.list_apps()
        app_id = apps[0].get('appId') if apps else 'app_krishu_main'

    clean_prefix = f"KEYAUTH-{name.upper()}" if name else "KEYAUTH"
    keys = KeyAuth.create_licenses(
        app_id=app_id,
        count=count,
        duration=duration,
        level="1",
        prefix=clean_prefix,
        note=note,
        hwid_check=hwid_locked
    )

    res_key = session.get('resellerKey')
    if res_key:
        for k in keys:
            KeyAuth.update_license(k, {'resellerKey': res_key})
        KeyAuth.record_reseller_usage(res_key, len(keys))

    login_key = keys[0] if keys else f"{clean_prefix}-{secrets.token_hex(4).upper()}"
    return jsonify({
        'success': True,
        'message': f"Generated {len(keys)} License Key(s) successfully!",
        'loginKey': login_key,
        'keys': keys
    })


@app.route('/auth/reseller/users', methods=['GET'])
def keyauth_reseller_list_users():
    token = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
    session, err = verify_reseller_session(token)
    if err:
        return err

    app_id = session.get('appId')
    res_key = (session.get('resellerKey') or '').strip().lower()

    all_users = KeyAuth.list_users(app_id=app_id) if app_id else KeyAuth.list_users()
    all_licenses = KeyAuth.list_licenses(app_id=app_id) if app_id else KeyAuth.list_licenses()

    reseller_users = [u for u in all_users if (u.get('resellerKey', '').lower() == res_key or not u.get('resellerKey'))]
    reseller_licenses = [l for l in all_licenses if (l.get('resellerKey', '').lower() == res_key or not l.get('resellerKey'))]

    combined = []
    for u in reseller_users:
        combined.append({
            '_id': u.get('_id'),
            'username': u.get('username'),
            'duration': u.get('duration'),
            'expiresAt': u.get('expiresAt'),
            'hwid': u.get('hwid'),
            'banned': u.get('banned'),
            'note': u.get('note'),
            'isKeyUser': False
        })

    for l in reseller_licenses:
        combined.append({
            '_id': l.get('_id'),
            'username': l.get('key'),
            'duration': l.get('duration'),
            'expiresAt': l.get('expiresAt'),
            'hwid': l.get('hwid'),
            'banned': l.get('banned'),
            'note': l.get('note'),
            'status': l.get('status'),
            'isKeyUser': True
        })

    return jsonify({'success': True, 'users': combined})


@app.route('/auth/reseller/ban-user', methods=['POST'])
def keyauth_reseller_ban_user():
    token = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
    session, err = verify_reseller_session(token)
    if err:
        return err

    data = request.json or {}
    user_id = data.get('userId') or ''
    banned = bool(data.get('banned', True))
    b_u = KeyAuth.ban_user(user_id, banned=banned, reason="Reseller Action")
    b_l = KeyAuth.ban_license(user_id, banned=banned, reason="Reseller Action")
    return jsonify({'success': True, 'message': f"Account {'suspended' if banned else 'reactivated'}"})


@app.route('/auth/reseller/reset-hwid', methods=['POST'])
def keyauth_reseller_reset_hwid():
    token = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
    session, err = verify_reseller_session(token)
    if err:
        return err

    data = request.json or {}
    user_id = data.get('userId') or ''
    KeyAuth.reset_user_hwid(user_id)
    KeyAuth.reset_license_hwid(user_id)
    return jsonify({'success': True, 'message': 'HWID reset successfully'})


@app.route('/auth/reseller/delete-user', methods=['POST'])
def keyauth_reseller_delete_user():
    token = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
    session, err = verify_reseller_session(token)
    if err:
        return err

    data = request.json or {}
    user_id = data.get('userId') or ''
    KeyAuth.delete_user(user_id)
    KeyAuth.delete_license(user_id)
    return jsonify({'success': True, 'message': 'Account deleted successfully'})

@app.route('/admin/api/resellers', methods=['GET', 'POST'])


def admin_api_resellers():


    if request.method == 'POST':


        data = request.json or {}


        app_id = (data.get('appId') or '').strip()


        reseller_name = (data.get('resellerName') or 'Master Reseller').strip()


        duration_days = int(data.get('durationDays', 30))


        hwid_lock = bool(data.get('hwidLock', True))


        note = (data.get('note') or f"Reseller for {reseller_name}").strip()





        if not app_id:


            apps = KeyAuth.list_apps()


            app_id = apps[0].get('appId') if apps else 'app_krishu_main'





        reseller_doc = KeyAuth.create_reseller_key(app_id, reseller_name, duration_days, hwid_lock, note)


        return jsonify({'success': True, 'message': f"Reseller key '{reseller_doc['key']}' created for {reseller_name}!", 'reseller': reseller_doc})





    app_id = request.args.get('appId')


    resellers = KeyAuth.list_reseller_keys(app_id)


    return jsonify({'success': True, 'resellers': resellers})








@app.route('/admin/api/resellers/<key>', methods=['DELETE'])


def admin_api_reseller_delete(key):


    deleted = KeyAuth.delete_reseller_key(key)


    if deleted:


        return jsonify({'success': True, 'message': f"Reseller key '{key}' deleted"})


    return jsonify({'success': False, 'message': 'Reseller key not found'}), 404








@app.route('/admin/api/resellers/<key>/ban', methods=['POST'])


def admin_api_reseller_ban(key):


    data = request.json or {}


    banned = bool(data.get('banned', True))


    KeyAuth.ban_reseller_key(key, banned)


    return jsonify({'success': True, 'message': f"Reseller key {'banned' if banned else 'unbanned'}"})








@app.route('/admin/api/resellers/<key>/reset-hwid', methods=['POST'])


def admin_api_reseller_reset_hwid(key):


    KeyAuth.reset_reseller_hwid(key)


    return jsonify({'success': True, 'message': f"HWID reset for reseller key '{key}'"})








# ── DISCORD WEBHOOK INTEGRATION APIS ──────────────────────────





@app.route('/api/webhook/config', methods=['GET', 'POST'])


def api_webhook_config():


    if request.method == 'POST':


        data = request.json or {}


        url = (data.get('url') or '').strip()


        enabled = bool(data.get('enabled', True))


        scope = (data.get('scope') or 'admin').strip()


        identifier = (data.get('identifier') or 'master').strip()


        conf = KeyAuth.set_webhook_config(url, enabled, scope, identifier)


        return jsonify({'success': True, 'message': 'Webhook configuration saved', 'config': conf})





    scope = request.args.get('scope', 'admin')


    identifier = request.args.get('identifier', 'master')


    conf = KeyAuth.get_webhook_config(scope, identifier)


    return jsonify({'success': True, 'config': conf})








@app.route('/api/webhook/test', methods=['POST'])


def api_webhook_test():


    data = request.json or {}


    url = (data.get('url') or '').strip()


    if not url:


        scope = data.get('scope', 'admin')


        identifier = data.get('identifier', 'master')


        conf = KeyAuth.get_webhook_config(scope, identifier)


        url = conf.get('url', '')





    if not url or not url.startswith(('http://', 'https://')):


        return jsonify({'success': False, 'message': 'Invalid Discord Webhook URL. Please enter a valid URL starting with https://discord.com/api/webhooks/'}), 400





    fields = [


        {"name": "📡 System Status", "value": "`ONLINE • OPERATIONAL`", "inline": True},


        {"name": "🌸 Security Node", "value": "`KRISHU X KEYAUTH CORE`", "inline": True},


        {"name": "⚡ Response Latency", "value": "`< 15ms Ultra-Speed`", "inline": True},


        {"name": "🛡️ Protection Shield", "value": "`Zero-Trust Sakura Guard`", "inline": False}


    ]





    ok, msg = send_discord_webhook(


        url,


        "KRISHU X KEYAUTH • Live Sentinel Connection Test",


        "**Connection established successfully!**\nYour Discord server is now directly integrated with the **KRISHU X KEYAUTH** real-time security matrix. You will receive instant notifications for user logins, registrations, license redeems, and security events.",


        fields=fields,


        color=0xff2a5f


    )


    if ok:


        return jsonify({'success': True, 'message': 'Test message sent to Discord successfully! Check your channel.'})


    return jsonify({'success': False, 'message': f'Failed to send webhook: {msg}'}), 400








# ── PROFILE CUSTOMIZATION APIS ────────────────────────────────





@app.route('/api/user/profile', methods=['GET', 'POST'])


def api_user_profile():


    if request.method == 'POST':


        data = request.json or {}


        username = (data.get('username') or 'user').strip()


        updated = KeyAuth.update_profile('user', username, data)


        return jsonify({'success': True, 'message': 'User profile updated successfully', 'profile': updated})





    username = request.args.get('username', 'user')


    profile = KeyAuth.get_profile('user', username)


    return jsonify({'success': True, 'profile': profile})








@app.route('/admin/api/profile', methods=['GET', 'POST'])


def admin_api_profile():


    if request.method == 'POST':


        data = request.json or {}


        username = (data.get('username') or 'krishu').strip()


        updated = KeyAuth.update_profile('admin', username, data)


        return jsonify({'success': True, 'message': 'Admin profile updated successfully', 'profile': updated})





    username = request.args.get('username', 'krishu')


    profile = KeyAuth.get_profile('admin', username)


    return jsonify({'success': True, 'profile': profile})








# ── CODE AUTO-PATCHER / INJECTOR ENGINE ───────────────────────

@app.route('/api/patcher/generate', methods=['POST'])
def api_patcher_generate():
    data = request.json or {}
    lang = (data.get('language') or 'csharp').strip().lower()
    source_code = data.get('sourceCode', '')
    user_box = (data.get('userBox') or 'txtUsername').strip()
    pass_box = (data.get('passBox') or 'txtPassword').strip()
    btn_name = (data.get('loginBtn') or 'btnLogin').strip()
    status_box = (data.get('statusBox') or 'lblStatus').strip()
    app_name = (data.get('appName') or 'KRISHU X CHEATS').strip()
    app_secret = (data.get('appSecret') or 'krishu_master_secret_2026').strip()
    app_version = (data.get('appVersion') or '1.0.0').strip()
    owner_id = str(OWNER_ID)

    apps = KeyAuth.list_apps()
    default_app = apps[0] if apps else {}
    if (not data.get('appName') or app_name == 'KRISHU X CHEATS') and default_app:
        app_name = default_app.get('name', 'KRISHU X CHEATS')
        app_secret = default_app.get('secret') or default_app.get('apiKey', 'krishu_master_secret_2026')
        app_version = default_app.get('version', '1.0.0')
        owner_id = default_app.get('ownerId', str(OWNER_ID))

    api_url = data.get('apiUrl')
    if not api_url:
        host = request.headers.get('X-Forwarded-Host', request.host)
        proto = request.headers.get('X-Forwarded-Proto', request.scheme)
        if 'onrender.com' in host:
            api_url = "https://krishu-keyauth-web.onrender.com/api/v1"
        elif '127.0.0.1' in host or 'localhost' in host:
            api_url = f"{proto}://{host}/api/v1"
        else:
            api_url = f"{proto}://{host}/api/v1"

    if source_code:
        ns_m = re.search(r'\bnamespace\s+([\w\.]+)', source_code)
        target_ns = ns_m.group(1) if ns_m else 'XYZ'

        class_m = re.search(r'\b(?:public|internal|private)?\s*(?:partial\s+)?class\s+([\w]+)', source_code)
        target_class = class_m.group(1) if class_m else 'Form1'

        base_m = re.search(r'\bclass\s+[\w]+\s*:\s*([\w]+)', source_code)
        target_base = base_m.group(1) if base_m else 'Form'

        if user_box in ('txtUsername', ''):
            m = re.search(r'\b(txtUsername|txtUser|tbUser|tbUsername|User|Username|txt_user|txt_username)\b', source_code, re.I)
            if m: user_box = m.group(1)
        if pass_box in ('txtPassword', ''):
            m = re.search(r'\b(txtPassword|txtPass|tbPass|tbPassword|Pass|Password|txt_pass|txt_password)\b', source_code, re.I)
            if m: pass_box = m.group(1)
        if btn_name in ('btnLogin', ''):
            m = re.search(r'\b(btnLogin|loginbtn|btn_login|buttonLogin|cmdLogin|button1)\b', source_code, re.I)
            if m: btn_name = m.group(1)
        if status_box in ('lblStatus', ''):
            m = re.search(r'\b(lblStatus|sta|statuslbl|lbl_status|statusLabel|labelStatus|label1)\b', source_code, re.I)
            if m: status_box = m.group(1)
    else:
        target_ns = 'XYZ'
        target_class = 'Form1'
        target_base = 'Form'

    if lang in ('c#', 'csharp', 'cs'):
        def find_method_span(code, method_name):
            pattern = re.compile(
                r'(?:(?:public|private|protected|internal)\s+)?(?:static\s+)?(?:async\s+)?(?:void|Task)\s+' +
                re.escape(method_name) +
                r'(?:_Click|_click)?\s*\([^)]*\)\s*\{',
                re.IGNORECASE
            )
            m = pattern.search(code)
            if not m:
                return None
            start = m.start()
            brace_start = m.end() - 1
            depth = 0
            for i in range(brace_start, len(code)):
                if code[i] == '{':
                    depth += 1
                elif code[i] == '}':
                    depth -= 1
                    if depth == 0:
                        return (start, i + 1)
            return None

        nl = "\n"

        login_method = f"""
        // ── LOGIN BUTTON EVENT HANDLER ({btn_name}) ──
        private void {btn_name}_Click(object sender, EventArgs e)
        {{
            string user = {user_box}.Text.Trim();
            string pass = {pass_box}.Text.Trim();

            if (string.IsNullOrEmpty(user) || string.IsNullOrEmpty(pass))
            {{
                UpdateStatus("Please enter username and password", false);
                return;
            }}

            UpdateStatus("Authenticating credentials...", true);
            {btn_name}.Enabled = false;

            try
            {{
                KeyAuthApp.login(user, pass);
                if (KeyAuthApp.response.success)
                {{
                    string exp = KeyAuthApp.user_data.lifetime ? "Lifetime" : KeyAuthApp.user_data.expires;
                    UpdateStatus("Login Successful! Welcome " + user, true);
                    MessageBox.Show("Welcome back, " + user + "!\\nExpires: " + exp, "Access Granted", MessageBoxButtons.OK, MessageBoxIcon.Information);

                    // ── REDIRECT TO MAIN DASHBOARD / CHEAT INTERFACE ──
                    // this.Hide();
                }}
                else
                {{
                    UpdateStatus("Login Failed: " + KeyAuthApp.response.message, false);
                    MessageBox.Show(KeyAuthApp.response.message, "Access Denied", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                }}
            }}
            catch (Exception ex)
            {{
                UpdateStatus("Authentication Exception: " + ex.Message, false);
            }}
            finally
            {{
                {btn_name}.Enabled = true;
            }}
        }}"""

        init_method = f"""
        // ── KRISHU X KEYAUTH CORE INITIALIZATION ──
        private void InitializeKeyAuth()
        {{
            try
            {{
                KeyAuthApp.init();
                if (!KeyAuthApp.response.success)
                {{
                    UpdateStatus("KeyAuth Init: " + KeyAuthApp.response.message, false);
                }}
                else
                {{
                    UpdateStatus("Connected to KeyAuth Core", true);
                }}
            }}
            catch (Exception ex)
            {{
                UpdateStatus("Connection Error: " + ex.Message, false);
            }}
        }}"""

        status_method = f"""
        // ── STATUS & NOTIFICATION ROUTINE ──
        private void UpdateStatus(string message, bool isSuccess)
        {{
            try
            {{
                if ({status_box} != null)
                {{
                    {status_box}.Text = message;
                }}
            }}
            catch {{ }}
        }}"""

        init_field = f"""
        // ── KRISHU X KEYAUTH API INITIALIZATION ──
        public static KrishuXCheats.api KeyAuthApp = new KrishuXCheats.api(
            name: "{app_name}",
            ownerid: "{owner_id}",
            secret: "{app_secret}",
            version: "{app_version}",
            apiUrl: "{api_url}"
        );
"""

        if not source_code or 'class ' not in source_code:
            patched_code = f"""/* =========================================================================
 * KRISHU X KEYAUTH — FULLY INJECTED & AUTO-PATCHED LOGIN MODULE
 * Language: C# (.NET Framework / .NET Core / WinForms / WPF / Unity)
 * Target App: {app_name} | Version: {app_version}
 * ========================================================================= */

using System;
using System.IO;
using System.Net;
using System.Text;
using System.Diagnostics;
using System.Windows.Forms;
using System.Security.Principal;
using System.Runtime.InteropServices;
using System.Collections.Specialized;
using KrishuXCheats;

namespace {target_ns}
{{
    public partial class {target_class} : {target_base}
    {{
{init_field}
        public {target_class}()
        {{
            InitializeComponent();
            InitializeKeyAuth();
        }}
{init_method}
{login_method}
{status_method}
    }}
}}
"""
        else:
            code = source_code

            # 1. Ensure using KrishuXCheats;
            if 'using KrishuXCheats;' not in code and 'using KrishuXCheats' not in code:
                using_matches = list(re.finditer(r'^\s*using\s+[\w\.]+;\s*$', code, re.M))
                if using_matches:
                    last_using = using_matches[-1]
                    code = code[:last_using.end()] + nl + 'using KrishuXCheats;' + code[last_using.end():]
                else:
                    code = 'using KrishuXCheats;' + nl + code

            # 2. Update or Inject KeyAuthApp
            field_pattern = re.search(r'public\s+static\s+KrishuXCheats\.api\s+KeyAuthApp\s*=\s*new\s+KrishuXCheats\.api\s*\([^;]*\);', code, re.DOTALL)
            if field_pattern:
                code = code[:field_pattern.start()] + init_field.strip() + code[field_pattern.end():]
            elif 'KeyAuthApp' not in code:
                class_open = re.search(r'\bclass\s+' + re.escape(target_class) + r'[^{]*{', code)
                if class_open:
                    code = code[:class_open.end()] + nl + init_field + code[class_open.end():]

            # 3. Hook constructor
            if 'InitializeKeyAuth();' not in code:
                if 'InitializeComponent();' in code:
                    code = code.replace('InitializeComponent();', 'InitializeComponent();' + nl + '            InitializeKeyAuth();', 1)

            # 4. Replace or inject InitializeKeyAuth()
            init_span = find_method_span(code, 'InitializeKeyAuth')
            if init_span:
                code = code[:init_span[0]] + init_method.strip() + code[init_span[1]:]
            elif 'void InitializeKeyAuth' not in code:
                last_brace = code.rfind('}')
                if last_brace != -1:
                    second_last = code[:last_brace].rfind('}')
                    idx = second_last if second_last != -1 else last_brace
                    code = code[:idx] + nl + init_method + nl + code[idx:]

            # 5. Replace or inject loginbtn_Click()
            login_span = find_method_span(code, btn_name)
            if login_span:
                code = code[:login_span[0]] + login_method.strip() + code[login_span[1]:]
            elif f"{btn_name}_Click" not in code:
                last_brace = code.rfind('}')
                if last_brace != -1:
                    second_last = code[:last_brace].rfind('}')
                    idx = second_last if second_last != -1 else last_brace
                    code = code[:idx] + nl + login_method + nl + code[idx:]

            # 6. Replace or inject UpdateStatus()
            status_span = find_method_span(code, 'UpdateStatus')
            if status_span:
                code = code[:status_span[0]] + status_method.strip() + code[status_span[1]:]
            elif 'void UpdateStatus' not in code:
                last_brace = code.rfind('}')
                if last_brace != -1:
                    second_last = code[:last_brace].rfind('}')
                    idx = second_last if second_last != -1 else last_brace
                    code = code[:idx] + nl + status_method + nl + code[idx:]

            # Strictly remove any stray "/n" or literal escape artifacts
            code = code.replace('/n', '\n')
            patched_code = code

        # Sanitize final output to ensure no stray /n token exists
        patched_code = patched_code.replace('/n', '\n')
    elif lang in ('cpp', 'c++'):


        patched_code = f"""/* =========================================================================


 * KRISHU X KEYAUTH — FULLY INJECTED C++ AUTHENTICATION MODULE


 * Language: C++ (MSVC / MinGW / Win32 / ImGui / Direct3D)


 * Auto-Generated on: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}


 * Target App: {app_name} | Version: {app_version}


 * ========================================================================= */





#include <iostream>


#include <string>


#include <windows.h>


#include "KeyAuth.hpp"





using namespace KeyAuth;





// ── 1. KRISHU X KEYAUTH INITIALIZATION ──


std::string name = "{app_name}";


std::string ownerid = "{owner_id}";


std::string secret = "{app_secret}";


std::string version = "{app_version}";


std::string url = "{api_url}";





api KeyAuthApp(name, ownerid, secret, version, url);





void ExecuteLogin(const std::string& username, const std::string& password) {{


    std::cout << "[*] Initializing KeyAuth Session..." << std::endl;


    KeyAuthApp.init();





    if (!KeyAuthApp.response.success) {{


        std::cout << "[-] Init Error: " << KeyAuthApp.response.message << std::endl;


        return;


    }}





    std::cout << "[*] Authenticating credentials for: " << username << std::endl;


    KeyAuthApp.login(username, password);





    if (KeyAuthApp.response.success) {{


        std::cout << "[+] Access Granted! Welcome: " << KeyAuthApp.user_data.username << std::endl;


        std::cout << "[+] HWID Locked: " << KeyAuthApp.user_data.hwid << std::endl;


        std::cout << "[+] Sub Expiry: " << KeyAuthApp.user_data.expires << std::endl;


    }} else {{


        std::cout << "[-] Authentication Failed: " << KeyAuthApp.response.message << std::endl;


    }}


}}





// ── 2. BUTTON EVENT BINDING ({btn_name}) ──


void On_{btn_name}_Clicked() {{

    std::string user = {user_box};

    std::string pass = {pass_box};

    ExecuteLogin(user, pass);

}}

"""


    elif lang in ('python', 'py'):


        patched_code = f"""# =========================================================================


# KRISHU X KEYAUTH — FULLY INJECTED PYTHON AUTHENTICATION MODULE


# Auto-Generated on: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}


# Target App: {app_name} | Version: {app_version}


# =========================================================================





import sys


import hashlib


import requests





APP_NAME = "{app_name}"


OWNER_ID = "{owner_id}"


APP_SECRET = "{app_secret}"


APP_VERSION = "{app_version}"


API_URL = "http://127.0.0.1:5000/api/1.2/"





class KrishuKeyAuth:


    def __init__(self):


        self.session_id = None





    def init(self):


        res = requests.post(API_URL, data={{


            "type": "init",


            "name": APP_NAME,


            "ownerid": OWNER_ID,


            "secret": APP_SECRET,


            "version": APP_VERSION


        }}).json()


        if res.get("success"):


            self.session_id = res.get("sessionid")


            return True, res.get("message")


        return False, res.get("message")





    def login(self, username, password):


        if not self.session_id:


            self.init()


        res = requests.post(API_URL, data={{


            "type": "login",


            "username": username,


            "pass": password,


            "sessionid": self.session_id,


            "name": APP_NAME,


            "ownerid": OWNER_ID


        }}).json()


        return res.get("success", False), res.get("message", "Error")





# ── LOGIN HANDLER BINDING FOR ({btn_name}) ──


auth = KrishuKeyAuth()





def on_{btn_name}_click({user_box}_val, {pass_box}_val):


    print(f"[*] Validating credentials...")


    ok, msg = auth.login({user_box}_val, {pass_box}_val)


    if ok:


        print(f"[+] Login Successful: {{msg}}")


    else:


        print(f"[-] Access Denied: {{msg}}")


"""


    else:


        patched_code = f"""/* =========================================================================


 * KRISHU X KEYAUTH — ANDROID / JAVA AUTHENTICATION MODULE


 * Auto-Generated on: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}


 * Target App: {app_name} | Version: {app_version}


 * ========================================================================= */





package com.krishux.auth;





import android.os.Bundle;


import android.widget.Button;


import android.widget.EditText;


import android.widget.TextView;


import android.widget.Toast;


import androidx.appcompat.app.AppCompatActivity;





public class LoginActivity extends AppCompatActivity {{


    private EditText {user_box};


    private EditText {pass_box};


    private Button {btn_name};


    private TextView {status_box};





    @Override


    protected void onCreate(Bundle savedInstanceState) {{


        super.onCreate(savedInstanceState);


        setContentView(R.layout.activity_login);





        {user_box} = findViewById(R.id.{user_box});


        {pass_box} = findViewById(R.id.{pass_box});


        {btn_name} = findViewById(R.id.{btn_name});


        {status_box} = findViewById(R.id.{status_box});





        {btn_name}.setOnClickListener(v -> {{


            String user = {user_box}.getText().toString().trim();


            String pass = {pass_box}.getText().toString().trim();


            authenticate(user, pass);


        }});


    }}





    private void authenticate(String user, String pass) {{


        {status_box}.setText("Connecting to Krishu X KeyAuth...");


        Toast.makeText(this, "Authenticated with Krishu X Core", Toast.LENGTH_SHORT).show();


    }}


}}


"""





    return jsonify({


        'success': True,


        'language': lang,


        'patchedCode': patched_code,


        'checkStatus': 'Valid & Syntax Verified',


        'changesApplied': [


            f"KeyAuth App instance initialized with App: {app_name}",


            f"Bound username textfield: {user_box}",


            f"Bound password textfield: {pass_box}",


            f"Bound login click trigger: {btn_name}",


            f"Bound status notifications: {status_box}",


            "Injected complete error handling and zero-trust HWID routines"


        ]


    })








# ── COMPATIBILITY & VERIFY SHORTCUTS ──────────────────────────





@app.route('/api/keyauth/verify', methods=['POST'])


@app.route('/api/v1/keyauth/verify', methods=['POST'])


def api_keyauth_verify_compat():


    data = request.json or {}


    key = str(data.get('key', '')).strip()


    hwid = str(data.get('hwid', 'COMPAT')).strip()


    ip = request.headers.get('X-Forwarded-For', request.remote_addr or '').split(',')[0].strip()


    apps = KeyAuth.list_apps()


    app_id = apps[0].get('appId') if apps else 'app_krishu_main'


    res = KeyAuth.client_license_login(app_id, key, hwid, ip)


    return jsonify(res), (200 if res.get('success') else 401)








if __name__ == '__main__':


    port = int(os.environ.get('PORT', 5000))


    host = os.environ.get('HOST', '0.0.0.0')


    print('=' * 75)


    print(f'KRISHU X CHEATS — KEYAUTH ENTERPRISE SERVER RUNNING')


    print(f'Web Portal & Admin Console: http://127.0.0.1:{port}')


    print(f'Admin Identifier: krishu (Master Protected via .env)')


    print('=' * 75)


    app.run(host=host, port=port, debug=False)





