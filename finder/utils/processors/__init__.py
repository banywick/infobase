# processors/__init__.py
from .screw_bolt_processor import ScrewBoltProcessor
from .rivet_processor import RivetProcessor
from .pin_processor import PinProcessor
from .key_processor import KeyProcessor
from .cotter_pin_processor import CotterPinProcessor
from .stud_processor import StudProcessor
from .ring_processor import RingProcessor
from .washer_processor import WasherProcessor
from .nut_processor import NutProcessor
from .default_processor import DefaultProcessor

__all__ = [
    'ScrewBoltProcessor',
    'RivetProcessor',
    'PinProcessor',
    'KeyProcessor',
    'CotterPinProcessor',
    'StudProcessor',
    'RingProcessor',
    'WasherProcessor',
    'NutProcessor',
    'DefaultProcessor'
]