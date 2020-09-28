import json
from functools import wraps
from urllib.request import urlopen
from flask import abort, request
from jose import jwt

AUTH0_DOMAIN = 'wildapps.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'fsnd-capstone'
AUTH0_CLIENT_ID = '9wUPdNcHOxTZVOrqgekSx0LJCD6BdVRB'
REDIRECT_URL = 'http://localhost:5000/callback'
AUTH0_AUTHORIZE_URL = f'https://{AUTH0_DOMAIN}/authorize?audience=' \
                      f'{API_AUDIENCE}&response_type=token&client_id=' \
                      f'{AUTH0_CLIENT_ID}&redirect_uri={REDIRECT_URL}'


# AuthError Exception
class AuthError(Exception):
    """
    AuthError Exception
    A standardized way to communicate auth failure modes
    """
    def __init__(self, error_details, status_code):
        self.error = error_details
        self.status_code = status_code


def get_token_auth_header():
    """
    Obtains the Access Token from the Authorization Header
    credit: Udacity lesson and sample code for BasicFlaskAuth
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token


def check_permissions(permission, payload):
    """
    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in
        the payload permissions array
    return true otherwise

    @INPUTS
        permission: string permission (i.e. 'create:roadtrips')
        payload: decoded jwt payload
    """
    if 'permissions' in payload and permission in payload['permissions']:
        return True
    raise AuthError({
        'success': False,
        'message': 'Invalid permissions',
        'error': 403
    }, 403)


def verify_decode_jwt(token):   # pragma: no cover
    """
    source: Udacity-provided sample code
    """
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience '
                               'and issuer.'
            }, 401)

        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)

    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key.'
    }, 403)


def requires_auth(permission=''):
    """
    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the
    requested permission
    return the decorator which passes the decoded payload to the decorated
    method

    @INPUTS
        permission: string permission (i.e. 'create:roadtrips')
    """
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
                check_permissions(permission, payload)
            except AuthError as e:
                abort(e.status_code)
            except Exception:
                abort(401)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
