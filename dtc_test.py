# DTC test scenario for ELM327-emulator
# Merge this into the running emulator with: merge dtc_test
# Or start with: python3 -m elm -s car
# Then in the console: merge dtc_test
#
# This makes mode 03 return two DTCs: P0301 (Cyl 1 misfire) and P0420 (Cat efficiency)

from elm.obd_message import ECU_ADDR_E, ECU_R_ADDR_E, ELM_FOOTER
from elm.obd_message import HD, SZ, DT

ObdMessage = {
    'car': {
        # Must use SHOW_DIAG_TC — that's the key the 'car' scenario uses for mode 03
        'SHOW_DIAG_TC': {
            'Request': '^03' + ELM_FOOTER,
            'Descr': 'Show stored Diagnostic Trouble Codes',
            'Header': ECU_ADDR_E,
            'Response':
                # 43 = mode 03 response
                # 02 = number of DTCs
                # 03 01 = P0301 (Cylinder 1 Misfire Detected)
                # 04 20 = P0420 (Catalyst System Efficiency Below Threshold)
                HD(ECU_R_ADDR_E) + SZ('06') + DT('43 02 03 01 04 20'),
        },
    }
}
