"""
配置：常量定义
"""
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent

# 本地数据库路径
DB_PATH: Path = BASE_DIR / "resources" / "History_Chronology.db"

# 远程数据库下载地址
REMOTE_DB_URL: str = "https://github.com/Hellohistory/OpenPrepTools/raw/master/history_chronology/resources/History_Chronology.db"

# 支持的年份上下限
YEAR_MIN: int = -840
YEAR_MAX: int = 1912

# 各种主题样式表路径
LIGHT_STYLE_QSS: Path = BASE_DIR / "resources" / "style.qss"
DARK_STYLE_QSS: Path = BASE_DIR / "resources" / "style_dark.qss"
BLUE_STYLE_QSS: Path = BASE_DIR / "resources" / "style_blue.qss"
GREEN_STYLE_QSS: Path = BASE_DIR / "resources" / "style_green.qss"
ORANGE_STYLE_QSS: Path = BASE_DIR / "resources" / "style_orange.qss"
HIGHCONTRAST_STYLE_QSS: Path = BASE_DIR / "resources" / "style_highcontrast.qss"
SOLARIZED_STYLE_QSS: Path = BASE_DIR / "resources" / "style_solarized.qss"

# 应用程序图标路径
ICON_PATH: Path = BASE_DIR / "resources" / "logo.ico"