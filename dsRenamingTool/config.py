
LOGGING_CONFIG = {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                                "brief": {
                                            "class": "logging.Formatter",
                                            "datefmt": "%d-%m-%Y %I:%M:%S",
                                            "format": "// %(name)s %(asctime)s %(levelname)s| %(message)s //"
                                         },

                                "detailed": {
                                            "class": "logging.Formatter",
                                            "datefmt": "%d-%m-%Y %I:%M:%S",
                                            "format": " %(message)s Call: %(name)s.%(funcName)s;"
                                            }
                },
                "handlers": {
                        "console":{
                                  "level": "DEBUG",
                                  "class": "logging.StreamHandler",
                                  "formatter": "brief",
                                  "stream" : "ext://sys.stdout"
                                  },

                        "file_handler": {
                                  "level": "DEBUG",
                                  "class": "logging.FileHandler",
                                  "formatter": "detailed",
                                  "filename": "",
                                  "mode": "a",
                                  "encoding": "utf-8"
                                        }
                             },
                "loggers": { },
                "root": {
                        "handlers": ["console", "file_handler"],
                        "level": "DEBUG"
                        }
}
