import os

from func import *


def note2script(note_list, time_th=0.03, note_cap=6, beat=59):
    #求有相交的子集
    note_group_list=[]
    i=0
    while i<len(note_list):
        note=note_list[i]
        note_group=[note]
        i = i + 1
        max_end=note[1]
        while i < len(note_list) and note_list[i][0] < max_end-time_th:
            note_next = note_list[i]
            note_group.append(note_next)
            max_end=max(max_end, note_next[1])
            i+=1
        note_group_list.append(note_group)
    print('note count:', len(note_list))
    print('group count:', len(note_group_list))
    result=[]
    for note_group in note_group_list:
        note_group=np.array(note_group)
        note_group_agg=dict(Counter(note_group[:,2]))

        note_set=list(note_group_agg.keys())
        note_set.sort()
        click=np.array(note_set)
        click_note_map={int(k):int(v) for k,v in zip(note_set, click)}

        for i in range(note_group.shape[0]):
            note_group[i,2]=click_note_map[int(note_group[i,2])]%note_cap

        result.append(note_group)

    result=np.vstack(result)
    result[:,:2]=(result[:,:2]*1000)/beat
    result=result.astype(int)
    result=result[np.argsort(result[:,0]),:]
    return result

def proc_long(script, long_th=30):
    occupy_map = np.zeros((6, np.max(script[:, 1]) + 1), dtype=np.uint8)

    def find_empty_line(l,h):
        for i in range(6):
            if (occupy_map[i,l:h]==0).all():
                return i
            return -1

    def check_short(note):
        if occupy_map[note[2], note[0]] == 1:
            eline = find_empty_line(note[0], note[1] + 1)
            if eline == -1:
                return
            else:
                script[i, 2] = eline
                occupy_map[eline, note[0]] = 1
        else:
            occupy_map[note[2], note[0]] = 1

    #rm_idxs=[]
    for i, note in enumerate(script):
        if note[1]-note[0]>long_th: #长键
            if occupy_map[note[2], note[0]]==1: #起始点被占用
                eline = find_empty_line(note[0], note[1] + 1)  # 查找未被占用的一行
                if eline == -1:  # 全都被占用
                    if (occupy_map[note[2], note[0] + 1:note[1] + 1] == 0).all():  # 起始点前面一格未被占用 (音符首尾重叠)
                        script[i, 0] += 1
                    else: #转为短键
                        script[i, 1] = note[0] + 1
                        check_short(script[i])
                        continue
                else:
                    script[i, 2] = eline
            occupy_map[script[i,2], note[0]:note[1]+1]=1
        else:
            check_short(note)

    #script = np.delete(script, rm_idxs, axis=0)
    return script

# 解析MIDI参考 https://github.com/7eu7d7/GenshinMidi
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OF Generate')
    # MIDI获取 https://www.aigei.com/s?type=midi&dim=jay_chou-pop_music&term=is_vip_false&page=6#resContainer
    parser.add_argument('-p', '--path', default='test.mid', type=str)
    parser.add_argument('-l', '--long', default=30, type=int)
    parser.add_argument('--beat', default=74, type=int)
    parser.add_argument('--iou_mix', default=0.7, type=float)
    parser.add_argument('--log_base', default=3, type=float)
    args = parser.parse_args()

    mid = mido.MidiFile(args.path, clip=True)
    # 主旋律track名称 https://github.com/ryohey/signal -> https://signal.vercel.app/edit
    note_list = tracks_mix(mid, mid.tracks, 'main')

    note_list = note_mix(note_list, iou_th=args.iou_mix)
    note_list = note_expend(note_list, log_base=args.log_base)

    script=note2script(note_list, beat=args.beat)
    script=proc_long(script, long_th=args.long)

    np.save(f'{os.path.basename(args.path)[:-4]}.npy', script)
