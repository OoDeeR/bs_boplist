from os import path
import re
import requests as req
import json
import math
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import messagebox
import glob
import base64
from PIL import Image, ImageTk, UnidentifiedImageError
from unidecode import unidecode

class Score():
    def __init__(self, lbid,song_hash, song, mapper, diff, score, pp, stars, time):
        self.lbid = lbid
        self.hash = song_hash
        self.song = song
        self.mapper = mapper
        self.diff = diff
        self.score = score
        self.pp = pp
        self.stars = stars
        self.time = time

class Player():
    def __init__(self, name, ssid):
        self.name = name
        self.ssid = ssid

def getPlayer1():
    global p1_ssid
    global p1_name
    global page_count
    
    p1_ssid = ent_player1.get()
    if not re.match('[0-9]{16,17}',p1_ssid):
        ent_player1.delete(0,'end')
        ent_player1.insert(-1, 'invalid ID')
        drpdwn_p1_choice.set('Player 1')
        btn_get_p1_scores.config(state = 'disabled')
    else:    
        url = 'https://scoresaber.com/api/player/' + p1_ssid + '/basic'
        response = req.get(url).json()
        try:
            p1_name = response['name']
            drpdwn_p1_choice.set(p1_name)
            url_st = 'https://scoresaber.com/api/player/' + p1_ssid + '/scores'
            response2 = req.get(url_st).json()
            score_total = response2['metadata']['total']
            page_count = math.trunc(score_total / 100)+1
            btn_get_p1_scores.config(state = 'normal')
            if path.exists(p1_name + '.json'):
                lbl_p1_local_cache.config(text = p1_name + '.json')
                p1_json = json.load(open(p1_name + '.json'))
                score_list = []
                for item in p1_json['scores']:
                    score_item = Score(item['lbid'],item['hash'],item['song'],item['mapper'],item['diff'],item['score'],item['pp'],item['stars'],item['time'])
                    score_list.append(score_item)
                score_list = sorted(score_list, key = lambda x: x.time, reverse = True)
                last_update = score_list[0].time[0:10]
                lbl_p1_last_update.config(text = last_update)
                    
            else:
                lbl_p1_local_cache.config(text = 'no local file')
        except KeyError:
            ent_player1.delete(0,'end')
            ent_player1.insert(-1, 'invalid ID')
            drpdwn_p1_choice.set('Player 1')
            btn_get_p1_scores.config(state = 'disabled')

def setPlayer1():
    global p1_name
    global p1_ssid
    global page_count

    p1_name = drpdwn_p1_choice.get()
    loc_json_file = p1_name + '.json'
    lbl_p1_local_cache["text"] = loc_json_file
    p1_json = json.load(open(loc_json_file))
    score_list = []
    for item in p1_json['scores']:
        score_item = Score(item['lbid'],item['hash'],item['song'],item['mapper'],item['diff'],item['score'],item['pp'],item['stars'],item['time'])
        score_list.append(score_item)
    score_list = sorted(score_list, key = lambda x: x.time, reverse = True)
    last_update = score_list[0].time[0:10]
    lbl_p1_last_update.config(text = last_update)
    ent_player1.delete(0,'end')
    ent_player1.insert(-1, p1_json['metadata'][0]['ssid'])
    btn_get_p1_scores.config(state = 'normal')
    p1_ssid = ent_player1.get()
    url_st = 'https://scoresaber.com/api/player/' + p1_ssid + '/scores'
    response2 = req.get(url_st).json()
    score_total = response2['metadata']['total']
    page_count = math.trunc(score_total / 100)+1

def getPlayer1File():

    file_path = filedialog.askopenfilename(title = 'Choose your player json file!', filetypes = (('json files','*.json'),('all files','*.*')))
    p1_json = json.load(open(file_path))

    lbl_p1_local_cache["text"] = str(file_path).rsplit('/',1)[-1]


    score_list = []
    for item in p1_json['scores']:
        score_item = Score(item['lbid'],item['hash'],item['song'],item['mapper'],item['diff'],item['score'],item['pp'],item['stars'],item['time'])
        score_list.append(score_item)
    score_list = sorted(score_list, key = lambda x: x.time, reverse = True)
    last_update = score_list[0].time[0:10]
    lbl_p1_last_update.config(text = last_update)

