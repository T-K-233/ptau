from struct import unpack, pack
import csv


def read_vlv(file):
    """
    convert Variable Length Values to integers
    """
    bin_str = ''
    char = file.read(1)
    while(unpack('>B', char)[0] > 127):
        bin_str += bin(ord(char) - 128)[2:].zfill(7)
        char = file.read(1)
    bin_str += bin(ord(char))[2:].zfill(7)
    return  int(bin_str, 2)

def midicsv(midifile, csvfile):
    """
    Converts midi file into csv file

    :param midifile: path to the midifile
    :param csvfile: path to the csvfile
    :returns: None
    """
    with open(midifile, 'rb') as f:
        with open(csvfile, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar = "'")

            # File Header
            file_head = f.read(4)
            if file_head == b'MThd':
                data = unpack('>LHHH', f.read(10))
                midi_format, track_number, division = data[1:]
                writer.writerow([0, 0, 'Header', midi_format, track_number, division])
            print('< 0,0,Header,1,2,240 >')

            # Track Header
            for track in range(1, track_number+1):
                tick = 0
                track_head = f.read(4)
                if track_head == b'MTrk':
                    writer.writerow([track, tick, 'Start_track'])
                    print('< %d, 0, Start_track >' % track)

                # Track Size
                track_size = unpack('>L', f.read(4))[0]
                print('Track Size: ', track_size)

                while True:
                    # Read Tick
                    v_time = read_vlv(f)
                    tick += v_time

                    # Parse Event
                    raw_e = f.read(1)

                    # MetaEvents
                    if unpack('>B', raw_e)[0] == 255:
                        meta_type = unpack('>B', f.read(1))[0]
                        length = read_vlv(f)
                        print('< MetaEvent Type of ', meta_type, length)

                        if meta_type == 3:
                            writer.writerow([track, tick, 'Title_t', '"%s"' % f.read(length).decode()])
                        elif meta_type == 33:
                            f.read(length)
                        elif meta_type == 47:
                            writer.writerow([track, tick, 'End_track'])
                            f.read(0)
                            break
                        elif meta_type == 81:
                            int_tempo = unpack('>I', b'\0' + f.read(length))[0]    # Convert 24bit to 32bit
                            writer.writerow([track, tick, 'Tempo', int_tempo])
                        elif meta_type == 84:
                            print('< %d, %d, SMPTE >' % (track, tick))
                            f.read(length)
                        elif meta_type == 88:
                            print('< %d, %d, TimeSig >' % (track, tick))
                            f.read(length)
                        elif meta_type == 89:
                            print('< %d, %d, KeySig >' % (track, tick))
                            f.read(length)
                    
                    # midi_event
                    else:
                        event_value = unpack('>B', raw_e)[0]

                        if 128 <= event_value <= 143:
                            curr_event = 'Note_off_c'
                            n = event_value - 128
                            kk, vv = unpack('>BB', f.read(2))
                            writer.writerow([track, tick, curr_event, n, kk, vv])
                        
                        elif 144 <= event_value <= 159:
                            curr_event = 'Note_on_c'
                            n = event_value - 144
                            kk, vv = unpack('>BB', f.read(2))
                            writer.writerow([track, tick, curr_event, n, kk, vv])
                            
                        elif 176 <= event_value <= 191:
                            curr_event = 'Control_c'
                            n = event_value - 176
                            kk, vv = unpack('>BB', f.read(2))
                            writer.writerow([track, tick, curr_event, n, kk, vv])
                        
                        elif 192 <= event_value <= 207:
                            curr_event = 'Program_c'
                            n = event_value - 192
                            pp = unpack('>B', f.read(1))[0]
                            writer.writerow([track, tick, curr_event, n, pp])

                        else:
                            if curr_event in ['Note_on_c', 'Note_off_c', 'Control_c']:
                                kk, vv = unpack('>BB', raw_e + f.read(1))
                                writer.writerow([track, tick, curr_event, n, kk, vv])
                                
                            elif curr_event == 'Program_c':
                                pp = unpack('>B', raw_e)[0]
                                writer.writerow([track, tick, curr_event, n, pp])
                                
            
            writer.writerow([0, 0, 'End_of_file'])
    print('== MIDICSV Done ==')


def csvmidi(csvfile, midifile):
    raise NotImplementedError('csvmidi() is not implemented yet')
