import datetime
import json
import os
import re
import shutil

import urllib3
from natsort import natsorted

script_dir = os.path.dirname(__file__)
clips_path = os.path.join(script_dir, "clips/")
final_video_path = os.path.join(script_dir, "videos/")
ffmpeg = "C:/Users/<user>/Downloads/ffmpeg-2022-10-13-git-9e8a327e68-full_build/bin/ffmpeg"
series_name = "La liga de los malos"
id_link = 0000000


def save_flist(files):
    f_data = 'file \'' + '\'\nfile \''.join(files) + '\''
    print(f_data)

    f_list = 'list.txt'
    with open(f_list, 'w', encoding='gbk') as f:
        f.write(f_data)
    return f_list


def download_videos(in_video_list, in_side):
    c_list = in_video_list['720']['videos']
    for index, video in enumerate(c_list):
        clip_name = f'clip-{id_link}-{in_side}-{index}.mp4'
        next_clip_name = f'clip-{id_link}-{in_side}-{index + 1}.mp4'
        if os.path.exists(clips_path + clip_name) and os.path.getsize(clips_path + clip_name) > 0:
            if index + 1 < len(c_list) and os.path.exists(clips_path + next_clip_name):
                continue
        print(f'Downloading clip {index} url: {video["url"]}')
        with http.request('GET', video['url'], preload_content=False) as resp, open(clips_path + clip_name,
                                                                                    'wb') as out_file:
            shutil.copyfileobj(resp, out_file)
        resp.release_conn()


http = urllib3.PoolManager()
r = http.request(
    'GET',
    f'https://beelup.com/player.php?id={id_link}',
    headers={
        'Cookie': 'primera_visita=SI; consentimiento_cookie=1; email=scrapper%40gmail.com; telefono=1500000000; nombre=scrap; apellido=per; fecha_nacimiento_dia=1; fecha_nacimiento_mes=1; fecha_nacimiento_anio=1969'})
html = r.data.decode('utf-8')
video_lista = json.loads(re.findall("g_video_lista = JSON\.parse\('(.*)'\)", html)[0])
fecha_inicio = re.findall("fecha_inicio.*\'(.*)\'", html)[0]
date = datetime.datetime.strptime(fecha_inicio, '%Y-%m-%d %H:%M:%S.%f')
complejo = re.findall("complejo.*\'(.*)\'", html)[0]
cancha = re.findall("cancha: \'(.*)\'", html)[0].replace(' -', '')
final_file_name = f'{series_name} - {datetime.datetime.strftime(date, "%Y-%m-%d")} - {complejo} {cancha}.mp4'
for side in video_lista.keys():
    download_videos(video_lista[side], side)

os.chdir(clips_path)
if {"der", "izq"} <= video_lista.keys():
    clips_der = []
    clips_izq = []
    for filename in natsorted(os.listdir(clips_path)):
        if filename.startswith(f'clip-{id_link}-der'):
            clips_der.append(clips_path + filename)
        if filename.startswith(f'clip-{id_link}-izq'):
            clips_izq.append(clips_path + filename)
    os.chdir(final_video_path)
    call_der = f'{ffmpeg} -f concat -safe 0 -i {save_flist(clips_der)} -c copy "der-{id_link}.mp4" -y'
    os.system(call_der)
    call_izq = f'{ffmpeg} -f concat -safe 0 -i {save_flist(clips_izq)} -c copy izq-{id_link}.mp4 -y'
    os.system(call_izq)
    merge_call = f'{ffmpeg} -i izq-{id_link}.mp4 -i der-{id_link}.mp4 -filter_complex "[0:v][1:v]hstack=inputs=2[v];[0:a][1:a]amerge=inputs=2[a]" -map "[v]" -map "[a]" -ac 2 "{final_file_name}"'
    os.system(merge_call)

    os.remove(f"der-{id_link}.mp4")
    os.remove(f"izq-{id_link}.mp4")

else:
    clips = []
    for filename in natsorted(os.listdir(clips_path)):
        if filename.startswith(f'clip-{id_link}'):
            clips.append(clips_path + filename)
    os.chdir(final_video_path)
    call = f'{ffmpeg} -f concat -safe 0 -i {save_flist(clips)} -c copy "{final_file_name}" -y'
    os.system(call)

os.remove('list.txt')
os.chdir(clips_path)
for filename in natsorted(os.listdir(clips_path)):
    if filename.startswith(f'clip-{id_link}'):
        os.remove(filename)
