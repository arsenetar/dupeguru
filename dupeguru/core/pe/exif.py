# Created By: Virgil Dupras
# Created On: 2011-04-20
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# Heavily based on http://topo.math.u-psud.fr/~bousch/exifdump.py by Thierry Bousch (Public Domain)

import logging

EXIF_TAGS = {
    0x0100: "ImageWidth",
    0x0101: "ImageLength",
    0x0102: "BitsPerSample",
    0x0103: "Compression",
    0x0106: "PhotometricInterpretation",
    0x010A: "FillOrder",
    0x010D: "DocumentName",
    0x010E: "ImageDescription",
    0x010F: "Make",
    0x0110: "Model",
    0x0111: "StripOffsets",
    0x0112: "Orientation",
    0x0115: "SamplesPerPixel",
    0x0116: "RowsPerStrip",
    0x0117: "StripByteCounts",
    0x011A: "XResolution",
    0x011B: "YResolution",
    0x011C: "PlanarConfiguration",
    0x0128: "ResolutionUnit",
    0x012D: "TransferFunction",
    0x0131: "Software",
    0x0132: "DateTime",
    0x013B: "Artist",
    0x013E: "WhitePoint",
    0x013F: "PrimaryChromaticities",
    0x0156: "TransferRange",
    0x0200: "JPEGProc",
    0x0201: "JPEGInterchangeFormat",
    0x0202: "JPEGInterchangeFormatLength",
    0x0211: "YCbCrCoefficients",
    0x0212: "YCbCrSubSampling",
    0x0213: "YCbCrPositioning",
    0x0214: "ReferenceBlackWhite",
    0x828F: "BatteryLevel",
    0x8298: "Copyright",
    0x829A: "ExposureTime",
    0x829D: "FNumber",
    0x83BB: "IPTC/NAA",
    0x8769: "ExifIFDPointer",
    0x8773: "InterColorProfile",
    0x8822: "ExposureProgram",
    0x8824: "SpectralSensitivity",
    0x8825: "GPSInfoIFDPointer",
    0x8827: "ISOSpeedRatings",
    0x8828: "OECF",
    0x9000: "ExifVersion",
    0x9003: "DateTimeOriginal",
    0x9004: "DateTimeDigitized",
    0x9101: "ComponentsConfiguration",
    0x9102: "CompressedBitsPerPixel",
    0x9201: "ShutterSpeedValue",
    0x9202: "ApertureValue",
    0x9203: "BrightnessValue",
    0x9204: "ExposureBiasValue",
    0x9205: "MaxApertureValue",
    0x9206: "SubjectDistance",
    0x9207: "MeteringMode",
    0x9208: "LightSource",
    0x9209: "Flash",
    0x920A: "FocalLength",
    0x9214: "SubjectArea",
    0x927C: "MakerNote",
    0x9286: "UserComment",
    0x9290: "SubSecTime",
    0x9291: "SubSecTimeOriginal",
    0x9292: "SubSecTimeDigitized",
    0xA000: "FlashPixVersion",
    0xA001: "ColorSpace",
    0xA002: "PixelXDimension",
    0xA003: "PixelYDimension",
    0xA004: "RelatedSoundFile",
    0xA005: "InteroperabilityIFDPointer",
    0xA20B: "FlashEnergy",  # 0x920B in TIFF/EP
    0xA20C: "SpatialFrequencyResponse",  # 0x920C    -  -
    0xA20E: "FocalPlaneXResolution",  # 0x920E    -  -
    0xA20F: "FocalPlaneYResolution",  # 0x920F    -  -
    0xA210: "FocalPlaneResolutionUnit",  # 0x9210    -  -
    0xA214: "SubjectLocation",  # 0x9214    -  -
    0xA215: "ExposureIndex",  # 0x9215    -  -
    0xA217: "SensingMethod",  # 0x9217    -  -
    0xA300: "FileSource",
    0xA301: "SceneType",
    0xA302: "CFAPattern",  # 0x828E in TIFF/EP
    0xA401: "CustomRendered",
    0xA402: "ExposureMode",
    0xA403: "WhiteBalance",
    0xA404: "DigitalZoomRatio",
    0xA405: "FocalLengthIn35mmFilm",
    0xA406: "SceneCaptureType",
    0xA407: "GainControl",
    0xA408: "Contrast",
    0xA409: "Saturation",
    0xA40A: "Sharpness",
    0xA40B: "DeviceSettingDescription",
    0xA40C: "SubjectDistanceRange",
    0xA420: "ImageUniqueID",
}

