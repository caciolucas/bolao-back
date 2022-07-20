import jwt, os, hashlib

SALT = os.environ.get('DATABASE_SALT', 'salt')
SECRET = os.environ.get('JWT_SECRET', 'secret')


def cursor_result_to_dict(cursor, single_row=False):
    if single_row:
        if result := cursor.fetchone():
            return dict(zip(cursor.column_names, result))
        else:
            return None
    else:
        if result := cursor.fetchall():
            return [dict(zip(cursor.column_names, row)) for row in result]
        else:
            return []


def check_for_token(token):
    try:
        schema, token = token.split(' ')
    except ValueError:
        return {'success': False, 'message': 'Credenciais inválidas'}
    if schema != 'Bearer':
        return {'success': False, 'message': 'Credenciais inválidas - Schema inválido'}
    return {'success': True, 'email': jwt.decode(token, 'secret', algorithms=['HS256'])['email']}


def crypt_password(password):
    return hashlib.sha256(password.encode('utf-8') + SALT.encode('utf-8')).hexdigest()


def generate_token(email):
    return jwt.encode({'email': email}, SECRET, algorithm='HS256')
