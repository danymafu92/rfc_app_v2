"""Supabase token authentication adapter for Django REST Framework.

This module exposes `SupabaseAuthentication`, a small DRF authentication
adapter that accepts a Supabase access token via the `Authorization: Bearer`
header. It decodes the JWT WITHOUT verifying the signature (development
convenience) and constructs a minimal `SupabaseUser` object used by DRF.

Security note: production systems should verify JWT signatures or validate
tokens using Supabase's server-side SDK. This adapter is intentionally
permissive to make local development and CI easier.
"""

from rest_framework import authentication, exceptions
from django.conf import settings
from supabase import create_client, Client
import jwt


class SupabaseAuthentication(authentication.BaseAuthentication):
    """Authenticate requests using a Supabase access token.

    Behavior:
    - If the Authorization header is missing or not a Bearer token, returns
      None so other authentication backends (if any) may run.
    - Decodes the token without signature verification and extracts the
      `sub` claim as the user's id. If missing, authentication fails.
    - Returns a lightweight `SupabaseUser` object with `id`, `email` and
      `is_authenticated = True` so DRF permission checks work.
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]

        try:
            # The supabase client is created here to reflect the original
            # project intent; it's not required for JWT decoding but may be
            # useful for future server-side calls.
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

            decoded = jwt.decode(token, options={"verify_signature": False})

            user_id = decoded.get('sub')
            if not user_id:
                raise exceptions.AuthenticationFailed('Invalid token')

            class SupabaseUser:
                def __init__(self, user_id, email=None):
                    self.id = user_id
                    self.email = email or ''
                    self.is_authenticated = True

                def __str__(self):
                    return self.email or self.id

            user = SupabaseUser(user_id, decoded.get('email'))

            return (user, token)

        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Authentication failed: {str(e)}')
"""Supabase token authentication adapter for Django REST Framework.

This module exposes `SupabaseAuthentication`, a small DRF authentication
adapter that accepts a Supabase access token via the `Authorization: Bearer`
header. It decodes the JWT WITHOUT verifying the signature (development
convenience) and constructs a minimal `SupabaseUser` object used by DRF.

Security note: production systems should verify JWT signatures or validate
tokens using Supabase's server-side SDK. This adapter is intentionally
permissive to make local development and CI easier.
"""

from rest_framework import authentication, exceptions
from django.conf import settings
from supabase import create_client, Client
import jwt


class SupabaseAuthentication(authentication.BaseAuthentication):
    """Authenticate requests using a Supabase access token.

    Behavior:
    - If the Authorization header is missing or not a Bearer token, returns
      None so other authentication backends (if any) may run.
    - Decodes the token without signature verification and extracts the
      `sub` claim as the user's id. If missing, authentication fails.
    - Returns a lightweight `SupabaseUser` object with `id`, `email` and
      `is_authenticated = True` so DRF permission checks work.
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]

        try:
            # The supabase client is created here to reflect original intent;
            # it's not required for simple JWT decoding but may be useful if
            # future changes need server-side calls.
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

            decoded = jwt.decode(token, options={"verify_signature": False})

            user_id = decoded.get('sub')
            if not user_id:
                raise exceptions.AuthenticationFailed('Invalid token')

            class SupabaseUser:
                def __init__(self, user_id, email=None):
                    self.id = user_id
                    self.email = email or ''
                    self.is_authenticated = True

                def __str__(self):
                    return self.email or self.id

            user = SupabaseUser(user_id, decoded.get('email'))

            return (user, token)

        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Authentication failed: {str(e)}')
"""Supabase token-based authentication adapter for Django REST Framework.

This adapter extracts a Bearer token from the Authorization header, decodes
the JWT (without verifying signature) to read the `sub` claim and constructs a
minimal `SupabaseUser` object that DRF can use for `request.user`.

Important notes for contributors / AI agents:
- This implementation intentionally does NOT verify JWT signatures. Supabase
  is expected to be the authoritative auth provider. For production, consider
  verifying signatures or using Supabase's server-side SDK to validate tokens.
- The adapter returns a lightweight `SupabaseUser` with `id` and `email` and
  sets `is_authenticated = True` so standard DRF permission checks work.
"""

from rest_framework import authentication
from rest_framework import exceptions
from django.conf import settings
from supabase import create_client, Client
import jwt


class SupabaseAuthentication(authentication.BaseAuthentication):
    """Authenticate requests using a Supabase access token.

    The adapter reads the `Authorization: Bearer <token>` header, decodes the
    JWT WITHOUT verifying the signature (development convenience) and builds
    a minimal `SupabaseUser` object used by DRF permission checks.
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]

        try:
            # create_client is available but not strictly required here; it's
            # kept to mirror the original codebase intent for possible future
            # server-side Supabase calls.
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

            decoded = jwt.decode(
                token,
                options={"verify_signature": False}
            )

            user_id = decoded.get('sub')

            if not user_id:
                raise exceptions.AuthenticationFailed('Invalid token')

            class SupabaseUser:
                def __init__(self, user_id, email=None):
                    self.id = user_id
                    self.email = email or ''
                    self.is_authenticated = True

                def __str__(self):
                    return self.email or self.id

            user = SupabaseUser(user_id, decoded.get('email'))

            return (user, token)

        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Authentication failed: {str(e)}')
"""Supabase token-based authentication adapter for Django REST Framework.

