import board
import digitalio
from lib.proveskit_ground_station.proveskit_ground_station import GroundStation
from lib.pysquared.cdh import CommandDataHandler
from lib.pysquared.config.config import Config
from lib.pysquared.hardware.busio import _spi_init
from lib.pysquared.hardware.digitalio import initialize_pin
from lib.pysquared.hardware.radio.manager.rfm9x import RFM9xManager
from lib.pysquared.hardware.radio.manager.sx1280 import SX1280Manager
from lib.pysquared.hardware.radio.packetizer.packet_manager import PacketManager
from lib.pysquared.logger import Logger
from lib.pysquared.nvm.counter import Counter

logger: Logger = Logger(
    error_counter=Counter(1),
    colorized=False,
)
config: Config = Config("config.json")

spi0 = _spi_init(
    logger,
    board.SPI0_SCK,
    board.SPI0_MOSI,
    board.SPI0_MISO,
)

spi1 = _spi_init(
    logger,
    board.SPI1_SCK,
    board.SPI1_MOSI,
    board.SPI1_MISO,
)

uhf_radio = RFM9xManager(
    logger,
    config.radio,
    spi0,
    initialize_pin(logger, board.SPI0_CS0, digitalio.Direction.OUTPUT, True),
    initialize_pin(logger, board.RF1_RST, digitalio.Direction.OUTPUT, True),
)

uhf_packet_manager = PacketManager(
    logger,
    uhf_radio,
    config.radio.license,
    0.2,
)

ufh_cdh = CommandDataHandler(
    logger,
    config,
    uhf_packet_manager,
)

sband_radio = SX1280Manager(
    logger,
    config.radio,
    spi1,
    initialize_pin(logger, board.SPI1_CS0, digitalio.Direction.OUTPUT, True),
    initialize_pin(logger, board.RF2_RST, digitalio.Direction.OUTPUT, True),
    initialize_pin(logger, board.RF2_IO0, digitalio.Direction.OUTPUT, True),
    2.4,
    initialize_pin(logger, board.RF2_TX_EN, digitalio.Direction.OUTPUT, False),
    initialize_pin(logger, board.RF2_RX_EN, digitalio.Direction.OUTPUT, False),
)

sband_packet_manager = PacketManager(
    logger,
    sband_radio,
    config.radio.license,
    0.2,
)

sband_cdh = CommandDataHandler(
    logger,
    config,
    sband_packet_manager,
)

ground_station = GroundStation(
    logger,
    config,
    uhf_packet_manager,
    ufh_cdh,
)

ground_station.run()
