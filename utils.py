import datetime
import email
import imaplib
import logging
import os

import pytz
import re

import schedule
import unicodedata
from bs4 import BeautifulSoup
from bs4.element import Tag

from dotenv import load_dotenv
from email.header import decode_header

from config import *


load_dotenv()
logger = logging.getLogger(__name__)
blocks = ["p", "h1", "h2", "h3", "h4", "h5", 'div', ]


def email_name(full_addr: str) -> str:
    """Extract short email box name from full address"""
    return re.findall(r'([\w._-]+)@[\w._-]+\.[\w.]+', full_addr)[0]


def is_uidsfile(full_addr: str) -> None:
    """Checking the existence of a file to record ids of viewed emails."""
    name = email_name(full_addr)
    try:
        if not os.path.isfile(f'{PREFIX}{name}{EXT}'):
            open(f'{PREFIX}{name}{EXT}', 'w+').close()
    except Exception as e:
        logger.exception(f'Error creating viewed emails file {PREFIX}{name}{EXT} on start.', exc_info=True)
        raise e


def erase_file(filename: str) -> bool:
    """The file is partially erased here"""
    erased: bool = False
    try:
        list_file = []
        with open(filename, 'r') as f:
            for count, line in enumerate(f):
                pass
            total_count = count
        if total_count > MAX_LINES_IN_FILE:
            with open(filename, 'r') as f:
                for index, line in enumerate(f):
                    if index > (total_count - MAX_LINES_IN_FILE):
                        list_file.append(line)
        if list_file:
            with open(filename, 'w') as f:
                f.writelines(list_file)
            logger.info(f'\nThe {filename} file was partially cleaned. The last {MAX_LINES_IN_FILE} lines are saved.')
            erased = True
    except Exception:
        logger.warning(f'Unable to clear the {filename} file.', exc_info=True)
    return erased


def erase_files(files_names: list) -> None:
    """The uids or log files are cleared here"""
    erased: bool = False
    for name in files_names:
        if erase_file(name):
            erased = True
    if erased:
        logger.info(f'Scheduled tasks:\n  {schedule.get_jobs()}')


def email_login(cred: dict) -> imaplib.IMAP4_SSL or bool:
    """Creating a connection to an email."""
    name = cred.get('name', '')
    try:
        imap = imaplib.IMAP4_SSL(cred['server'], cred['port'])
    except Exception:
        logger.exception(f"Failed to create IMAP {name} connection:", exc_info=True)
        return False
    else:
        try:
            imap.login(name, cred['pass'])
        except Exception:
            logger.exception(f"IMAP {name} authentication error:", exc_info=True)
            return False
        else:
            logger.info(f"IMAP {name} connection established")
            return imap


def range_date() -> str:
    """Creating a string to search for email by date sent."""
    start_date = datetime.date.today() - datetime.timedelta(days=SEARCH_DEPTH)
    end_date = datetime.date.today() + datetime.timedelta(days=1)
    start_date_str = start_date.strftime('%d-%b-%Y')
    end_date_str = end_date.strftime('%d-%b-%Y')
    return f'(SINCE {start_date_str} BEFORE {end_date_str})'


def pull_seen_mail_uids(name: str) -> set:
    """Reading from a file of email U_IDs that have already been viewed."""
    seen_mails = set()
    try:
        with open(f'{PREFIX}{name}{EXT}', 'r') as f:
            while True:
                u_id = f.readline().strip()
                if not u_id:
                    break
                seen_mails.add(u_id)
    except Exception as e:
        logger.warning(f'Unable to read the file {PREFIX}{name}{EXT} with the numbers of viewed emails:\n',
                       exc_info=True)
        raise e
    return seen_mails


def push_seen_mail_uids(name: str, new_mails: set) -> None:
    """Record in a file the email U_IDs that have already been viewed."""
    with open(f'uids_{name}.txt', 'a') as f:
        try:
            new_mails_str = ", ".join(map(str, new_mails))
            while True:
                f.writelines(str(new_mails.pop()) + '\n')
                if not new_mails:
                    break
        except Exception as e:
            logger.warning(f'Unable to replenish the browsed emails file "{PREFIX}{name}{EXT}":\n', exc_info=True)
            raise e
        else:
            logger.debug(f'U_ids of new emails written to file "{PREFIX}{name}{EXT}": {new_mails_str}')