def getP1Scores():
    global p1_ssid
    global p1_name
    global page_count

    player1 = Player(p1_name, p1_ssid)
    p1_list = [player1]

    p1_file = p1_name + '.json'
    try:
        with open(p1_file, 'w', encoding = 'utf-8') as p1_scores:
            i = 1
            scorelist = []
            while i <= page_count:
                url = 'https://scoresaber.com/api/player/' + p1_ssid + '/scores?limit=100&sort=top&page=' + str(i)
                response = req.get(url).json()
                for item in response['playerScores']:
                    lbid = item['leaderboard']['id']
                    song_hash = item['leaderboard']['songHash']
                    songname = item['leaderboard']['songName']
                    mapper = item['leaderboard']['levelAuthorName']
                    rawdiff = item['leaderboard']['difficulty']['difficulty']
                    diff = ''
                    match rawdiff:
                        case 1:
                            diff = 'Easy'
                        case 3:
                            diff = 'Normal'
                        case 5:
                            diff = 'Hard'
                        case 7:
                            diff = 'Expert'
                        case 9:
                            diff = 'ExpertPlus'
                        case _:
                            diff = 'na'
                    if item['leaderboard']['maxScore'] != 0:
                        score = str(round(item['score']['baseScore'] / item['leaderboard']['maxScore'] * 100, 2)) + ' %'
                    else:
                        score = item['score']['baseScore']
                    pp = item['score']['pp']
                    stars = item['leaderboard']['stars']
                    date = item['score']['timeSet']

                    score_item = Score(lbid,song_hash,songname,mapper,diff,score,pp,stars,date)

                    scorelist.append(score_item)
                    
                    
                btn_get_p1_scores.config(text = ('page: ' + str(i) + ' / ' + str(page_count)))
                root.update()
                i = i + 1
            btn_get_p1_scores.config(text = 'Update Scores')
            p1_string = json.dumps([ob.__dict__ for ob in p1_list])
            json_string = json.dumps([ob.__dict__ for ob in scorelist])
            whole_string = '{"metadata" : ' + p1_string + ', "scores" : ' + json_string + '}'

            beautified_json = json.dumps(json.loads(whole_string), indent = 2)
            p1_scores.write(beautified_json)

            lbl_p1_local_cache.config(text = p1_file)
            scorelist = sorted(scorelist, key = lambda x: x.time, reverse = True)
            last_update = scorelist[0].time[0:10]
            lbl_p1_last_update.config(text = last_update)

        p1_scores.close()
    
    except Exception as e:
        print(e)

    
def getPlayer2():
    global p2_ssid
    global p2_name
    global page_count_p2
    
    p2_ssid = ent_player2.get()
    if not re.match('[0-9]{16,17}',p2_ssid):
        ent_player2.delete(0,'end')
        ent_player2.insert(-1, 'invalid ID')
        drpdwn_p1_choice.set('Player 2')
        btn_get_p2_scores.config(state = 'disabled')
    else:    
        url = 'https://scoresaber.com/api/player/' + p2_ssid + '/basic'
        response = req.get(url).json()
        try:
            p2_name = response['name']
            drpdwn_p2_choice.set(p2_name)
            url_st = 'https://scoresaber.com/api/player/' + p2_ssid + '/scores'
            response2 = req.get(url_st).json()
            score_total = response2['metadata']['total']
            page_count_p2 = math.trunc(score_total / 100)+1
            btn_get_p2_scores.config(state = 'normal')
            if path.exists(p2_name + '.json'):
                lbl_p2_local_cache.config(text = p2_name + '.json')
                p2_json = json.load(open(p2_name + '.json'))
                score_list = []
                for item in p2_json['scores']:
                    score_item = Score(item['lbid'],item['hash'],item['song'],item['mapper'],item['diff'],item['score'],item['pp'],item['stars'],item['time'])
                    score_list.append(score_item)
                score_list = sorted(score_list, key = lambda x: x.time, reverse = True)
                last_update = score_list[0].time[0:10]
                lbl_p2_last_update.config(text = last_update)
                    
            else:
                lbl_p2_local_cache.config(text = 'no local file')
        except KeyError:
            ent_player2.delete(0,'end')
            ent_player2.insert(-1, 'invalid ID')
            drpdwn_p2_choice.set('Player 1')
            btn_get_p2_scores.config(state = 'disabled')

def setPlayer2():
    global p2_name
    global p2_ssid
    global page_count_p2

    p2_name = drpdwn_p2_choice.get()
    loc_json_file = p2_name + '.json'
    lbl_p2_local_cache["text"] = loc_json_file
    p2_json = json.load(open(loc_json_file))
    score_list = []
    for item in p2_json['scores']:
        score_item = Score(item['lbid'],item['hash'],item['song'],item['mapper'],item['diff'],item['score'],item['pp'],item['stars'],item['time'])
        score_list.append(score_item)
    score_list = sorted(score_list, key = lambda x: x.time, reverse = True)
    last_update = score_list[0].time[0:10]
    lbl_p2_last_update.config(text = last_update)
    ent_player2.delete(0,'end')
    ent_player2.insert(-1, p2_json['metadata'][0]['ssid'])
    btn_get_p2_scores.config(state = 'normal')
    p2_ssid = ent_player2.get()
    url_st = 'https://scoresaber.com/api/player/' + p2_ssid + '/scores'
    response2 = req.get(url_st).json()
    score_total = response2['metadata']['total']
    page_count_p2 = math.trunc(score_total / 100)+1

