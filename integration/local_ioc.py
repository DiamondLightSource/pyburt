#!/dls_sw/prod/R3.14.12.3/support/pythonSoftIoc/2-6/pythonIoc
# It's important to use pythonIoc for this, otherwise it won't work.

import sys

if __name__ == "__main__":

    try:
        from pkg_resources import require

        require("numpy")
        require("cothread")
        require("iocbuilder")
        # import dls_packages
        from softioc import softioc, builder
    except ImportError as e:
        print(e)
        print("You must use the pythonIoc interpreter for this program.")
        print("/dls_sw/prod/R3.14.12.3/support/pythonSoftIoc/2-6/pythonIoc")
        sys.exit()

    IOC_NAME = "SR-CS-TEST-01"

    def notify(value):
        print("notify", value)

    builder.SetDeviceName(IOC_NAME)
    # ai, ao
    ain = builder.aIn("AI")
    aout = builder.aOut("AO")
    longname = builder.aIn("THIS-IS-A-VERY-LONG-PV-NAME-AI")
    # bo
    bout = builder.boolOut("BO", "ZERO VAL", "ONE VAL")
    # mbbi, mbbo
    mbbout = builder.mbbOut("MBBO", ("OFF", 0), ("ON", 1), ("NOT SURE", 2))
    mbbout_one = builder.mbbOut("MBBO1", ("OFF", 0))
    mbbin = builder.mbbIn("MBBI", ("OFF", 0), ("ON", 1), ("NOT SURE", 2))

    # float only available via typed waveform
    scalar_float = builder.WaveformOut("TESTPV_FLOAT", length=1)
    arr_float = builder.WaveformOut("TESTPV_ARR_FLOAT", length=160)

    # long
    longout = builder.longOut("TESTPV_LONG")
    arr_long = builder.WaveformOut("TESTPV_ARR_LONG", length=5, datatype="l")

    # double
    scalar_double = builder.aOut("TESTPV_DBL")
    arr_double = builder.WaveformOut("TESTPV_ARR_DBL", length=40, datatype="d")

    # string
    scalar_str = builder.stringOut("TESTPV_STR")
    arr_str = builder.WaveformOut("TESTPV_ARR_STR", length=5, datatype="S")

    # char only available via typed waveform
    scalar_char = builder.WaveformOut("TESTPV_CHAR", length=1, datatype="b")
    arr_char = builder.WaveformOut("TESTPV_ARR_CHAR", length=1000, datatype="b")

    # short only available via typed waveform
    scalar_short = builder.WaveformOut("TESTPV_SHORT", length=1, datatype="h")
    arr_short = builder.WaveformOut("TESTPV_ARR_SHORT", length=5, datatype="h")

    bcdorbit_pvs = [
        "BCD_LIMIT",
        "SLEW_RATE",
        "BCD_X_S1",
        "BCD_Y_S2",
        "BCD_X_S3",
        "BCD_Y_S4",
        "BCD_X_S5",
        "BCD_Y_S6",
        "BCD_X_S7",
        "BCD_Y_S8",
        "BCD_X_S9",
        "BCD_Y_S10",
        "BCD_X_S11",
        "BCD_Y_S12",
        "BCD_X_S13",
        "BCD_Y_S14",
        "BCD_X_S15",
        "BCD_Y_S16",
        "BCD_X_S17",
        "BCD_Y_S18",
        "BCD_X_S19",
        "BCD_Y_S20",
        "BCD_X_S21",
        "BCD_Y_S22",
        "BCD_X_S23",
        "BCD_Y_S24",
        "BCD_X_S25",
        "BCD_Y_S26",
        "BCD_X_S27",
        "BCD_Y_S28",
        "BCD_X_S29",
        "BCD_Y_S30",
        "BCD_X_S31",
        "BCD_Y_S32",
        "BCD_X_S33",
        "BCD_Y_S34",
        "BCD_X_S35",
        "BCD_Y_S36",
        "BCD_X_S37",
        "BCD_Y_S38",
        "BCD_X_S39",
        "BCD_Y_S40",
        "BCD_X_S41",
        "BCD_Y_S42",
    ]

    for i in range(len(bcdorbit_pvs)):
        globals()["pv%s" % i] = builder.WaveformOut(bcdorbit_pvs[i], length=1)

    builder.LoadDatabase()
    softioc.iocInit()
    softioc.interactive_ioc(globals())
