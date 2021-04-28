from tests.ioc_manager import IocManager

LOCAL_PV_FLOAT = "SR-CS-SOFT-01:FLOAT"
LOCAL_PV_ARR_FLOAT = "SR-CS-SOFT-01:FLOAT_ARR"

LOCAL_PV_LONG = "SR-CS-SOFT-01:LONGIN"
LOCAL_PV_ARR_LONG = "SR-CS-SOFT-01:LONG_ARR"

LOCAL_PV_DBL = "SR-CS-SOFT-01:AI"
LOCAL_PV_ARR_DBL = "SR-CS-SOFT-01:DOUBLE_ARR"

LOCAL_PV_STR = "SR-CS-SOFT-01:STRINGIN"
LOCAL_PV_ARR_STR = "SR-CS-SOFT-01:STRING_ARR"

LOCAL_PV_ENUM = "SR-CS-SOFT-01:MBBI"

LOCAL_PV_CHAR_UNINIT = "SR-CS-SOFT-01:CHAR_SCALAR_UNINIT"
LOCAL_PV_CHAR = "SR-CS-SOFT-01:CHAR_SCALAR"
LOCAL_PV_ARR_CHAR = "SR-CS-SOFT-01:CHAR_ARR"

LOCAL_PV_SHORT = "SR-CS-SOFT-01:TESTPV_SHORT"
LOCAL_PV_ARR_SHORT = "SR-CS-SOFT-01:SHORT_ARR"


def create_ioc_manager():
    manager = IocManager()

    manager.add_ai_record("SR-CS-SOFT-01:AI", VAL="0", PREC="2", PINI="YES")
    manager.add_ao_record(
        "SR-CS-SOFT-01:AO", VAL="70.0", DRVL="70.0", DRVH="150.0", PREC="1", PINI="YES"
    )
    manager.add_waveform_record(
        "SR-CS-SOFT-01:DOUBLE_ARR", length="8", ftvl="DOUBLE", PINI="YES"
    )
    manager.add_waveform_record(
        "SR-CS-SOFT-01:DOUBLE_ARR_UNINIT", length="8", ftvl="DOUBLE", PINI="YES"
    )
    manager.add_waveform_record(
        "SR-CS-SOFT-01:FLOAT", length="1", ftvl="FLOAT", PINI="YES"
    )
    manager.add_waveform_record(
        "SR-CS-SOFT-01:FLOAT_ARR", length="8", ftvl="FLOAT", PINI="YES"
    )
    manager.add_waveform_record(
        "SR-CS-SOFT-01:FLOAT_ARR_UNINIT", length="8", ftvl="FLOAT", PINI="YES"
    )
    manager.add_stringin_record("SR-CS-SOFT-01:EMPTYSTRING")
    manager.add_stringin_record(
        "SR-CS-SOFT-01:STRINGIN",
        DESC="Gen Time Current Provider",
        DTYP="General Time",
        INP="@BESTTCP",
        SCAN="1 second",
    )
    manager.add_stringout_record(
        "SR-CS-SOFT-01:STRINGOUT", DESC="Gen Time Current Provider", SCAN="1 second"
    )
    manager.add_waveform_record(
        "SR-CS-SOFT-01:STRING_ARR", length="8", ftvl="STRING", PINI="YES"
    )
    manager.add_waveform_record(
        "SR-CS-SOFT-01:STRING_ARR_UNINIT", length="8", ftvl="STRING", PINI="YES"
    )
    manager.add_waveform_record(
        "SR-CS-SOFT-01:CHAR_SCALAR_UNINIT", length="1", ftvl="CHAR", PINI="YES"
    )
    manager.add_waveform_record(
        "SR-CS-SOFT-01:CHAR_SCALAR", length="1", ftvl="CHAR", PINI="YES"
    )
    manager.add_waveform_record(
        "SR-CS-SOFT-01:CHAR_ARR", length="8", ftvl="CHAR", PINI="YES"
    )
    manager.add_waveform_record(
        "SR-CS-SOFT-01:CHAR_ARR_UNINIT", length="8", ftvl="CHAR", PINI="YES"
    )
    manager.add_waveform_record(
        "SR-CS-SOFT-01:SHORT_ARR", length="8", ftvl="SHORT", PINI="YES"
    )
    manager.add_longin_record(
        "SR-CS-SOFT-01:LONGIN",
        DESC="Gen Time Error Count",
        DTYP="General Time",
        INP="@GETERRCNT",
        SCAN="1 second",
        HIHI="1",
        HHSV="MAJOR",
    )
    manager.add_longout_record(
        "SR-CS-SOFT-01:LONGOUT",
        DESC="Gen Time Error Count",
        SCAN="1 second",
        HIHI="1",
        HHSV="MAJOR",
    )
    manager.add_waveform_record(
        "SR-CS-SOFT-01:LONG_ARR", length="8", ftvl="LONG", PINI="YES"
    )
    manager.add_waveform_record(
        "SR-CS-SOFT-01:LONG_ARR_UNINIT", length="8", ftvl="LONG", PINI="YES"
    )
    manager.add_mbbi_record("SR-CS-SOFT-01:MBBI", states=["OK", "Fault", "Warning"])
    manager.add_mbbo_record(
        "SR-CS-SOFT-01:MBBO",
        states=["Running", "Maintenance", "Test", "OFFLINE"],
        DESC="SR-CS-IOC-01 Acc Mode",
        ZRSV="NO_ALARM",
        ONSV="MINOR",
        TWSV="MINOR",
        THSV="MAJOR",
    )
    manager.add_bi_record(
        "SR-CS-SOFT-01:BI", VAL="0", ZNAM="OK", ONAM="Fault", PINI="YES"
    )
    manager.add_bo_record(
        "SR-CS-SOFT-01:BO",
        DESC="Gen Time Error Reset",
        DTYP="General Time",
        OUT="@RSTERRCNT",
        ZNAM="Reset",
        ONAM="Reset",
    )

    return manager