def create_info(
        name: str,
        u_id: int,
        m_type: str,
        email_from: str,
        email_to: str,
        mail_datetime: str,
        subject: str,
        content: str
        ) -> dict:
    """Information from e-mail is collected in a dictionary and
    the time of the e-mail is translated into the desired time zone."""
    mail_datetime = re.sub(r"\(.*?\)", "", mail_datetime, flags=re.DOTALL)
    try:
        inst_datetime = datetime.datetime.strptime(mail_datetime.strip(), '%a, %d %b %Y %H:%M:%S %z')
        datetime_tz = inst_datetime.astimezone(pytz.timezone('Europe/Moscow'))
        date = datetime_tz.strftime('%Y-%m-%d')
        time = datetime_tz.strftime('%H:%M:%S')
    except Exception:
        date = mail_datetime
        time = mail_datetime
    logger.info(f'Email {u_id} dated {date} {time} from folder "{m_type}", box "{name}" viewed')
    return {
        'box': name,
        'id': u_id,
        'type': m_type,
        'from': email_from,
        'to': email_to,
        'date': date,
        'time': time,
        'subject': subject,
        'email_body': content,
    }


def pull_name(data) -> str:
    """The email name is extracted from email data."""
    if isinstance(data, bytes):
        email_name = re.findall(r'[\w._-]+@[\w._-]+\.[\w.]+', data.decode())
    else:
        try:
            email_name = re.findall(r'[\w._-]+@[\w._-]+\.[\w.]+', data)
            if not email_name:
                email_name = data
        except Exception:
            email_name = data
    if isinstance(email_name, list):
        email_name = list(map(str.lower, email_name))
        email_name = ', '.join(list(set(email_name)))
    return email_name


def del_break(text: str) -> str:
    """Spaces and line breaks are removed from the text."""
    textlist = text.split('\n')
    textlist = list(map(str.strip, textlist))
    for el in ['', '\r\n', '\r', '\t', '\t\t', '\t\t\t', '\t\t\t\t']:
        while el in textlist: textlist.remove(el)
    return "\n".join(textlist)


def extract_blocks(parent_tag) -> list:
    """Recursively extracting block elements with a necessary tags."""
    extracted_blocks = []
    for tag in parent_tag:
        if tag.name in blocks:
            extracted_blocks.append(tag)
            continue
        if isinstance(tag, Tag):
            if len(tag.contents) > 0:
                inner_blocks = extract_blocks(tag)
                if len(inner_blocks) > 0:
                    extracted_blocks.extend(inner_blocks)
    return extracted_blocks


def to_plaintext(html_text: str) -> str:
    """Extracting text with necessary tags from a html-line."""
    soup = BeautifulSoup(html_text, features="lxml")
    if soup.body:
        extracted_blocks = extract_blocks(soup.body)
        extracted_blocks_texts = [block.get_text().strip() for block in extracted_blocks]
        plaintext = "\n".join(extracted_blocks_texts)
        return del_break(plaintext)


def clean_html(html: str) -> str:
    """Simplified cleaning of lines from html-tags and removal of empty lines."""
    del_tags = re.sub(r"<.*?>", "\n", html, flags=re.DOTALL)
    text_list = list(filter(None, del_tags.split('\n')))
    res_list = []
    for el in text_list:
        row = el.strip()
        if len(row):
            res_list.append(row)
    res_text = '\n'.join(res_list)
    return res_text


def info_from_email(name: str, u_id: int, mail: list, m_type: str) -> dict or None:
    """Decoding email and retrieve addresses, time and content from email."""
    msg = email.message_from_bytes(mail[0][1])
    mail_datetime = decode_header(msg.get('Date'))[0][0]
    try:
        subject = decode_header(msg['Subject'])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()
    except Exception:
        try:
            subject = decode_header(msg['Subject'])[0][0].decode('cp1251')
        except Exception as e:
            subject = 'Unable to parse email subject or it is empty'
            logger.warning(f'Unable to parse subject of email {u_id} dated {mail_datetime} from box "{name}":\n{e}')
    to_data = decode_header(msg.get('To'))[-1][0]
    email_to = pull_name(to_data)
    from_data = decode_header(msg.get('From'))[-1][0]
    email_from = pull_name(from_data)
    for part in msg.walk():
        maintype = part.get_content_maintype()
        subtype = part.get_content_subtype()
        if (maintype == 'text' and subtype == 'plain') or (maintype == 'text' and subtype == 'html'):
            pre_content = None
            try:
                pre_content = part.get_payload(decode=True).decode()
            except Exception:
                logger.info(f'On first try it is impossible to get content of the email {u_id}'
                            f' dated {mail_datetime} from box "{name}"')
            if not pre_content:
                try:
                    pre_content = part.get_payload(decode=True).decode('cp1251')
                    ch = re.search(r"[а-я]{1}[А-Я]{5,}\s[А-Я]{5,}", pre_content, flags=re.DOTALL)
                    if ch:
                        pre_content = part.get_payload(decode=True).decode('KOI8-R')
                except Exception as e:
                    logger.warning(
                        f'It is impossible to get content of the email {u_id}'
                        f' dated {mail_datetime} from box "{name}":\n{e}')
            try:
                content = unicodedata.normalize('NFKC', pre_content)
                logger.debug(f'Got the content of the email {u_id} dated {mail_datetime}'
                             f' from box "{name}"')
                if subtype == 'html':
                    mail_body = to_plaintext(content)
                    if not mail_body:
                        mail_body = clean_html(content)
                    if mail_body[0] == '+':
                        mail_body = mail_body[1:]
                else:
                    plainlist = content.split('\n\n')
                    if 'CLIENT-SPECIFIC STYLES' in plainlist[0]:
                        plainlist.pop(0)
                    plain_text = "\n".join(plainlist)
                    mail_body = del_break(plain_text)
            except Exception as e:
                mail_body = f'Unable to parse email or email content is empty'
                logger.warning(f'Unable to parse email {u_id} dated {mail_datetime} from box "{name}" folder "{m_type}"'
                               f' or email content is empty:\n{e}')
            mail_body = f'{mail_body[:LEN_TEXT]}'
            info = create_info(name, u_id, m_type, email_from, email_to, mail_datetime, subject, mail_body)
            if info:
                return info


