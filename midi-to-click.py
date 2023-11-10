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
    # return {noteNum_7 + (7 * magnification), (noteNum_7 + 1) + (7 * magnification)}
    return [noteNum_7 + (7 * magnification)]


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
    1: (609, 530),
    2: (653, 530),
    3: (697, 530),
    4: (739, 530),
    5: (781, 530),
    6: (825, 530),
    7: (871, 530),
    8: (915, 530),
    9: (959, 530),
    10: (1003, 530),
    11: (1046, 530),
    12: (1089, 530),
    13: (1132, 530),
    14: (1175, 530),
    15: (1218, 530),
    16: (1261, 530),
    17: (1304, 530),
    18: (1347, 530),
    19: (1390, 530),
    20: (1433, 530),
    21: (1476, 530),
    22: (1519, 530)
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
    for item in note_list:
        delta = item[0] - p
        if delta <= 0 or item[0] == 0:
            continue
        time.sleep(delta / 8)
        p = item[0]
        t = toLyreKey(to36Key(int(item[2])))
        print("{}\t{}\t{}".format(item[0], item[1], t[0]))
        point = keymap[t.pop()]
        pyautogui.leftClick(point[0], point[1])
