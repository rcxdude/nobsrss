# coding: utf8
"""

    Securely hash and check passwords using PBKDF2.

    Use random salts to protect againt rainbow tables, many iterations against
    brute-force, and constant-time comparaison againt timing attacks.

    Keep parameters to the algorithm together with the hash so that we can
    change the parameters and keep older hashes working.

    See more details at http://exyr.org/2011/hashing-passwords/

    Author: Simon Sapin
    License: BSD

"""

import hashlib
from os import urandom
from base64 import b64encode, b64decode
from itertools import izip

# From https://github.com/mitsuhiko/python-pbkdf2
"""
    pbkdf2
    ~~~~~~

    This module implements pbkdf2 for Python.  It also has some basic
    tests that ensure that it works.  The implementation is straightforward
    and uses stdlib only stuff and can be easily be copy/pasted into
    your favourite application.

    Use this as replacement for bcrypt that does not need a c implementation
    of a modified blowfish crypto algo.

    Example usage:

    >>> pbkdf2_hex('what i want to hash', 'the random salt')
    'fa7cc8a2b0a932f8e6ea42f9787e9d36e592e0c222ada6a9'

    How to use this:

    1.  Use a constant time string compare function to compare the stored hash
        with the one you're generating::

            def safe_str_cmp(a, b):
                if len(a) != len(b):
                    return False
                rv = 0
                for x, y in izip(a, b):
                    rv |= ord(x) ^ ord(y)
                return rv == 0

    2.  Use `os.urandom` to generate a proper salt of at least 8 byte.
        Use a unique salt per hashed password.

    3.  Store ``algorithm$salt:costfactor$hash`` in the database so that
        you can upgrade later easily to a different algorithm if you need
        one.  For instance ``PBKDF2-256$thesalt:10000$deadbeef...``.


    :copyright: (c) Copyright 2011 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
import hmac
import hashlib
from struct import Struct
from operator import xor
from itertools import izip, starmap

_pack_int = Struct('>I').pack

def pbkdf2_hex(data, salt, iterations=1000, keylen=24, hashfunc=None):
    """Like :func:`pbkdf2_bin` but returns a hex encoded string."""
    return pbkdf2_bin(data, salt, iterations, keylen, hashfunc).encode('hex')


def pbkdf2_bin(data, salt, iterations=1000, keylen=24, hashfunc=None):
    """Returns a binary digest for the PBKDF2 hash algorithm of `data`
    with the given `salt`.  It iterates `iterations` time and produces a
    key of `keylen` bytes.  By default SHA-1 is used as hash function,
    a different hashlib `hashfunc` can be provided.
    """
    hashfunc = hashfunc or hashlib.sha1
    mac = hmac.new(data, None, hashfunc)
    def _pseudorandom(x, mac=mac):
        h = mac.copy()
        h.update(x)
        return map(ord, h.digest())
    buf = []
    for block in xrange(1, -(-keylen // mac.digest_size) + 1):
        rv = u = _pseudorandom(salt + _pack_int(block))
        for i in xrange(iterations - 1):
            u = _pseudorandom(''.join(map(chr, u)))
            rv = starmap(xor, izip(rv, u))
        buf.extend(rv)
    return ''.join(map(chr, buf))[:keylen]

# Parameters to PBKDF2. Only affect new passwords.
SALT_LENGTH = 12
KEY_LENGTH = 24
HASH_FUNCTION = 'sha256'  # Must be in hashlib.
COST_FACTOR = 10000


def make_hash(password):
    """Generate a random salt and return a new hash for the password."""
    if isinstance(password, unicode):
        password = password.encode('utf-8')
    salt = b64encode(urandom(SALT_LENGTH))
    return 'PBKDF2${}${}${}${}'.format(
        HASH_FUNCTION,
        COST_FACTOR,
        salt,
        b64encode(pbkdf2_bin(password, salt, COST_FACTOR, KEY_LENGTH,
                             getattr(hashlib, HASH_FUNCTION))))


def check_hash(password, hash_):
    """Check a password against an existing hash."""
    if isinstance(password, unicode):
        password = password.encode('utf-8')
    algorithm, hash_function, cost_factor, salt, hash_a = hash_.split('$')
    assert algorithm == 'PBKDF2'
    hash_a = b64decode(hash_a)
    hash_b = pbkdf2_bin(password, salt, int(cost_factor), len(hash_a),
                        getattr(hashlib, hash_function))
    assert len(hash_a) == len(hash_b)  # we requested this from pbkdf2_bin()
    # Same as "return hash_a == hash_b" but takes a constant time.
    # See http://carlos.bueno.org/2011/10/timing.html
    diff = 0
    for char_a, char_b in izip(hash_a, hash_b):
        diff |= ord(char_a) ^ ord(char_b)
    return diff == 0
