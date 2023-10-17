from typing import Optional, Union
from pydantic import BaseModel, Field, field_validator


class ContentProtectionItem(BaseModel):
    cenc_default_KID: str = Field(..., alias="@cenc:default_KID")
    schemeIdUri: str = Field(..., alias="@schemeIdUri")
    value: Optional[str] = Field(None, alias="@value")
    mspr_pro: Optional[str] = Field(None, alias="mspr:pro")
    cenc_pssh: Optional[str] = Field(None, alias="cenc:pssh")


class Initialization(BaseModel):
    range: str = Field(..., alias="@range")


class SegmentBase(BaseModel):
    indexRange: str = Field(..., alias="@indexRange")
    Initialization: Initialization


class RepresentationItem(BaseModel):
    id: str = Field(..., alias="@id")
    width: str = Field(..., alias="@width")
    height: str = Field(..., alias="@height")
    bandwidth: str = Field(..., alias="@bandwidth")
    codecs: str = Field(..., alias="@codecs")
    frameRate: str = Field(..., alias="@frameRate")
    BaseURL: str
    SegmentBase: SegmentBase


class Initialization1(BaseModel):
    range: str = Field(..., alias="@range")


class SegmentBase1(BaseModel):
    indexRange: str = Field(..., alias="@indexRange")
    Initialization: Initialization1


class AudioChannelConfiguration(BaseModel):
    schemeIdUri: str = Field(..., alias="@schemeIdUri")
    value: str = Field(..., alias="@value")


class RepresentationItem1(BaseModel):
    id: str = Field(..., alias="@id")
    bandwidth: str = Field(..., alias="@bandwidth")
    audioSamplingRate: str = Field(..., alias="@audioSamplingRate")
    codecs: str = Field(..., alias="@codecs")
    BaseURL: str
    SegmentBase: SegmentBase1
    AudioChannelConfiguration: AudioChannelConfiguration


class AdaptationSetItem(BaseModel):
    mimeType: str = Field(..., alias="@mimeType")
    segmentAlignment: str = Field(..., alias="@segmentAlignment")
    subsegmentAlignment: Optional[str] = Field(None, alias="@subsegmentAlignment")
    startWithSAP: Optional[str] = Field(None, alias="@startWithSAP")
    subsegmentStartsWithSAP: Optional[str] = Field(None, alias="@subsegmentStartsWithSAP")
    bitstreamSwitching: Optional[str] = Field(None, alias="@bitstreamSwitching")
    ContentProtection: list[ContentProtectionItem]
    Representation: Union[list[RepresentationItem], RepresentationItem1]
    lang: Optional[str] = Field(None, alias="@lang")


class Period(BaseModel):
    start: str = Field(..., alias="@start")
    duration: str = Field(..., alias="@duration")
    id: str = Field(..., alias="@id")
    AdaptationSet: list[AdaptationSetItem]

    @field_validator("AdaptationSet", mode="before")
    @classmethod
    def to_list(cls, v):
        if isinstance(v, list):
            return v
        return [AdaptationSetItem.model_validate(v)]


class MPD(BaseModel):
    xmlns_xsi: str = Field(..., alias="@xmlns:xsi")
    xmlns: str = Field(..., alias="@xmlns")
    xmlns_cenc: str = Field(..., alias="@xmlns:cenc")
    xmlns_mspr: str = Field(..., alias="@xmlns:mspr")
    xsi_schemaLocation: str = Field(..., alias="@xsi:schemaLocation")
    type: str = Field(..., alias="@type")
    minBufferTime: str = Field(..., alias="@minBufferTime")
    profiles: str = Field(..., alias="@profiles")
    mediaPresentationDuration: str = Field(..., alias="@mediaPresentationDuration")
    Period: list[Period]

    @field_validator("Period", mode="before")
    @classmethod
    def to_list(cls, v):
        if isinstance(v, list):
            return v
        return [Period.model_validate(v)]


class BaseMPD(BaseModel):
    MPD: MPD
