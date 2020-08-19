from nanoid import generate
from slugify import slugify
from datetime import datetime
import dateparser


RULE_SUMMARY = """
## {name}
** {description} **
Total dates checked: {total}
Ignored: {ignored}
Passed: {passed}
Failed: {failed}
"""
DATE_FMT = "%Y-%m-%d"


def gen_checkup_id() -> str:
    return generate(size=5)


def get_filename(id, name, ext) -> str:
    name = slugify(name)
    dt = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    filename = '{}_{}_{}_{}'.format(dt, id, name, ext)
    return filename


def get_date_as_string(date):
    date = str(date)
    print('getting date {}'.format(date))
    return dateparser.parse(date).strftime(DATE_FMT)