def getPlayer2File():

    file_path = filedialog.askopenfilename(title = 'Choose your player json file!', filetypes = (('json files','*.json'),('all files','*.*')))
    p2_json = json.load(open(file_path))

    lbl_p2_local_cache["text"] = str(file_path).rsplit('/',1)[-1]


    score_list = []
    for item in p2_json['scores']:
        score_item = Score(item['lbid'],item['hash'],item['song'],item['mapper'],item['diff'],item['score'],item['pp'],item['stars'],item['time'])
        score_list.append(score_item)
    score_list = sorted(score_list, key = lambda x: x.time, reverse = True)
    last_update = score_list[0].time[0:10]
    lbl_p2_last_update.config(text = last_update)

def getP2Scores():
    global p2_ssid
    global p2_name
    global page_count_p2

    player2 = Player(p2_name, p2_ssid)
    p2_list = [player2]

    p2_file = p2_name + '.json'
    try:
        with open(p2_file, 'w', encoding = 'utf-8') as p2_scores:
            i = 1
            scorelist = []
            while i <= page_count_p2:
                url = 'https://scoresaber.com/api/player/' + p2_ssid + '/scores?limit=100&sort=top&page=' + str(i)
                response = req.get(url).json()
                for item in response['playerScores']:
                    lbid = item['leaderboard']['id']
                    song_hash = item['leaderboard']['songHash']
                    songname = item['leaderboard']['songName']
                    mapper = item['leaderboard']['levelAuthorName']
                    rawdiff = item['leaderboard']['difficulty']['difficulty']
                    diff = ''
                    match rawdiff:
                        case 1:
                            diff = 'Easy'
                        case 3:
                            diff = 'Normal'
                        case 5:
                            diff = 'Hard'
                        case 7:
                            diff = 'Expert'
                        case 9:
                            diff = 'ExpertPlus'
                        case _:
                            diff = 'na'
                    if item['leaderboard']['maxScore'] != 0:
                        score = str(round(item['score']['baseScore'] / item['leaderboard']['maxScore'] * 100, 2)) + ' %'
                    else:
                        score = item['score']['baseScore']
                    pp = item['score']['pp']
                    stars = item['leaderboard']['stars']
                    date = item['score']['timeSet']

                    score_item = Score(lbid,song_hash,songname,mapper,diff,score,pp,stars,date)

                    scorelist.append(score_item)

                
                btn_get_p2_scores.config(text = ('page: ' + str(i) + ' / ' + str(page_count_p2)))
                root.update()
                i = i + 1
            btn_get_p2_scores.config(text = 'Update Scores')
            p2_string = json.dumps([ob.__dict__ for ob in p2_list])
            json_string = json.dumps([ob.__dict__ for ob in scorelist])
            whole_string = '{"metadata" : ' + p2_string + ', "scores" : ' + json_string + '}'

            beautified_json = json.dumps(json.loads(whole_string), indent=2)
            p2_scores.write(beautified_json)

            lbl_p2_local_cache.config(text = p2_file)
            scorelist = sorted(scorelist, key = lambda x: x.time, reverse = True)
            last_update = scorelist[0].time[0:10]
            lbl_p2_last_update.config(text = last_update)

        p2_scores.close()

    except Exception as e:
        print(e)


def disableEntry():
    if select_all.get() == 1:
        ent_max_number.delete(0,tk.END)
        ent_max_number.config(state = 'disabled')
    elif select_all.get() == 0:
        ent_max_number.config(state = 'normal')

incl_no_score = False
only_no_score = False

def setInclNoScore():
    global only_no_score
    global incl_no_score

    if var_include_no_score.get() == 1:
        incl_no_score = True
        only_no_score = False
        var_no_score_only.set(0)
    elif var_include_no_score.get() == 0:
        incl_no_score = False

def setOnlyNoScore():
    global only_no_score
    global incl_no_score

    if var_no_score_only.get() == 1:
        only_no_score = True
        incl_no_score = False
        var_include_no_score.set(0)
    elif var_no_score_only.get() == 0:
        only_no_score = False


