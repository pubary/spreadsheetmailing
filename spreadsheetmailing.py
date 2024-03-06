import datetime
import logging
import os
import threading
from time import sleep

import gspread
import schedule
from dotenv import load_dotenv
from gspread import Client, Spreadsheet, Worksheet

from config import *
from log_config import logfile

from utils import pull_data, push_seen_mail_uids, email_login, email_name, parsed_data, \
    erase_files, is_uidsfile


load_dotenv()

SHEET_URL = os.getenv('GOOGLE_SHEET_URL')
NAME_1 = os.getenv('EMAIL_NAME_1')
NAME_2 = os.getenv('EMAIL_NAME_2')
NAME_3 = os.getenv('EMAIL_NAME_3')
CRED = os.getenv('CREDENTIALS')

CRED_1 = {
    'name': NAME_1,
    'pass': os.getenv('EMAIL_PASS_1'),
    'server': os.getenv('IMAP_SERVER_1'),
    'port': int(os.getenv('IMAP_PORT_1')),
}
CRED_2 = {
    'name': NAME_2,
    'pass': os.getenv('EMAIL_PASS_2'),
    'server': os.getenv('IMAP_SERVER_2'),
    'port': int(os.getenv('IMAP_PORT_2')),
}
CRED_3 = {
    'name': NAME_3,
    'pass': os.getenv('EMAIL_PASS_3'),
    'server': os.getenv('IMAP_SERVER_3'),
    'port': int(os.getenv('IMAP_PORT_3')),
}
files_names = [
    logfile,
    f'{PREFIX}{email_name(NAME_1)}{EXT}',
    f'{PREFIX}{email_name(NAME_2)}{EXT}',
    f'{PREFIX}{email_name(NAME_3)}{EXT}'
]

logger = logging.getLogger(__name__)


def thr():
    """Creation of a flow to check the execution of schedule."""
    while True:
        schedule.run_pending()
        sleep(1)


def create_ws(sh: Spreadsheet, name: str) -> Worksheet:
    """A table is created with the desired name in the spreadsheet-file."""
    ws = sh.add_worksheet(name, rows=1, cols=5)
    return ws


def fill_rows(ws: Worksheet, rows: list) -> None:
    """Writing rows to a spreadsheet"""
    if rows:
        try:
            ws.acell('A2').value
        except Exception:
            ws.append_rows(rows, value_input_option='USER_ENTERED')
        else:
            ws.insert_rows(rows, row=2, value_input_option='USER_ENTERED')


def create_rows(mail_data: dict, ws: Worksheet, pars_ws: Worksheet = None) -> None:
    """Creating rows with data for the selected spreadsheet."""
    rows = list()
    pars_rows = list()
    for data in mail_data:
        if pars_ws\
                and data['type'] == 'received'\
                and data.get('subject', '').lower() == SUBJECT_BOX_3.lower():
            body = parsed_data(data.get('email_body', ''))
            pars_row = [data.get('date', ''),
                        data.get('time', ''),
                        body.get('phone', ''),
                        body.get('form', ''),
                        body.get('city', ''),
                        body.get('source', '')]
            pars_rows.append(pars_row)
        else:
            m_type = data['type']
            if m_type == 'received':
                m_type = 'Входящий'
                addr = data.get('from', '')
            else:
                m_type = 'Исходящий'
                addr = data.get('to', '')
            row = [data.get('date', ''),
                   data.get('time', ''),
                   m_type,
                   addr,
                   data.get('email_body', '')]
            rows.append(row)
    if pars_ws:
        fill_rows(pars_ws, pars_rows)
    fill_rows(ws, rows)


def is_header(ws: Worksheet, name: str) -> bool:
    """Checks if the header exists in the spreadsheet."""
    header = choose_header(name)
    values = ws.row_values(1)
    return values == header


def choose_header(name: str):
    """Selecting a header for the table depending on the name of the mailbox."""
    if name == TABLE_NAME_3:
        header = TABLE_HEADER_3
    else:
        header = TABLE_HEADER
    return header


