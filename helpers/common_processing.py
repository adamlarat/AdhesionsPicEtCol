# -*- coding: utf-8 -*

from typing import Optional


# OLD function when using uno
# def verifierDate(date_str, errorOut=True):
#     """ Cette fonction vérifie qu'une date sous forme de chaîne de caractère est correcte """
#     if date_str == '' or date_str == 'EXT':
#         return date_str
#     ### HelloAsso renvoie un format bizarre %Y-%m-%dT%H%M%S.%ns+GMT
#     liste    = date_str.replace('T',' ').replace('.',' ').split(' ')
#     if len(liste) == 1:
#         try:
#             myDate = datetime.strptime(date_str,'%d/%m/%Y')
#         except:
#             if errorOut:
#                 print("La date n'est pas formatée correctement: ",date_str,". Changée en ''")
#             return ''
#     elif len(liste) == 2:
#         try:
#             myDate = datetime.strptime(date_str,'%d/%m/%Y %H:%M:%S')
#         except:
#             if errorOut:
#                 print("La date n'est pas formatée correctement: ",date_str,". Changée en ''")
#             return ''
#     elif len(liste) == 3:
#         ### Format de date HelloAsso
#         try:
#             myDate = datetime.strptime(date_str.split('.')[0],'%Y-%m-%dT%H:%M:%S')
#         except:
#             if errorOut:
#                 print("La date n'est pas formatée correctement: ",date_str,". Changée en ''")
#             return ''
#         return myDate.strftime('%d/%m/%Y %H:%M:%S')
#     else:
#         if errorOut:
#             print('Format de date non conforme :',date_str,". Changée en ''")
#         return ''
#     return date_str



def verifierDate(date_str: str, errorOut=True) -> str:
    """ Cette fonction vérifie qu'une date sous forme de chaîne de caractère est correcte """
    from dateutil import parser
    from datetime import datetime
    import pytz
    out_date = date_str
    if date_str == '' or date_str == 'EXT':
        out_date = date_str

    try:
        # Parse the date string
        parsed_date = parser.parse(date_str)

        # If the parsed date has a timezone, convert it to UTC
        if parsed_date.tzinfo is not None:
            parsed_date = parsed_date.astimezone(pytz.UTC)

        # Format the date based on whether it includes time information
        if parsed_date.hour == 0 and parsed_date.minute == 0 and parsed_date.second == 0:
            out_date = parsed_date.strftime('%d/%m/%Y')
        else:
            out_date = parsed_date.strftime('%d/%m/%Y %H:%M:%S')

    except ValueError as e:
        if errorOut is True:
            print(f"La date n'est pas formatée correctement: {date_str}. Erreur: {str(e)}")
    return out_date



def get_logger(
    log_file: Optional[str] = None,
    terminal_output: bool = False,
    roll_over: bool = True,
    in_logger_name: str = "logger",
    **kwargs,
):
    """
    Return a logger
    If logging file already file already exist, it is compeltely replaced
    by new logging

    :param log_file: complete path to the register logging file
    :param terminal_output: if the logging entries are written to sdout,
        defaults to False
    :type terminal_output: bool, optional
    :param roll_over: if True, if the log file already exist it will be overwritten,
        default to True. If you activate `multiprocessing` you are likely to open/close
        the logger within numerous processe, so you should set roll_over to False.
    :type roll_over: bool, optional.
    :param in_logger_name: name for the logger.

    :return: logging.Logger or multiprocessing.Logger

    """
    import logging
    from logging.handlers import RotatingFileHandler
    import os
    import sys
    import warnings

    logger_level = kwargs.get("level", logging.INFO)
    format_str = kwargs.get(
        "format_str",
        "> %(asctime)s :: %(filename)s :: %(lineno)s :: %(funcName)s() :: %(levelname)s :: %(message)s",
    )

    logger = logging.getLogger(name=in_logger_name)

    # prevent children logger sharing handlers
    logger.propagate = False

    logger.setLevel(logger_level)
    formatter = logging.Formatter(format_str)
    if len(logger.handlers) > 0:
        # handler already captured
        return logger

    if terminal_output:
        # output text in terminal
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logger_level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if log_file is not None:
        file_handler = RotatingFileHandler(log_file, "w", backupCount=0)
        if roll_over:
            if isinstance(log_file, str):
                should_roll_over = os.path.isfile(log_file)
            else:
                # pathlib
                should_roll_over = log_file.exists()
            if should_roll_over:  # log already exists, roll over!
                file_handler.doRollover()

        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


    try:  # get fancy colored outputs in terminal
        import coloredlogs

        coloredlogs.install(
            level="INFO",
            fmt=format_str,
            level_styles={
                "warning": {"color": 118}
            },
            field_styles={
                "asctime": {"color": 115},
                "hostname": {"color": "magenta"},
                "lineno": {"color": 195},
                "levelname": {"color": "green"},
                "message": {"color": 253},
                "name": {"color": 225},
                "funcName": {"color": 75},
                "programname": {"color": "white"},
                "username": {"color": "yellow"},
            },
        )
    except ImportError:
        # the package is not installed
        # not a problem as it is just extra colors
        # warnings.warn(
        #     "\n\nInstall coloredlogs with \n`pip install coloredlogs`\n"
        #     + "if you want a colorfull output of loggings in terminal !!\n\n"
        # )
        pass
    return logger





if __name__ == "__main__":
    # Test the function
    test_dates = [
        "2022-09-13T20:27:04.7996404+02:00",
        "2023-08-05",
        "05/08/2023",
        "2023-08-05 14:30:00",
        "05/08/2023 14:30:00",
        "",
        "EXT"
    ]

    for date in test_dates:
        result = verifierDate(date)
        print(f"Input: {date}")
        print(f"Output: {result}")
        print("-----------------------")