def isNumber(n):
    try:
        float(n)
        return True

    except ValueError:
        return False

image_path = ''

def getImage():
    global photo
    global image_path
    global b64_img
        
    file_path = filedialog.askopenfilename(title = 'Choose your player json file!', filetypes = (('Image files','.jpg .png .bmp'),('all files','*.*')))
    image_path = open(file_path, 'rb')
    b64_img = base64.b64encode(image_path.read()).decode('utf-8')
    try:
        img = Image.open(file_path, mode = 'r')
        img2 = img.resize((75,75),Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img2)
    except UnidentifiedImageError:
        messagebox.showerror('error', 'Something something wrong image. I\'ll look into this later.')

    
    lbl_image.config(image = photo)
    

def createPlaylist():
    global image_path

    check_fail1 = 'Please choose player 1!'
    check_fail2 = 'Please choose player 2!'
    check_fail3 = 'Please enter a valid lower bound for the star range!'
    check_fail4 = 'Please enter a valid star range!'
    check_fail5 = 'Please enter a valid star range!'
    check_fail6 = 'Please choose a valid number of entries!'
    
    try:
        p1 = json.load(open(lbl_p1_local_cache['text']))
        check1 = True
                
    except:
        check1 = False

    try:     
        p2 = json.load(open(lbl_p2_local_cache['text']))
        check2 = True
    except:
        check2 = False

    try:
        min_stars = float(ent_min_stars.get())
        check3 = True
    except ValueError:
        min_stars = math.inf
        check3 = False
        
    try:
        max_stars = float(ent_max_stars.get())
        check4 = True
        
    except ValueError:
        check4 = False

    if min_stars >= max_stars:
        check5 = False

    else:
        check5 = True

    if not (re.match(r'[0-9]+',ent_max_number.get()) or select_all.get() == 1):
        check6 = False
    elif re.match(r'[0-9]+',ent_max_number.get()):
        entries = int(ent_max_number.get())
        check6 = True
    elif select_all.get() == 1:
        entries = 'all'
        check6 = True


    if check1 == True and check2 == True and check3 == True \
        and check4 == True and check5 == True and check6 == True \
        and incl_no_score == True and only_no_score == False:

        string_list = []
        maps_string = ''

        pl_name = 'vs. ' + lbl_p2_local_cache['text'].replace('.json', '') \
            + ' [' + str(min_stars) + '-' + str(max_stars) + ']'

        #b64_img = base64.b64encode(image_path.read()).decode('utf-8')

        pl_string = '{"playlistTitle":"' + pl_name + '","playlistAuthor":"bop","playlistDescription":"' + 'bop' + '","image":"data:image/png;base64,' + b64_img + '","songs":['

        p1_set = set()
        for item in p1['scores']:
            p1_set.add(item['lbid'])

        p2_set = set()
        for item in p2['scores']:
            p2_set.add(item['lbid'])


        diff_set = p1_set ^ p2_set

        if entries == 'all':
            for item in p1['scores']:
                if min_stars < item['stars'] <= max_stars:
                    for item2 in p2['scores']:
                        if item2['lbid'] == item['lbid'] and float(item2['pp']) > float(item['pp']):
                            song_string = '{"hash":"' + item['hash'] + '","songName":"' + unidecode(item['song']).replace('\\', '\\\\').replace('\"', '\\"') + '","difficulties": [{"characteristic":"Standard", "name": "' + item['diff'] + '"}]}'
                            string_list.append(song_string)

            for item in p2['scores']:
                if min_stars < item['stars'] <= max_stars:
                    if item['lbid'] in diff_set:
                        song_string = '{"hash":"' + item['hash'] + '","songName":"' + unidecode(item['song']).replace('\\', '\\\\').replace('\"', '\\"') + '","difficulties": [{"characteristic":"Standard", "name": "' + item['diff'] + '"}]}'
                        string_list.append(song_string)

            for s in string_list:
                maps_string = maps_string + s + ','

            maps_string = maps_string[:-1]
            pl_string = pl_string + maps_string + ']}'
            pretty_pl_string = json.dumps(json.loads(pl_string), indent = 2)
            
            entry_nr = str(len(string_list))


        elif isNumber(entries):
            for item in p1['scores']:
                if min_stars < item['stars'] <= max_stars:
                    for item2 in p2['scores']:
                        if item2['lbid'] == item['lbid'] and float(item2['pp']) > float(item['pp']):
                            song_string = '{"hash":"' + item['hash'] + '","songName":"' + unidecode(item['song']).replace('\\', '\\\\').replace('\"', '\\"') + '","difficulties": [{"characteristic":"Standard", "name": "' + item['diff'] + '"}]}'
                            string_list.append(song_string)

            for item in p2['scores']:
                if min_stars < item['stars'] <= max_stars:
                    if item['lbid'] in diff_set:
                        song_string = '{"hash":"' + item['hash'] + '","songName":"' + unidecode(item['song']).replace('\\', '\\\\').replace('\"', '\\"') + '","difficulties": [{"characteristic":"Standard", "name": "' + item['diff'] + '"}]}'
                        string_list.append(song_string)

            if entries > len(string_list):
                entries = len(string_list)

            i = 0
            while i < entries:
                maps_string = maps_string + string_list[i] + ','
                i += 1


            maps_string = maps_string[:-1]
            pl_string = pl_string + maps_string + ']}'
            pretty_pl_string = json.dumps(json.loads(pl_string), indent = 2)

            entry_nr = str(entries)


        with open(pl_name + ' (incl. no scores).bplist', 'w') as playlist:
            playlist.write(pretty_pl_string)
            messagebox.showinfo('Success!', 'Playlist with ' + entry_nr + ' entries saved as \'' + pl_name + '.bplist\'')


    if check1 == True and check2 == True and check3 == True and check4 == True and check5 == True and check6 == True and incl_no_score == False and only_no_score == True:

        string_list = []
        maps_string = ''

        pl_name = 'vs. ' + lbl_p2_local_cache['text'].replace('.json', '') + ' [' + str(min_stars) + '-' + str(max_stars) + ']'

        #b64_img = base64.b64encode(image_path.read()).decode('utf-8')

        pl_string = '{"playlistTitle":"' + pl_name + '","playlistAuthor":"bop","playlistDescription":"' + 'bop' + '","image":"data:image/png;base64,' + b64_img + '","songs":['


        p1_set = set()
        for item in p1['scores']:
            p1_set.add(item['lbid'])

        p2_set = set()
        for item in p2['scores']:
            p2_set.add(item['lbid'])


        diff_set = p1_set ^ p2_set
        

        if entries == 'all':
            for item in p2['scores']:
                if min_stars < item['stars'] <= max_stars:
                    if item['lbid'] in diff_set:
                        song_string = '{"hash":"' + item['hash'] + '","songName":"' + unidecode(item['song']).replace('\\', '\\\\').replace('\"', '\\"') + '","difficulties": [{"characteristic":"Standard", "name": "' + item['diff'] + '"}]}'
                        string_list.append(song_string)



            for s in string_list:
                maps_string = maps_string + s + ','

            maps_string = maps_string[:-1]
            pl_string = pl_string + maps_string + ']}'
            pretty_pl_string = json.dumps(json.loads(pl_string), indent = 2)
            
            entry_nr = str(len(string_list))


        elif isNumber(entries):
            for item in p1['scores']:
                if min_stars < item['stars'] <= max_stars:
                    if item['lbid'] in diff_set:
                        song_string = '{"hash":"' + item['hash'] + '","songName":"' + unidecode(item['song']).replace('\\', '\\\\').replace('\"', '\\"') + '","difficulties": [{"characteristic":"Standard", "name": "' + item['diff'] + '"}]}'
                        string_list.append(song_string)

            i = 0
            while i < entries:
                maps_string = maps_string + string_list[i] + ','
                i += 1


            maps_string = maps_string[:-1]
            pl_string = pl_string + maps_string + ']}'
            pretty_pl_string = json.dumps(json.loads(pl_string), indent = 2)

            entry_nr = str(entries)


        with open(pl_name + ' (no scores).bplist', 'w') as playlist:
            playlist.write(pretty_pl_string)
            messagebox.showinfo('Success!', 'Playlist with ' + entry_nr + ' entries saved as \'' + pl_name + '.bplist\'')


    if check1 == True and check2 == True and check3 == True and check4 == True and check5 == True and check6 == True and incl_no_score == False and only_no_score == False:

        string_list = []
        maps_string = ''

        pl_name = 'vs. ' + lbl_p2_local_cache['text'].replace('.json', '') + ' [' + str(min_stars) + '-' + str(max_stars) + ']'

        #b64_img = base64.b64encode(image_path.read()).decode('utf-8')

        pl_string = '{"playlistTitle":"' + pl_name + '","playlistAuthor":"bop","playlistDescription":"' + 'bop' + '","image":"data:image/png;base64,' + b64_img + '","songs":['

        if entries == 'all':
            for item in p1['scores']:
                if min_stars < item['stars'] <= max_stars:
                    for item2 in p2['scores']:
                        if item2['lbid'] == item['lbid'] and float(item2['pp']) > float(item['pp']):
                            song_string = '{"hash":"' + item['hash'] + '","songName":"' + unidecode(item['song']).replace('\\', '\\\\').replace('\"', '\\"') + '","difficulties": [{"characteristic":"Standard", "name": "' + item['diff'] + '"}]}'
                            string_list.append(song_string)

            for s in string_list:
                maps_string = maps_string + s + ','

            maps_string = maps_string[:-1]
            pl_string = pl_string + maps_string + ']}'
            pretty_pl_string = json.dumps(json.loads(pl_string), indent = 2)
            
            entry_nr = str(len(string_list))


        elif isNumber(entries):
            for item in p1['scores']:
                if min_stars < item['stars'] <= max_stars:
                    for item2 in p2['scores']:
                        if item2['lbid'] == item['lbid'] and float(item2['pp']) > float(item['pp']):
                            song_string = '{"hash":"' + item['hash'] + '","songName":"' + unidecode(item['song']).replace('\\', '\\\\').replace('\"', '\\"') + '","difficulties": [{"characteristic":"Standard", "name": "' + item['diff'] + '"}]}'
                            string_list.append(song_string)

            i = 0
            while i < entries:
                maps_string = maps_string + string_list[i] + ','
                i += 1


            maps_string = maps_string[:-1]
            pl_string = pl_string + maps_string + ']}'
            pretty_pl_string = json.dumps(json.loads(pl_string), indent = 2)

            entry_nr = str(entries)


        with open(pl_name + '.bplist', 'w') as playlist:
            playlist.write(pretty_pl_string)
            messagebox.showinfo('Success!', 'Playlist with ' + entry_nr + ' entries saved as \'' + pl_name + '.bplist\'')

            
    elif check1 == False:
        messagebox.showerror('error', check_fail1)
        

    elif check2 == False:
        messagebox.showerror('error', check_fail2)
        

    elif check3 == False:
        messagebox.showerror('error', check_fail3)
        

    elif check4 == False:
        messagebox.showerror('error', check_fail4)
        

    elif check5 == False:
        messagebox.showerror('error', check_fail5)
        

    elif check6 == False:
        messagebox.showerror('error', check_fail6)
        

