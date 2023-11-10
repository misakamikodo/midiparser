from func import *


def to36Key(noteValve):
    # 1/-1, 1/-1, 1/2, 1/2/3, 1/2/3, 2/3/-1, 1/-1 SpinnerSettings 三级音阶分配 -1不取
    sp = [1, 1, 1, 2, 3, 3, 3]
    # 钢琴有88键，选择7组 7x12=84
    noteValve = noteValve - 24
    grepNumber = int(noteValve / 12)
    if noteValve <= 1:
        return 1
    elif noteValve >= 84:
        return 84
    elif sp[grepNumber] != -1:
        return noteValve - (grepNumber * 12) + ((sp[grepNumber] - 1) * 12) + 1
    else:
        return -1


# 按照黑键的设定，按照黑键左边的白键为索引
def invalidKey(noteNum_7, magnification):
    # return [noteNum_7 + (7 * magnification), (noteNum_7 + 1) + (7 * magnification)]
    return [noteNum_7 + (7 * magnification)]
    # return [(noteNum_7 + 1) + (7 * magnification)]


# 根据黑键的设定，36键进一步压缩成21键
def toLyreKey(noteValue):
    # 音阶？
    magnification = 0
    noteNum_12 = 1
    if noteValue <= 12:
        noteNum_12 = noteValue
    elif noteValue <= 24:
        magnification = 1
        noteNum_12 = noteValue - 12
    elif noteValue <= 36:
        magnification = 2
        noteNum_12 = noteValue - 24

    if noteNum_12 == 1:
        return [1 + (7 * magnification)]
    elif noteNum_12 == 2:
        return invalidKey(1, magnification)
    elif noteNum_12 == 3:
        return [2 + (7 * magnification)]
    elif noteNum_12 == 4:
        return invalidKey(2, magnification)
    elif noteNum_12 == 5:
        return [3 + (7 * magnification)]
    elif noteNum_12 == 6:
        return [4 + (7 * magnification)]
    elif noteNum_12 == 7:
        return invalidKey(4, magnification)
    elif noteNum_12 == 8:
        return [5 + (7 * magnification)]
    elif noteNum_12 == 9:
        return invalidKey(5, magnification)
    elif noteNum_12 == 10:
        return [6 + (7 * magnification)]
    elif noteNum_12 == 11:
        return invalidKey(6, magnification)
    elif noteNum_12 == 12:
        return [7 + (7 * magnification)]

    return None


# https://www.pianoabrsm.com/piano
keymap = {
    1: 'Z',
    2: 'X',
    3: 'C',
    4: 'Q',
    5: 'W',
    6: 'E',
    7: 'R',
    8: 'T',
    9: 'Y',
    10: 'U',
    11: 'I',
    12: 'O',
    13: 'P',
    14: '[',
    15: ']',
    16: 'V',
    17: 'B',
    18: 'N',
    19: 'M',
    20: ',',
    21: '.',
    22: '/'
}

# 解析MIDI参考 https://github.com/7eu7d7/GenshinMidi
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OF Generate')
    # MIDI获取 https://www.aigei.com/s?type=midi&dim=jay_chou-pop_music&term=is_vip_false&page=6#resContainer
    parser.add_argument('-p', '--path', default='yq-main.mid', type=str)
    # parser.add_argument('-l', '--long', default=30, type=int)
    # parser.add_argument('--beat', default=74, type=int)
    parser.add_argument('--iou_mix', default=0.7, type=float)
    parser.add_argument('--log_base', default=3, type=float)
    parser.add_argument('--main_track', default=None, type=str)
    args = parser.parse_args()

    mid = mido.MidiFile(args.path, clip=True)
    # 主旋律track名称 https://github.com/ryohey/signal -> https://signal.vercel.app/edit
    note_list = tracks_mix(mid, mid.tracks, 'main')
    note_list = note_overleap_mix(note_list)
    note_list = note_short_rm(note_list)

    note_list = note_mix(note_list, iou_th=args.iou_mix)
    note_list = note_expend(note_list, log_base=args.log_base)
    print("音符开始\t音符结束\t音符")
    p = -2
    group = []
    for item in note_list:
        delta = item[0] - p
        group.append(item)
        if delta != 0:
            time.sleep(delta / 2)
            for each in group:
                t = toLyreKey(to36Key(int(each[2])))
                print("{}\t{}\t{}".format(each[0], each[1], t[0]))
                point = keymap[t.pop()]
                pyautogui.press(point)
            group.clear()
        p = item[0]