INTR_TAGS = {
    0x0001: "InteroperabilityIndex",
    0x0002: "InteroperabilityVersion",
    0x1000: "RelatedImageFileFormat",
    0x1001: "RelatedImageWidth",
    0x1002: "RelatedImageLength",
}

GPS_TA0GS = {
    0x00: "GPSVersionID",
    0x01: "GPSLatitudeRef",
    0x02: "GPSLatitude",
    0x03: "GPSLongitudeRef",
    0x04: "GPSLongitude",
    0x05: "GPSAltitudeRef",
    0x06: "GPSAltitude",
    0x07: "GPSTimeStamp",
    0x08: "GPSSatellites",
    0x09: "GPSStatus",
    0x0A: "GPSMeasureMode",
    0x0B: "GPSDOP",
    0x0C: "GPSSpeedRef",
    0x0D: "GPSSpeed",
    0x0E: "GPSTrackRef",
    0x0F: "GPSTrack",
    0x10: "GPSImgDirectionRef",
    0x11: "GPSImgDirection",
    0x12: "GPSMapDatum",
    0x13: "GPSDestLatitudeRef",
    0x14: "GPSDestLatitude",
    0x15: "GPSDestLongitudeRef",
    0x16: "GPSDestLongitude",
    0x17: "GPSDestBearingRef",
    0x18: "GPSDestBearing",
    0x19: "GPSDestDistanceRef",
    0x1A: "GPSDestDistance",
    0x1B: "GPSProcessingMethod",
    0x1C: "GPSAreaInformation",
    0x1D: "GPSDateStamp",
    0x1E: "GPSDifferential",
}

INTEL_ENDIAN = ord("I")
MOTOROLA_ENDIAN = ord("M")

# About MAX_COUNT: It's possible to have corrupted exif tags where the entry count is way too high
# and thus makes us loop, not endlessly, but for heck of a long time for nothing. Therefore, we put
# an arbitrary limit on the entry count we'll allow ourselves to read and any IFD reporting more
# entries than that will be considered corrupt.
MAX_COUNT = 0xFFFF


def s2n_motorola(bytes):
    x = 0
    for c in bytes:
        x = (x << 8) | c
    return x


def s2n_intel(bytes):
    x = 0
    y = 0
    for c in bytes:
        x = x | (c << y)
        y = y + 8
    return x


class Fraction:
    def __init__(self, num, den):
        self.num = num
        self.den = den

    def __repr__(self):
        return "%d/%d" % (self.num, self.den)


