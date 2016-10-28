from django.conf import settings
from django.core import urlresolvers
from django.http import Http404
from localeurlcustom import settings as localeurl_settings
#Todo
URL_PREFIX = settings.CONFERENCE_URL_PREFIXES[settings.CONFERENCE_ID]
def is_locale_independent(path):
    """
    Returns whether the path is locale-independent.
    """
    if (localeurl_settings.LOCALE_INDEPENDENT_MEDIA_URL and
            settings.MEDIA_URL and
            path.startswith(settings.MEDIA_URL)):
        return True
    if (localeurl_settings.LOCALE_INDEPENDENT_STATIC_URL and
            getattr(settings, "STATIC_URL", None) and
            path.startswith(settings.STATIC_URL)):
        return True
    for regex in localeurl_settings.LOCALE_INDEPENDENT_PATHS:
        if regex.search(path):
            return True
    return False


def strip_path(path):
    """
    Separates the locale prefix from the rest of the path. If the path does not
    begin with a locale it is returned without change.
    """

    check = localeurl_settings.PATH_RE.match(path)
    if check:
        path_info = check.group('path') or '/'
        if path_info.startswith('/'):
            locale = check.group('locale')
            return locale, "/" + check.group(1) + "/" + locale + path_info

    return '', path


def supported_language(locale):
    """
    Returns the supported language (from settings.LANGUAGES) for the locale.
    """
    locale = locale.lower()
    bits = locale.split('-')
    if locale in localeurl_settings.SUPPORTED_LOCALES:
        return locale
    elif bits[0] in localeurl_settings.SUPPORTED_LOCALES:
        return bits[0]
    else:
        return None


def is_default_locale(locale):
    """
    Returns whether the locale is the default locale.
    """
    return locale == supported_language(settings.LANGUAGE_CODE)


def locale_path(path, locale=''):
    """
    Generate the localeurl-enabled path from a path without locale prefix. If
    the locale is empty settings.LANGUAGE_CODE is used.
    """

    locale = supported_language(locale)
    if not locale:
        locale = supported_language(settings.LANGUAGE_CODE)
    if is_locale_independent(path):
        return path
    elif is_default_locale(locale) and not localeurl_settings.PREFIX_DEFAULT_LOCALE:
        return path
    else:
        tmp = path.split("/")

        if len(tmp) < 3:
            if tmp[1] == URL_PREFIX:
                tmp.append("")
            else:
                raise Http404()
        elif len(tmp) < 2:
            tmp.insert(1, URL_PREFIX)
        elif tmp[1] == locale:
            tmp[1] = URL_PREFIX
        tmp_locale = tmp[2]
        if tmp_locale == locale:
            return path
        if tmp_locale in localeurl_settings.SUPPORTED_LOCALES:
            tmp[2] = locale
        else:
            tmp.insert(2, locale)
        return "/".join(tmp)

def locale_url(path, locale=''):
    """
    Generate the localeurl-enabled URL from a path without locale prefix. If
    the locale is empty settings.LANGUAGE_CODE is used.
    """
    path = locale_path(path, locale)
    return add_script_prefix(path)


def strip_script_prefix(url):
    """
    Strips the SCRIPT_PREFIX from the URL. Because this function is meant for
    use in templates, it assumes the URL starts with the prefix.
    """
    assert url.startswith(urlresolvers.get_script_prefix()), \
            "URL must start with SCRIPT_PREFIX: %s" % url
    pos = len(urlresolvers.get_script_prefix()) - 1
    return url[:pos], url[pos:]


def add_script_prefix(path):
    """
    Prepends the SCRIPT_PREFIX to a path.
    """

    return ''.join([urlresolvers.get_script_prefix(), path[1:]])