root = tk.Tk()
root.title('bop')
root.resizable(width = False, height = False)
style =ttk.Style(root)
root.tk.call('source','azure/azure.tcl')
root.tk.call('set_theme', 'dark')

frm_players = ttk.Frame(
    root
)

frm_files = ttk.Frame(
    root
)

p1_entry_frm = ttk.Frame(
    frm_players,
    )

lbl_player1 = ttk.Label(
    p1_entry_frm,
    width = 12,
    font = ('Consolas', 10),
    text = 'SSID Player 1'
    )

ent_player1 = ttk.Entry(
    p1_entry_frm,
    width = 10,
    font = ('Consolas', 10)
    )

s = ttk.Style()
s.configure('my.Accent.TButton', font = ('Consolas', 10))

t = ttk.Style()
t.configure('my.TCheckbutton', font = ('Consolas', 10))

btn_player1 = ttk.Button(
    p1_entry_frm,
    width = 4,
    text = 'OK',
    style = 'my.Accent.TButton',
    command = getPlayer1
    )


fav_list1 = []
for file in glob.glob('*.json'):
    fav_list1.append(file.replace('.json',''))

def clear_selection(e):
    setPlayer1()
    drpdwn_p1_choice.selection_clear()

drpdwn_p1_choice = ttk.Combobox(
    p1_entry_frm,
    values = fav_list1,
    state = 'readonly',
    width = 10,
    font = ('Consolas', 10),
    )