def write_header(ws: Worksheet, name: str):
    """Writing a header to the cells of the first row of a spreadsheet."""
    header = choose_header(name)
    alphabet = [chr(i) for i in range(97, 123)]
    letters = alphabet[slice(len(header))]
    ws.update(f'{"".join(letters[:1]).capitalize()}1:{"".join(letters[-1:]).capitalize()}1', [header, ])


def table(sh: Spreadsheet, name: str) -> Worksheet:
    """Opening or creating a spreadsheet with a header"""
    try:
        ws = sh.worksheet(name)
        if not is_header(ws, name):
            if ws.row_values(1):
                ws.insert_row([])
            write_header(ws, name)
    except gspread.exceptions.WorksheetNotFound:
        ws = create_ws(sh, name)
        write_header(ws, name)
    return ws


def push_data(imap, cred: dict, ws: Worksheet, pars_ws=None):
    """Getting data from emails and writing it to a spreadsheet-file table"""
    short_name = email_name(cred['name'])
    data = pull_data(short_name, imap)
    if data and not MY_DEBUG:
        create_rows(data[0], ws, pars_ws)
        new_mails = data[1].copy()
        push_seen_mail_uids(short_name, data[1])
        logger.info(f'Data from messages {new_mails} from the box "{short_name}" are written to the table')


def main():
    """The main function with main loop"""
    gc: Client = gspread.service_account(f"./{CRED}")
    sh: Spreadsheet = gc.open_by_url(SHEET_URL)
    ws_1 = table(sh, NAME_1)
    ws_2 = table(sh, NAME_2)
    ws_3 = table(sh, NAME_3)
    ws_4 = table(sh, TABLE_NAME_3)
    imap_1 = email_login(CRED_1)
    imap_2 = email_login(CRED_2)
    imap_3 = email_login(CRED_3)
    is_uidsfile(NAME_1)
    is_uidsfile(NAME_2)
    is_uidsfile(NAME_3)
    i: int = 0
    while True:
        sleep(TIMEOUT)
        try:
            push_data(imap_1, CRED_1, ws_1)
        except gspread.exceptions.APIError:
            logger.exception(f'Error writing data to spreadsheet "{NAME_1}"', exc_info=True)
        except Exception:
            logger.warning(f'Data was not written to the spreadsheet "{NAME_1}"', exc_info=True)
            imap_1 = None
            imap_1 = email_login(CRED_1)
        try:
            push_data(imap_2, CRED_2, ws_2)
        except gspread.exceptions.APIError:
            logger.exception(f'Error writing data to spreadsheet "{NAME_2}"', exc_info=True)
        except Exception:
            logger.warning(f'Data was not written to the spreadsheet "{NAME_2}"', exc_info=True)
            imap_2 = None
            imap_2 = email_login(CRED_2)
        try:
            push_data(imap_3, CRED_3, ws_3, ws_4)
        except gspread.exceptions.APIError:
            logger.exception(f'Error writing data to spreadsheet "{NAME_3}"', exc_info=True)
        except Exception:
            logger.warning(f'Data was not written to the spreadsheet "{NAME_3}"', exc_info=True)
            imap_3 = None
            imap_3 = email_login(CRED_3)
        if not imap_1 or not imap_2 or not imap_3:
            logger.warning('Can not connect to any email')
            raise ConnectionError('Error connecting to any email in <def email_login()>')
        i += 1
        if i // 10:
            logger.info(f'10 tries were completed')
            i = 0


if __name__ == '__main__':
    threading.Thread(target=thr).start()
    logger.info(f'\n\nThe service has started. Emails being viewed: {NAME_1}, {NAME_2}, {NAME_3}.')
    schedule.every().sunday.at(TIME_ERASE_FILES).do(erase_files, files_names=files_names)
    logger.info(f'Scheduled tasks:\n{schedule.get_jobs()}')
    print(f'Service spreadsheetmailing.py started at {datetime.datetime.now()}.')

    while True:
        try:
            main()
        except Exception as e:
            sleep(100)
            logger.exception(f'Service has restarted after error:\n', exc_info=True)
            print(f'Service spreadsheetmailing.py restarted at {datetime.datetime.now()} after error!:\n{e}')
            continue
