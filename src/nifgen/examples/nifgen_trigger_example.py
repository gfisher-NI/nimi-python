import argparse
import nifgen
import sys
import time


def example(resource_name1, resource_name2, options, waveform, frequency, amplitude, offset, phase, gen_time):
    with nifgen.Session(resource_name=resource_name1, options=options) as session1, nifgen.Session(resource_name=resource_name2, options=options) as session2:
        session_list = [session1, session2]
        for session in session_list:
            session.output_mode = nifgen.OutputMode.FUNC
            session.configure_standard_waveform(waveform=nifgen.Waveform[waveform], amplitude=amplitude, frequency=frequency, dc_offset=offset, start_phase=phase)
        session1.start_trigger_type = nifgen.StartTriggerType.SOFTWARE_EDGE
        session2.start_trigger_type = nifgen.StartTriggerType.DIGITAL_EDGE
        session2.digital_edge_start_trigger_edge = nifgen.StartTriggerDigitalEdgeEdge.RISING
        session2.digital_edge_start_trigger_source = '/' + resource_name1 + '/0/StartTrigger'
        with session2.initiate():
            with session1.initiate():
                session1.send_software_edge_trigger(nifgen.Trigger.START)
                time.sleep(gen_time)


def _main(argsv):
    supported_waveforms = list(nifgen.Waveform.__members__.keys())[:-1]  # no support for user-defined waveforms in example
    parser = argparse.ArgumentParser(description='Generates the standard function.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-n1', '--resource-name1', default='PXI1Slot2', help='Resource name of a National Instruments Function Generator')
    parser.add_argument('-n2', '--resource-name2', default='PXI1Slot3', help='Resource name of a National Instruments Function Generator')
    parser.add_argument('-w', '--waveform', default=supported_waveforms[0], choices=supported_waveforms, type=str.upper, help='Standard waveform')
    parser.add_argument('-f', '--frequency', default=1000, type=float, help='Frequency (Hz)')
    parser.add_argument('-a', '--amplitude', default=1.0, type=float, help='Amplitude (Vpk-pk)')
    parser.add_argument('-o', '--offset', default=0.0, type=float, help='DC offset (V)')
    parser.add_argument('-p', '--phase', default=0.0, type=float, help='Start phase (deg)')
    parser.add_argument('-t', '--time', default=5.0, type=float, help='Generation time (s)')
    parser.add_argument('-op', '--option-string', default='', type=str, help='Option string')
    args = parser.parse_args(argsv)
    example(args.resource_name1, args.resource_name2, args.option_string, args.waveform, args.frequency, args.amplitude, args.offset, args.phase, args.time)


def main():
    _main(sys.argv[1:])


def test_example():
    options = {'simulate': True, 'driver_setup': {'Model': '5433 (2CH)', 'BoardType': 'PXIe', }, }
    example('PXI1Slot2', 'PXI1Slot3', options, 'SINE', 1000, 1.0, 0.0, 0.0, 5.0)


def test_main():
    cmd_line = ['--option-string', 'Simulate=1, DriverSetup=Model:5433 (2CH);BoardType:PXIe', ]
    _main(cmd_line)


if __name__ == '__main__':
    main()