def create_info_list(name: str, imap: imaplib.IMAP4_SSL, box_type: str) -> tuple:
    """Creating a tuple with list of necessary information only from those emails from box folder
     that have not yet been viewed and with a list of the numbers of these emails."""
    if box_type == 'Sent':
        box = box_type
        m_type = 'sent'
    else:
        box = 'INBOX'
        m_type = 'received'
    imap.select(box, readonly=True)
    result, data = imap.uid('search', range_date())
    u_ids = data[0]
    if u_ids:
        u_id_set = set((u_ids.decode('utf8')).split())
        new_mails = u_id_set.difference(pull_seen_mail_uids(name))
        if new_mails:
            logger.info(f'New {m_type} emails detected in box "{name}": {new_mails}')
            info_list = list()
            for u_id in new_mails:
                result, mail = imap.uid('fetch', u_id, '(RFC822)')
                try:
                    info = info_from_email(name, u_id, mail, m_type)
                except Exception as e:
                    logger.warning(f'Impossible to get information from {m_type} email {u_id} from box "{name}":\n{e}')
                    continue
                else:
                    if info:
                        info_list.append(info)
            if info_list:
                return info_list, new_mails


def test_pull_mail(name, imap, u_id, box_type):
    """Service function for extracting the contents of email by its id"""
    if box_type.capitalize() == 'Sent':
        box = 'Sent'
    else:
        box = 'INBOX'
    imap.select(box, readonly=True)
    res, mail = imap.uid('fetch', u_id, '(RFC822)')
    return info_from_email(name, u_id, mail, box)


def pull_data(name: str, imap: imaplib.IMAP4_SSL) -> tuple:
    """Creating a tuple with list information from sent and retrieve emails
    and with a list of the numbers of these emails."""
    data: list = []
    uids: list = []
    received: tuple = create_info_list(name, imap, 'INBOX')
    sent: tuple = create_info_list(name, imap, 'Sent')
    if received:
        data += received[0]
        uids += received[1]
    if sent:
        data += sent[0]
        uids += sent[1]
    if data:
        return data, uids


def searching_data(reg_line: str, text: str) -> str:
    """Searching for data in email by template"""
    try:
        data = re.findall(reg_line, text, re.IGNORECASE)[0]
    except Exception:
        data = f'Data cannot be found'
        logger.warning(f'Could not find data for pattern {reg_line}', exc_info=True)
    return data


def parsed_data(email_body: str,
                phone: str = REG3_PHONE,
                form: str = REG3_FORM,
                city: str = REG3_CITY,
                source: str = REG3_SOURCE) -> dict:
    """Generating data found in emails using templates"""
    data = {
        'phone': searching_data(phone, email_body),
        'form': searching_data(form, email_body),
        'city': searching_data(city, email_body),
        'source': searching_data(source, email_body),
    }
    return data


if __name__ == '__main__':

    from pprint import pprint
    from spreadsheetmailing import CRED_1, CRED_2

    imap_1 = email_login(CRED_1)
    imap_2 = email_login(CRED_2)

    while True:
        imap = input('Введите номер email (<1> или <2>): ')
        if imap == '1':
            imap = imap_1
            name = email_name(CRED_1['name'])
        elif imap == '2':
            imap = imap_2
            name = email_name(CRED_2['name'])
        else:
            print('Ошибка ввода. Повторите')
            continue
        box = input('Введите название папки email (<вх> или <исх>): ')
        if box == 'вх':
            box = 'received'
        elif box == 'исх':
            box = 'sent'
        else:
            print('Ошибка ввода. Повторите')
            continue
        try:
            uid = str(input('Введите id email: '))
            pprint(test_pull_mail(name, imap_1, uid, 'received'))
        except Exception:
            print('Ошибка ввода. Повторите')
            continue
        else:
            break