drpdwn_p1_choice.set('Player 1')
drpdwn_p1_choice.bind("<<ComboboxSelected>>",clear_selection)

lbl_player1.grid(row = 0, column = 0, padx = '2', pady = '2', sticky = 'w')
ent_player1.grid(row = 0, column = 1, padx = '2', pady = '2', sticky = 'w')
btn_player1.grid(row = 0, column = 2, padx = '2', pady = '2', sticky = 'w')
drpdwn_p1_choice.grid(row = 1, column = 1, padx = '2', pady = '0')


p1_file_entry_frm = ttk.Frame(
    frm_files
    )

lbl_p1_local_cache = ttk.Label(
    p1_file_entry_frm,
    width = 14,
    font = ('Consolas', 10),
    text = ' - '
    )
lbl_p1_local_cache.config(anchor = 'center')

btn_get_p1_local_file = ttk.Button(
    p1_file_entry_frm,
    width = 13,
    text = 'Local File',
    style = 'my.Accent.TButton',
    command = getPlayer1File
    )

lbl_p1_last_update = ttk.Label(
    p1_file_entry_frm,
    width = 14,
    font = ('Consolas', 10),
    text = ' - '
    )

lbl_p1_last_update.config(anchor = 'center')

btn_get_p1_scores = ttk.Button(
    p1_file_entry_frm,
    state = 'disabled',
    width = 13,
    text = 'Update Scores',
    style = 'my.Accent.TButton',
    command = getP1Scores
    )

