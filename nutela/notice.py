import numpy as np
from astropy.time import Time
from pydantic import BaseModel, field_validator


class AstrotrackNotice(BaseModel):
    """IceCube AstroTrack GCN Notice."""

    title: str
    notice_date: str
    notice_type: str
    stream: str
    run_num: str
    event_num: str
    src_ra: float
    src_dec: float
    src_error: float
    src_error50: float
    discovery_date: str
    discovery_time: str
    energy: float
    signalness: float
    far: float
    sun_dist: float
    sun_postn: float
    moon_dist: float
    moon_postn: float
    gal_coords: str
    ecl_coords: str
    comments: str
    revision: int

    @field_validator("src_ra", "src_dec", "sun_postn", "moon_postn", mode="before")
    @classmethod
    def coord_validator(cls, value: str) -> float:
        v = float(value.split("d")[0])
        return v

    @field_validator("signalness", "energy", "far", mode="before")
    @classmethod
    def float_validator(cls, value: str) -> float:
        signalness = float(value.split(" ")[0])
        return signalness

    @field_validator("src_error", "src_error50", mode="before")
    @classmethod
    def src_error_validator(cls, value: str) -> float:
        """
        Parse the 90% source error string in arcminutes and convert to degrees.

        :param value: Source error string
        :return: Degrees
        """
        src_error = float(value.split(" ")[0]) / 60.0
        return src_error

    @field_validator("moon_dist", "sun_dist", mode="before")
    @classmethod
    def distance_validator(cls, value: str) -> float:
        dist = abs(float(value.split(" ")[0]))
        return dist

    @property
    def event_time(self) -> Time:
        """
        Return the discovery date and time as an astropy Time object.

        :return: Time object
        """
        date = (
            self.discovery_date.split(";")[-1].split("(")[0].strip().replace("/", "-")
        )
        time = self.discovery_time.split("{")[1].split("}")[0].strip()
        return Time(f"20{date}T{time}", format="isot")

    @property
    def area(self) -> float:
        """
        Calculate the area of the error circle in square degrees.

        :return: Area in square degrees
        """
        return np.pi * (self.src_error**2)

    @property
    def area_square(self) -> float:
        """
        Calculate the area of the error circle in square degrees.

        :return: Area in square degrees
        """
        return 4.0 * self.src_error**2.0
