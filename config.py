MY_DEBUG = False
TIMEOUT: int = 38  # break between email checks (default about 40)
SEARCH_DEPTH = 0  # possible additional past days for seen emails
TIME_ERASE_FILES = '01:01'  # partial file cleaning time every Sunday
LOG_NAME = 'blackorhideymailing'  # name of the .log file
MAX_LINES_IN_FILE: int = 500  # number of undeleted lines in the uids or log files after they were partially cleared
# !!! This number must be guaranteed to be greater than the maximum number of letters received and sent per day to any mailbox
PREFIX = 'uids_'  # file prefix for ID viewed emails
EXT = '.txt'  # file extension for ID viewed emails

TABLE_HEADER: list = ['Дата', 'Время', 'Тип', 'Почта клиента', 'Текст письма']
# the names of the columns in which information from emails is written for email box 1 and 2
TABLE_HEADER_3: list = ['Дата', 'Время', 'Телефон', 'Форма', 'Город', 'Медиа-источник']
# the names of the columns in which information from emails is written for email box no.3
TABLE_NAME_3: str = 'Заявки maslaopt.ru'
SUBJECT_BOX_3: str = 'Новая заявка maslaopt.ru'
# if the email from mailbox no.3 has this subject, then its text will be parsed for recording in a spreadsheet
REG3_PHONE: str = r'Телефон:[\n\r](.+)[\n\r]*'
REG3_FORM: str = r'Форма:[\n\r](.+)[\n\r]*'
REG3_CITY: str = r'Город:[\n\r](.+)[\n\r]*'
REG3_SOURCE: str = r'Медиа-источник:[\n\r](.+)[\n\r]*'
# parsing templates for searching data in the text of letters from the mailbox no.3

LEN_TEXT: int = 10000  # Do not set this value above 50000!
# length of the text from the email that will be written to the spreadsheet.
# Google spreadsheets do not allow you to write text longer than 50000 characters.
