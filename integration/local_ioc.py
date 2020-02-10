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
    test = builder.aOut("TEST", initial_value=0, on_update=notify, always_update=True)
    ain = builder.aIn("AI", initial_value=0)
    longname = builder.aIn("THIS-IS-A-VERY-LONG-PV-NAME-AI", initial_value=0)
    aout = builder.aOut("AO")
    # builder.bIn('BI')
    mbbout = builder.mbbOut("MBBO", ("OFF", 0), ("ON", 1), ("NOT SURE", 2))
    mbbout_one = builder.mbbOut("MBBO1", ("OFF", 0))
    mbbin = builder.mbbIn("MBBI", ("OFF", 0), ("ON", 1), ("NOT SURE", 2))
    wave = builder.WaveformOut("TESTPV", length=5)
    long = builder.longOut("TESTPV_LONG")
    double = builder.aOut("TESTPV_DBL")
    s = builder.stringOut("TESTPV_STR")

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
