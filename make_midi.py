from func import *

def make_midi(note_list, path):
    mid = MidiFile(ticks_per_beat=220)  # 给自己的文件定的.mid后缀
    track = MidiTrack()  # 定义声部，一个MidoTrack()就是一个声部
    track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))
    track.append(Message('program_change', channel=0, program=2, time=0))

    msg_list=[]
    for note in note_list:
        msg_list.append((note[0], 'note_on', note[2]))
        msg_list.append((note[1], 'note_off', note[2]))
    msg_list.sort(key=lambda x: x[0])

    last_time=0
    for msg in msg_list:
        dt=mido.second2tick(msg[0]-last_time, mid.ticks_per_beat, 500000)
        track.append(Message(msg[1], note=int(msg[2]), velocity=64, time=int(dt), channel=0))
        last_time=msg[0]
    mid.tracks.append(track)
    mid.save(path)

# 解析MIDI参考 https://github.com/7eu7d7/GenshinMidi
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OF Generate')
    # MIDI获取 https://www.aigei.com/s?type=midi&dim=jay_chou-pop_music&term=is_vip_false&page=6#resContainer
    parser.add_argument('-p', '--path', default='jda-main.mid', type=str)
    args = parser.parse_args()

    mid = mido.MidiFile(args.path, clip=True)
    # 主旋律track名称 https://github.com/ryohey/signal -> https://signal.vercel.app/edit
    note_list = tracks_mix(mid, mid.tracks, 'main')
    note_list = note_overleap_mix(note_list)
    note_list = note_short_rm(note_list)

    make_midi(note_list, 'test.mid')