This adapter extracts a Bearer token from the Authorization header, decodes
the JWT (without verifying signature) to read the `sub` claim and constructs a
minimal `SupabaseUser` object that DRF can use for `request.user`.

Important notes for contributors / AI agents:
- This implementation intentionally does NOT verify JWT signatures. Supabase
  is expected to be the authoritative auth provider. For production, consider
  verifying signatures or using Supabase's server-side SDK to validate tokens.
- The adapter returns a lightweight `SupabaseUser` with `id` and `email` and
  sets `is_authenticated = True` so standard DRF permission checks work.
"""

from rest_framework import authentication
from rest_framework import exceptions
from django.conf import settings
from supabase import create_client, Client
import jwt


class SupabaseAuthentication(authentication.BaseAuthentication):
    """Authenticate requests using a Supabase access token.

    The adapter reads the `Authorization: Bearer <token>` header, decodes the
    JWT WITHOUT verifying the signature (development convenience) and builds
    a minimal `SupabaseUser` object used by DRF permission checks.
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]

        try:
            # create_client is available but not strictly required here; it's
            # kept to mirror the original codebase intent for possible future
            # server-side Supabase calls.
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

            decoded = jwt.decode(
                token,
                options={"verify_signature": False}
            )

            user_id = decoded.get('sub')

            if not user_id:
                raise exceptions.AuthenticationFailed('Invalid token')

            class SupabaseUser:
                def __init__(self, user_id, email=None):
                    self.id = user_id
                    self.email = email or ''
                    self.is_authenticated = True

                def __str__(self):
                    return self.email or self.id

            user = SupabaseUser(user_id, decoded.get('email'))

            return (user, token)

        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Authentication failed: {str(e)}')
"""Supabase token-based authentication adapter for Django REST Framework.

This adapter extracts a Bearer token from the Authorization header, decodes
the JWT (without verifying signature) to read the `sub` claim and constructs a
minimal `SupabaseUser` object that DRF can use for `request.user`.

Important notes for contributors / AI agents:
- This implementation intentionally does NOT verify JWT signatures. Supabase
  is expected to be the authoritative auth provider. For production, consider
  verifying signatures or using Supabase's server-side SDK to validate tokens.
- The adapter returns a lightweight `SupabaseUser` with `id` and `email` and
  sets `is_authenticated = True` so standard DRF permission checks work.
"""

from rest_framework import authentication
from rest_framework import exceptions
from django.conf import settings
from supabase import create_client, Client
import jwt


class SupabaseAuthentication(authentication.BaseAuthentication):
    """Authenticate requests using a Supabase access token.

    The adapter reads the `Authorization: Bearer <token>` header, decodes the
    JWT WITHOUT verifying the signature (development convenience) and builds
    a minimal `SupabaseUser` object used by DRF permission checks.
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]

        try:
            # create_client is available but not strictly required here; it's
            # kept to mirror the original codebase intent for possible future
            # server-side Supabase calls.
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

            decoded = jwt.decode(
                token,
                options={"verify_signature": False}
            )

            user_id = decoded.get('sub')

            if not user_id:
                raise exceptions.AuthenticationFailed('Invalid token')

            class SupabaseUser:
                def __init__(self, user_id, email=None):
                    self.id = user_id
                    self.email = email or ''
                    self.is_authenticated = True

                def __str__(self):
                    return self.email or self.id

            user = SupabaseUser(user_id, decoded.get('email'))

            return (user, token)

        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Authentication failed: {str(e)}')
#the JWT (without verifying signature) to read the `sub` claim and constructs a
#minimal `SupabaseUser` object that DRF can use for `request.user`.
"""Supabase token-based authentication adapter for Django REST Framework.

This adapter extracts a Bearer token from the Authorization header, decodes
the JWT (without verifying signature) to read the `sub` claim and constructs a
minimal `SupabaseUser` object that DRF can use for `request.user`.

Important notes for contributors / AI agents:
- This implementation intentionally does NOT verify JWT signatures. Supabase
    is expected to be the authoritative auth provider. For production, consider
    verifying signatures or using Supabase's server-side SDK to validate tokens.
- The adapter returns a lightweight `SupabaseUser` with `id` and `email` and
    sets `is_authenticated = True` so standard DRF permission checks work.
"""

from rest_framework import authentication
from rest_framework import exceptions
from django.conf import settings
from supabase import create_client, Client
import jwt

class SupabaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]

        try:
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

            decoded = jwt.decode(
                token,
                options={"verify_signature": False}
            )

            user_id = decoded.get('sub')

            if not user_id:
                raise exceptions.AuthenticationFailed('Invalid token')

            class SupabaseUser:
                def __init__(self, user_id, email=None):
                    self.id = user_id
                    self.email = email or ''
                    self.is_authenticated = True

                def __str__(self):
                    return self.email or self.id

            user = SupabaseUser(user_id, decoded.get('email'))

            return (user, token)

        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Authentication failed: {str(e)}')
