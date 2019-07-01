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
    builder.LoadDatabase()
    softioc.iocInit()
    softioc.interactive_ioc(globals())
