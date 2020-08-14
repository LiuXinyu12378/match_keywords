import logging
import os

base_dir = os.getcwd()
logdir = os.path.join(base_dir,"logging")

if not os.path.exists(logdir):
    os.makedirs(logdir)

logfile_path = os.path.join(logdir,"log.txt")

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)     #设置日志等级为INFO
handler = logging.FileHandler(logfile_path)           #日志保存文件位置
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)

logger.addHandler(handler)
logger.addHandler(console)

# logger.info("Start print log")
# logger.debug("Do something")
# logger.warning("Something maybe fail.")
# logger.info("Finish")