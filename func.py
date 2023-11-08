import argparse
import time
from collections import Counter

import mido
import numpy as np
import pyautogui
from mido import Message, MidiFile, MidiTrack

# 1
def tracks_mix(mid, tracks, trackName):
    note_list=[]
    time_sum = 0
    note_on_dict={}
    tempo=500000
    print(len(tracks))

    for track in tracks:
        time_sum = 0
        if trackName is None or track.name == trackName:
            for msg in track:#每个音轨的消息遍历
                if msg.type=='set_tempo':
                    tempo=msg.tempo
                    print('ticks_per_beat', mid.ticks_per_beat)
                    print(msg, mido.tick2second(msg.time, mid.ticks_per_beat, tempo))
                time_sum+=mido.tick2second(msg.time, mid.ticks_per_beat, tempo)
                # if msg.type=='note_on':
                #     note_list.append([time_sum, time_sum, msg.note])
                if msg.type=='note_on':
                    note_on_dict[msg.note]=time_sum
                elif msg.type=='note_off':
                    note_list.append([note_on_dict[msg.note], time_sum, msg.note])

    note_list.sort(key=lambda x:x[0])
    note_list=np.array(note_list)

    return note_list



#  2
def note_overleap_mix(note_list, iou_th=0.2):
    #合并有重叠的音符
    rm_idxs=[]
    for i, note in enumerate(note_list):
        if i in rm_idxs:
            continue
        u=i+1
        while u<len(note_list) and note_list[u][0]<note[1]:
            note_next=note_list[u]
            if note[2] == note_next[2]:
                if note_next[1]<note[1]:
                    rm_idxs.append(u)
                len_u = note_next[1]-note_next[0]
                len_i = note[1]-note[0]
                if (note_next[1]-note[0])/min(len_i, len_u)>iou_th:
                    if len_i<len_u:
                        rm_idxs.append(i)
                        break
                    else:
                        rm_idxs.append(u)
            u+=1
    print('overleap:', len(rm_idxs))
    note_list=np.delete(note_list, rm_idxs, axis=0)
    return note_list
#  3
def note_short_rm(note_list, time_th=0.05):
    #合并有重叠的音符
    rm_idxs=[]
    for i, note in enumerate(note_list):
        if note[1]-note[0] < time_th:
            rm_idxs.append(i)
    print('short:', len(rm_idxs))
    note_list=np.delete(note_list, rm_idxs, axis=0)
    return note_list

def note_mix(note_list, iou_th=0.5):
    #合并同时间音符，适应谱子
    note_list_mix=[]
    rm_idxs = []
    for i, note in enumerate(note_list):
        if i in rm_idxs:
            continue
        u = i + 1
        n_start=note[0]
        n_end=note[1]
        note_v_list=[note[2]]
        while u < len(note_list) and note_list[u][0] < note[1]:
            note_next = note_list[u]
            uni_l = min(note[0], note_next[0])
            uni_h = max(note[1], note_next[1])
            in_l = max(note[0], note_next[0])
            in_h = min(note[1], note_next[1])
            if (in_h-in_l)/(uni_h-uni_l) > iou_th:
                rm_idxs.append(u)
                n_start=min(n_start, uni_l)
                n_end=max(n_end, uni_h)
                note_v_list.append(note_next[2])
            u += 1
        note_v_list=np.array(note_v_list)
        note_list_mix.append([n_start, n_end, round(np.mean(note_v_list)), len(note_v_list)])
    print('mix:', len(rm_idxs))
    return note_list_mix

def note_expend(note_list_mix, log_base=2):
    note_list=[]
    for note in note_list_mix:
        n_exp = int(np.log(note[3])/np.log(log_base)+1)
        if n_exp>1:
            for i in range(n_exp):
                note_list.append([note[0], note[1], note[2]+i])
        else:
            note_list.append(note[:3])
    return note_list
