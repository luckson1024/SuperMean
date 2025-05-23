print("# backend/utils/logger.py")
print("\n")
print("import logging")
print("import os")
print("from logging.handlers import RotatingFileHandler")
print("\n")
print("def setup_logging():")
print("    \"\"\"Sets up the global logging configuration.\"\"\"")
print("    log_level = os.environ.get(\"LOG_LEVEL\", \"INFO\").upper()")
print("    log_format = \"%(asctime)s - %(name)s - %(levelname)s - %(message)s\"")
print("    log_dir = \"logs\"")
print("    log_file = os.path.join(log_dir, \"supermean.log\")")
print("\n")
print("    # Create logs directory if it doesn't exist")
print("    if not os.path.exists(log_dir):")
print("        os.makedirs(log_dir)")
print("\n")
print("    # Root logger configuration")
print("    logging.basicConfig(level=log_level, format=log_format)")
print("\n")
print("    # File handler for rotating logs")
print("    file_handler = RotatingFileHandler(")
print("        log_file,")
print("        maxBytes=1024 * 1024 * 5,  # 5 MB")
print("        backupCount=5             # Keep up to 5 old logs")
print("    )")
print("    file_handler.setLevel(log_level)")
print("    file_handler.setFormatter(logging.Formatter(log_format))")
print("\n")
print("    # Add file handler to root logger")
print("    logging.getLogger().addHandler(file_handler)")
print("\n")
print("    logging.info(\"Logging configured.\")")
print("\n")
print("def get_logger(name: str):")
print("    \"\"\"Gets a logger instance for a specific module.\"\"\"")
print("    return logging.getLogger(name)")
print("\n")
print("# Optional: Call setup_logging() when the module is imported")
print("setup_logging()")
print("```")