# -*- coding: utf-8 -*-
import json
import logging
import os
import ssl

from functools import wraps
from flask import jsonify, request, _request_ctx_stack
from werkzeug.local import LocalProxy
from Crypto.Util import asn1
from google.appengine.api import urlfetch
from google.appengine.api import urlfetch_errors

import jwt
from jwt.exceptions import InvalidTokenError
from jwt.contrib.algorithms.pycrypto import RSAAlgorithm

from app.kernel.cache import cache
from app.models import User

FIREBASE_CERTIFICATES_URL = (
    'https://www.googleapis.com/robot/v1/metadata/x509/'
    'securetoken@system.gserviceaccount.com')

# for AppEngine, pyjwt needs to use PyCrypto instead of Cryptography.
jwt.register_algorithm('RS256', RSAAlgorithm(RSAAlgorithm.SHA256))

current_user = LocalProxy(lambda: _request_ctx_stack.top.current_user)


@cache.memoize(timeout=3600)
def get_firebase_certificates():
    try:
        urlfetch.set_default_fetch_deadline(300)
        result = urlfetch.Fetch(
            FIREBASE_CERTIFICATES_URL,
            validate_certificate=True)
        data = result.content
    except urlfetch_errors.Error:
        logging.error('Error while fetching Firebase certificates.')
        raise

    return json.loads(data)


@cache.memoize(timeout=3600)
def extract_public_key_from_certificate(x509_certificate):
    der_certificate_string = ssl.PEM_cert_to_DER_cert(x509_certificate)

    # Extract subjectPublicKeyInfo field from X.509 certificate (see RFC3280)
    der_certificate = asn1.DerSequence()
    der_certificate.decode(der_certificate_string)
    tbs_certification = asn1.DerSequence()  # To Be Signed certificate
    tbs_certification.decode(der_certificate[0])

    subject_public_key_info = tbs_certification[6]

    return subject_public_key_info


def unauthorized(error):
    resp = jsonify(error)
    resp.status_code = 401
    return resp


def verify_auth_token(token):
    # Determine which certificate was used to sign the JWT.
    header = jwt.get_unverified_header(token)

    certificates = get_firebase_certificates()

    try:
        kid = header['kid']
        certificate = certificates[kid]
    except KeyError:
        logging.warning('JWT signed with unkown kid {}'.format(kid))
        return None

    # Get the public key from the certificate. This is used to verify the
    # JWT signature.
    public_key = extract_public_key_from_certificate(certificate)

    try:
        return jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience=os.environ['FIREBASE_PROJECT_ID'],
            issuer='https://securetoken.google.com/{}'.format(
                os.environ['FIREBASE_PROJECT_ID']))
    except InvalidTokenError as e:
        logging.warning('JWT verification failed: {}'.format(e))


def requires_auth(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', None)
        if not auth:
            return unauthorized({'code': 'header_missing', 'description': 'Authorization header is expected.'})

        request_jwt = request.headers['Authorization'].split(' ').pop()
        if not request_jwt:
            return {'code': 'invalid_header', 'description': 'Authorization header must start with Bearer.'}

        claims = verify_auth_token(request_jwt)
        if not claims:
            return unauthorized({'code': 'unauthorized', 'description': 'Invalid token.'})

        _request_ctx_stack.top.current_user = User.get_or_insert(claims['sub'], email=claims.get('email'))
        return func(*args, **kwargs)
    return decorated
