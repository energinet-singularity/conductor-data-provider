import pandas as pd
import logging

log = logging.getLogger(__name__)

class ACLineSegment():

    def __init__(self, mrid: str):
        self.__mrid = mrid

    @property
    def mrid(self) -> str:
        return self.__mrid

    @mrid.setter
    def mrid(self, value: str):
        if len(value) > 10:
            log.error('to many chars.')
            raise AttributeError('Cannot set mrid')
        else:
            self.__mrid = value

test = ACLineSegment(mrid='abdeigsfde')
print(getattr(test, 'mrid'))

test1 = ACLineSegment()