lbl_p1_local_cache.grid(row = 0, column = 0, padx = '2', pady = '2', sticky = 'w')
btn_get_p1_local_file.grid(row = 0, column = 1, padx = '2', pady = '2', sticky = 'w')
lbl_p1_last_update.grid(row = 1, column = 0, padx = '2', pady = '2', sticky = 'w')
btn_get_p1_scores.grid(row = 1, column = 1, padx = '2', pady = '2')

p2_entry_frm = ttk.Frame(
    frm_players
    )


lbl_player2 = ttk.Label(
    p2_entry_frm,
    width = 12,
    font = ('Consolas', 10),
    text = 'SSID Player 2'
    )

ent_player2 = ttk.Entry(
    p2_entry_frm,
    width = 10,
    font = ('Consolas', 10)
    )

btn_player2 = ttk.Button(
    p2_entry_frm,
    width = 4,
    text = 'OK',
    style = 'my.Accent.TButton',
    command = getPlayer2
    )

fav_list2 = []
for file in glob.glob('*.json'):
    fav_list2.append(file.replace('.json',''))

def clear_selection2(e):
    setPlayer2()
    drpdwn_p2_choice.selection_clear()


drpdwn_p2_choice = ttk.Combobox(
    p2_entry_frm,
    values = fav_list2,
    state = 'readonly',
    width = 10,
    font = ('Consolas', 10))

drpdwn_p2_choice.set('Player 2')
drpdwn_p2_choice.bind("<<ComboboxSelected>>",clear_selection2)


lbl_player2.grid(row = 0, column = 0, padx = '2', pady = '2', sticky = 'w')
ent_player2.grid(row = 0, column = 1, padx = '2', pady = '2', sticky = 'w')
btn_player2.grid(row = 0, column = 2, padx = '2', pady = '2', sticky = 'w')
drpdwn_p2_choice.grid(row = 1, column = 1, padx = '2', pady = '2')

p2_file_entry_frm = ttk.Frame(
    frm_files
    )

lbl_p2_local_cache = ttk.Label(
    p2_file_entry_frm,
    width = 14,
    font = ('Consolas', 10),
    text = ' - '
    )

lbl_p2_local_cache.config(anchor = 'center')


btn_get_p2_local_file = ttk.Button(
    p2_file_entry_frm,
    width = 13,
    text = 'Local File',
    style = 'my.Accent.TButton',
    command = getPlayer2File
    )

lbl_p2_last_update = ttk.Label(
    p2_file_entry_frm,
    width = 14,
    font = ('Consolas', 10),
    text = ' - '
    )

lbl_p2_last_update.config(anchor = 'center')

btn_get_p2_scores = ttk.Button(
    p2_file_entry_frm,
    state = 'disabled',
    width = 13,
    text = 'Update Scores',
    style = 'my.Accent.TButton',
    command = getP2Scores
    )

lbl_p2_local_cache.grid(row = 0, column = 0, padx = '2', pady = '2', sticky = 'w')
btn_get_p2_local_file.grid(row = 0, column = 1, padx = '2', pady = '2', sticky = 'w')
lbl_p2_last_update.grid(row = 1, column = 0, padx = '2', pady = '2', sticky = 'w')
btn_get_p2_scores.grid(row = 1, column = 1, padx = '2', pady = '2')

frm_logo = ttk.Frame(
    root
    )

logo = Image.open('pics/bop.png', mode = 'r')
#img2 = img.resize((75,75),Image.Resampling.LANCZOS)
bop = ImageTk.PhotoImage(logo)

lbl_logo = ttk.Label(
    frm_logo,
    image = bop
    )

lbl_logo.grid(row = 0, column = 0, sticky = 'nswe')

frm_stars = ttk.Frame(
    root
    )

ent_star_range = ttk.Frame(
    frm_stars
    )

lbl_star_range = ttk.Label(
    ent_star_range,
    font = ('Consolas', 10),
    width = 12,
    text = 'star range'
    )

ent_min_stars = ttk.Entry(
    ent_star_range,
    font = ('Consolas', 10),
    width = 3
    )

lbl_star_range_separator = ttk.Label(
    ent_star_range,
    font = ('Consolas', 10),
    text = '-'
    )