class TIFF_file:
    def __init__(self, data):
        self.data = data
        self.endian = data[0]
        self.s2nfunc = s2n_intel if self.endian == INTEL_ENDIAN else s2n_motorola

    def s2n(self, offset, length, signed=0, debug=False):
        data_slice = self.data[offset : offset + length]
        val = self.s2nfunc(data_slice)
        # Sign extension ?
        if signed:
            msb = 1 << (8 * length - 1)
            if val & msb:
                val = val - (msb << 1)
        if debug:
            logging.debug(self.endian)
            logging.debug(
                "Slice for offset %d length %d: %r and value: %d",
                offset,
                length,
                data_slice,
                val,
            )
        return val

    def first_IFD(self):
        return self.s2n(4, 4)

    def next_IFD(self, ifd):
        entries = self.s2n(ifd, 2)
        return self.s2n(ifd + 2 + 12 * entries, 4)

    def list_IFDs(self):
        i = self.first_IFD()
        a = []
        while i:
            a.append(i)
            i = self.next_IFD(i)
        return a

    def dump_IFD(self, ifd):
        entries = self.s2n(ifd, 2)
        logging.debug("Entries for IFD %d: %d", ifd, entries)
        if entries > MAX_COUNT:
            logging.debug("Probably corrupt. Aborting.")
            return []
        a = []
        for i in range(entries):
            entry = ifd + 2 + 12 * i
            tag = self.s2n(entry, 2)
            entry_type = self.s2n(entry + 2, 2)
            if not 1 <= entry_type <= 10:
                continue  # not handled
            typelen = [1, 1, 2, 4, 8, 1, 1, 2, 4, 8][entry_type - 1]
            count = self.s2n(entry + 4, 4)
            if count > MAX_COUNT:
                logging.debug("Probably corrupt. Aborting.")
                return []
            offset = entry + 8
            if count * typelen > 4:
                offset = self.s2n(offset, 4)
            if entry_type == 2:
                # Special case: nul-terminated ASCII string
                values = str(self.data[offset : offset + count - 1], encoding="latin-1")
            else:
                values = []
                signed = entry_type == 6 or entry_type >= 8
                for _ in range(count):
                    if entry_type in {5, 10}:
                        # The type is either 5 or 10
                        value_j = Fraction(self.s2n(offset, 4, signed), self.s2n(offset + 4, 4, signed))
                    else:
                        # Not a fraction
                        value_j = self.s2n(offset, typelen, signed)
                    values.append(value_j)
                    offset = offset + typelen
            # Now "values" is either a string or an array
            a.append((tag, entry_type, values))
        return a


def read_exif_header(fp):
    # If `fp`'s first bytes are not exif, it tries to find it in the next 4kb
    def isexif(data):
        return data[0:4] == b"\377\330\377\341" and data[6:10] == b"Exif"

    data = fp.read(12)
    if isexif(data):
        return data
    # ok, not exif, try to find it
    large_data = fp.read(4096)
    try:
        index = large_data.index(b"Exif")
        data = large_data[index - 6 : index + 6]
        # large_data omits the first 12 bytes, and the index is at the middle of the header, so we
        # must seek index + 18
        fp.seek(index + 18)
        return data
    except ValueError:
        raise ValueError("Not an Exif file")


def get_fields(fp):
    data = read_exif_header(fp)
    length = data[4] * 256 + data[5]
    logging.debug("Exif header length: %d bytes", length)
    data = fp.read(length - 8)
    data_format = data[0]
    logging.debug("%s format", {INTEL_ENDIAN: "Intel", MOTOROLA_ENDIAN: "Motorola"}[data_format])
    T = TIFF_file(data)
    # There may be more than one IFD per file, but we only read the first one because others are
    # most likely thumbnails.
    main_ifd_offset = T.first_IFD()
    result = {}

    def add_tag_to_result(tag, values):
        try:
            stag = EXIF_TAGS[tag]
        except KeyError:
            stag = "0x%04X" % tag
        if stag in result:
            return  # don't overwrite data
        result[stag] = values

    logging.debug("IFD at offset %d", main_ifd_offset)
    IFD = T.dump_IFD(main_ifd_offset)
    exif_off = gps_off = 0
    for tag, type, values in IFD:
        if tag == 0x8769:
            exif_off = values[0]
            continue
        if tag == 0x8825:
            gps_off = values[0]
            continue
        add_tag_to_result(tag, values)
    if exif_off:
        logging.debug("Exif SubIFD at offset %d:", exif_off)
        IFD = T.dump_IFD(exif_off)
        # Recent digital cameras have a little subdirectory
        # here, pointed to by tag 0xA005. Apparently, it's the
        # "Interoperability IFD", defined in Exif 2.1 and DCF.
        intr_off = 0
        for tag, type, values in IFD:
            if tag == 0xA005:
                intr_off = values[0]
                continue
            add_tag_to_result(tag, values)
        if intr_off:
            logging.debug("Exif Interoperability SubSubIFD at offset %d:", intr_off)
            IFD = T.dump_IFD(intr_off)
            for tag, type, values in IFD:
                add_tag_to_result(tag, values)
    if gps_off:
        logging.debug("GPS SubIFD at offset %d:", gps_off)
        IFD = T.dump_IFD(gps_off)
        for tag, type, values in IFD:
            add_tag_to_result(tag, values)
    return result
