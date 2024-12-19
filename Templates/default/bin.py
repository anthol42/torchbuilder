from . import logger
from .color import Color, ResetColor

# Available loggers: log, warn, error

log = logger.Logger(console=True, T=logger.LoggerType.INFO, name="INFO", logColor=None)
log.config(show_name=True, show_time=True, show_type=False, show_origin=False,
              name_formatter=f"<CAPS>{Color(40)}[{'{}'}]{ResetColor()}",
              time_formatter=lambda x: (f'{Color(244)}{x.strftime("%Y-%m-%d %H:%M:%S")}{ResetColor()}', False),
              start_sep=" ")
warn = logger.Logger(console=True, T=logger.LoggerType.WARNING, name="WARNING", logColor=None)
warn.config(show_name=True, show_time=True, show_type=False, show_origin=True,
              name_formatter=f"<CAPS>{Color(226)}[{'{}'}]{ResetColor()}",
              time_formatter=lambda x: (f'{Color(244)}{x.strftime("%Y-%m-%d %H:%M:%S")}{ResetColor()}', False),
              start_sep="\n\t", origin_formatter=f"{Color(244)} |  From: {'{}'} -- line no {'{}'}{ResetColor()}")
error = logger.Logger(console=True, T=logger.LoggerType.ERROR, name="ERROR", logColor=Color(203))
error.config(show_name=True, show_time=True, show_type=False, show_origin=True,
              name_formatter=f"<CAPS>{Color(196)}[{'{}'}]{ResetColor()}",
              time_formatter=lambda x: (f'{Color(244)}{x.strftime("%Y-%m-%d %H:%M:%S")}{ResetColor()}', False),
              start_sep="\n\t", origin_formatter=f"{Color(244)} |  From: {'{}'} -- line no {'{}'}{ResetColor()}")