ent_max_stars = ttk.Entry(
    ent_star_range,
    font = ('Consolas', 10),
    width = 3
    )


lbl_star_range.grid(row = 0, column = 0, padx = '2', pady = '2', sticky = 'w')
ent_min_stars.grid(row = 0, column = 1, padx = '1', pady = '2')
lbl_star_range_separator.grid(row = 0, column = 2, padx = '1', pady = '2')
ent_max_stars.grid(row = 0, column = 3, padx = '1', pady = '2')


frm_ent_max_number = ttk.Frame(
    frm_stars
    )

lbl_entry_max_number = ttk.Label(
    frm_ent_max_number,
    width = 12,
    font = ('Consolas', 10),
    text = '#entries'
    )

ent_max_number = ttk.Entry(
    frm_ent_max_number,
    width = 3,
    font = ('Consolas', 10)
    )

select_all = tk.IntVar()

cb_select_all = ttk.Checkbutton(
    frm_ent_max_number,
    text = 'all',
    style = 'my.TCheckbutton',
    variable = select_all,
    command = disableEntry
    )


lbl_entry_max_number.grid(row = 0, column = 0, padx = '2', pady = '2')
ent_max_number.grid(row = 0, column = 1, padx = '2', pady = '2')
cb_select_all.grid(row = 0, column = 2, padx = '8', pady = '2')


ent_star_range.grid(row = 0, column = 0, padx = '2', pady = '2', sticky = 'nw')
frm_ent_max_number.grid(row = 1, column = 0, padx = '2', pady = '2', sticky = 'nw')


frm_no_score = ttk.Frame(
    root
)

var_include_no_score = tk.IntVar()

cb_include_no_score = ttk.Checkbutton(
    frm_no_score,
    text = 'incl. no score',
    style = 'my.TCheckbutton',
    variable = var_include_no_score,
    command = setInclNoScore
    )

var_no_score_only = tk.IntVar()

cb_no_score_only = ttk.Checkbutton(
    frm_no_score,
    text = 'only no score',
    style = 'my.TCheckbutton',
    variable = var_no_score_only,
    command = setOnlyNoScore
    )


cb_include_no_score.grid(row = 0, column = 0, padx = '1', pady = '2', sticky = 'nw')
cb_no_score_only.grid(row = 1, column = 0, padx = '1', pady = '2', sticky = 'nw')


frm_image_buttons = ttk.Frame(
    root
    )

img = Image.open('pics/pikachu.png', mode = 'r')
image_path = open('pics/pikachu.png', 'rb')
b64_img = base64.b64encode(image_path.read()).decode('utf-8')
img2 = img.resize((75,75),Image.Resampling.LANCZOS)
photo = ImageTk.PhotoImage(img2)

lbl_image = ttk.Label(
    frm_image_buttons,
    image = photo
    )

frm_buttons = ttk.Frame(
    frm_image_buttons
    )

btn_image = ttk.Button(
    frm_buttons,
    width = 13,
    text = 'Choose image',
    style = 'my.Accent.TButton',
    command = getImage
    )

btn_create_playlist = ttk.Button(
    frm_buttons,
    width = 13,
    text = 'Make Playlist',
    style = 'my.Accent.TButton',
    command = createPlaylist
    )



p1_entry_frm.grid(row = 0, column = 0, padx = '10', pady = '10', sticky = 'nw')
p2_entry_frm.grid(row = 1, column = 0, padx = '10', pady = '10', sticky = 'nw')

p1_file_entry_frm.grid(row = 0, column = 0, padx = '10', pady = '10', sticky = 'ne')
p2_file_entry_frm.grid(row = 1, column = 0, padx = '10', pady = '10', sticky = 'ne')



btn_image.grid(row = 0, column = 0, padx = '2', pady = '2', sticky = 'ne')
btn_create_playlist.grid(row = 1, column = 0, padx = '2', pady = '2', sticky = 'ne')

lbl_image.grid(row = 0, column = 0, padx = '10', pady = '0', sticky = 'nse')
frm_buttons.grid(row = 0, column = 1, padx = '0', pady = '0', sticky = 'ne')



frm_players.grid(row = 0, column = 0)
frm_logo.grid(row = 0, column = 1)
frm_files.grid(row = 0, column = 2)
frm_stars.grid(row = 2, column = 0, padx = '10', pady = '10', sticky = 'nw')
frm_no_score.grid(row = 2, column = 1, padx = '10', pady = '10', sticky = 'nw')
frm_image_buttons.grid(row = 2, column = 2, padx = '10', pady = '10', sticky = 'ne')

root.mainloop()
