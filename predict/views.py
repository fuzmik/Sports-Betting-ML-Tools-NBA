from __future__ import absolute_import, division, print_function, unicode_literals
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from .models import Game
####vc vode testing123
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http.response import HttpResponsePermanentRedirect


from django.views.generic import ListView
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from users.models import Profile
from tensorflow.keras import *
from datetime import datetime
from pytz import timezone
from django.template import loader
import requests, json, time, operator, pickle, random
import functools
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.callbacks import TensorBoard, EarlyStopping, ModelCheckpoint
from sklearn.model_selection import train_test_split
import random
#asdfasdf
playersPerTeam = 9
TEAMCOLORS = {
    'ATL':'#E03A3E',
    'BKN':'#000000',
    'BOS':'#158248',
    'CHA':'#1B6D87',
    'CHI':'#CE1341',
    'CLE':'#FAB81C',
    'DAL':'#287DC5',
    'DEN':'#FBC627',
    'DET':'#DD1631',
    'GSW':'#236BB6',
    'HOU':'#CE1341',
    'IND':'#FABB30',
    'LAC':'#2F7ABC',
    'LAL':'#552583',
    'MEM':'#6189B9',
    'MIA':'#980B2E',
    'MIL':'#06471A',
    'MIN':'#236192',
    'NOP':'#E31837',
    'NYK':'#236BB6',
    'OKC':'#F05134',
    'ORL':'#2677BD',
    'PHI':'#236BB5',
    'PHX':'#F9A01B',
    'POR':'#C6122A',
    'SAC':'#5A2D81',
    'SAS':'#1c1c1c',
    'TOR':'#CD1341',
    'UTA':'#FAA403',
    'WAS':'#CF142C',
}

def saveEdit(request,pk,change,**kwargs):

    changes = change[7:].split('-')
    changes.pop(-1)
    print(changes)
    context = {}
    user = request.user
    g = Game.objects.filter(pk=pk)
    csvid = g.values('csvid')[0]['csvid']
    path = 'csv/'+str(user.username)+str(csvid)+'.csv'
    csv = open(path,'r')
    first=True
    data = ''
    header = ''

    for line in csv.readlines():
        print(line)
        if first:
            header = line
            first = False
        else:
            data = line
            break

    data = data.split(',')
    header= header.split(',')
    print(path,data,'-------')
    gameid = data.pop(0)
    header.pop(0)
    homeid = data.pop(0)
    header.pop(0)
    visitorid = data.pop(0)
    header.pop(0)

    labels = ['ast','blk','dreb','fg3_pct','fg3a','fg3m','fga','fgm','fta','ftm','oreb','pf','pts','reb','stl', 'turnover', 'min']

    for c in changes:
        x = c.split(':')
        n=17*int(x[0])-17+int(x[1])
        data[n-2]=x[2]
        print(n)
        print(data[n-2])
    print(data,'fffffffffffff')


    writeCSVHeader(labels, path)
    def w(data, path, g):
        ss = str(g.values('gameid')[0]['gameid'])+','+homeid+','+visitorid
        for st in data:
            ss+=','+st
        print('$$$$$$$$$',ss)
        printp=(path)
        f = open(path,'a')
        f.write(ss+'\n')
    w(data, path,g)
    LABEL_COLUMN = 'winner'
    LABELS = [0, 1]
    l = labels
    p = predict(path)
    print(p)

    #p = float(p[0])
    g.update(home_score_prediction=round(p[0]))
    g.update(visitor_score_prediction=round(p[1]))
    g.update(pmscore=(round(p[0])-round(p[1])))
    
    return redirect('home-predict')



##
def editGame(request,pk,**kwargs):
    context = {}
    user = request.user
    g = Game.objects.filter(pk=pk)
    csvid = g.values('csvid')[0]['csvid']
    gID = g.values('gameid')[0]['gameid']
    print('gID:', gID)

    if gID is None:
        return redirect('home-predict')
    def get_labels():
        lol= []
        ll = ['ast','blk','dreb','fg3_pct','fg3a','fg3m','fga','fgm','fta','ftm','oreb','pf','pts','reb','stl', 'turnover', 'min']
        for l in ll:
            lol.append(l.upper())
        return lol
    context['labels']= get_labels()
    context['asdf']= 'oof'

    path = 'csv/'+str(user.username)+str(csvid)+'.csv'
    csv = open(path,'r+')
    header = ''
    data= ''
    first = True
    for line in csv.readlines():
        if first:
            header = line
            first = False
        else:
            data = line
            break
    data = data.split(',')
    header= header.split(',')
    #print(data,'ooooof')
    data.pop(0)
    header.pop(0)
    data.pop(0)
    header.pop(0)
    data.pop(0)
    header.pop(0)
    players = {}
    oofnog = []
    for i in range(0,18):
        #print(g.values('p'+str(i))[0]['p'+str(i)])
        oofnog.append(g.values('p'+str(i))[0]['p'+str(i)])
    url = 'https://www.balldontlie.io/api/v1/players/'
    resp = []
    #print(oofnog)
    for id in oofnog:
        obj = load_obj('2019PlayerNamesByID')
        #print(resp)
        found = False
        for x in obj:



            if int(x) == int(id):
                found = True
                print('found-------')
                resp.append(obj[x])

        if not found:
            r = req(url+str(id))
            fn = r['first_name']
            ln = r['last_name']
            full = fn+' '+ln
            resp.append(full)
            obj.update({str(id) : full})
            save_obj(obj,'2019PlayerNamesByID')

    c = 0
    for oof in range(1,19):
        n=17*oof-17
        temp = [str(oof)]
        for f in range(n,n+17):
            temp.append(data[f])

        players.update({ resp[c] : temp })
        c+=1

    context['pk'] = pk
    context['stats']= players
    context['home']=g.values('home')[0]['home']
    context['homecolor']=g.values('homecolor')[0]['homecolor']
    context['visitorcolor']=g.values('visitorcolor')[0]['visitorcolor']
    context['visitor']=g.values('visitor')[0]['visitor']
    context['gamedate']=g.values('gamedate')[0]['gamedate']
    context['home_score']=g.values('home_score')[0]['home_score']
    context['visitor_score']=g.values('visitor_score')[0]['visitor_score']
    context['home_spread']=g.values('home_spread')[0]['home_spread']
    context['visitor_spread']=g.values('visitor_spread')[0]['visitor_spread']
    context['prediction']=g.values('prediction')[0]['prediction']
    context['finished']=g.values('finished')[0]['finished']
    context['winner'] = g.values('winner')[0]['winner']
    context['pmscore'] = g.values('pmscore')[0]['pmscore']
    context['pvscore'] = g.values('visitor_score_prediction')[0]['visitor_score_prediction']
    context['phscore'] = g.values('home_score_prediction')[0]['home_score_prediction']
    context['game'] = g
    context['g'] = g
    #print(players)

    return render(request, 'predict/edit.html',context)
def predictToday(request,**kwargs):
    #print(request)




    print('predictToday------------------############-------------')
    return redirect('home-predict')

def getScore(request,pk,**kwargs):
    url = 'https://www.balldontlie.io/api/v1/games/'
    user= request.user
    g = Game.objects.filter(pk=pk).values('gameid')
    g = g[0]
    url += g['gameid']
    r = req(url)
    h = r['home_team_score']
    print('url====',url)

    v= r['visitor_team_score']
    print(request.user,'-----------------')
    p = Profile.objects.filter(user=request.user)
    po = Profile.objects.get(user=request.user)
    print(p.values('gain')[0]['gain'])
    if r['status'] == "Final":
        prediction = Game.objects.filter(pk=pk).values('prediction')[0]['prediction']
        pmscore = Game.objects.filter(pk=pk).values('pmscore')[0]['pmscore']
        finished = Game.objects.filter(pk=pk).values('finished')[0]['finished']

        if not finished: # add not back
            if pmscore >= 0 and h >v:#win p home
                asdf = float(p.values('gain')[0]['gain']) + float(prediction) - float(.5)
                p.update(gain=asdf)
                p.update(correct=p.values('correct')[0]['correct']+1)
                Game.objects.filter(pk=pk).update(winner=1)
            if pmscore < 0 and h < v:#win p visitor
                asdf = float(p.values('gain')[0]['gain']) + float(.5) -float(prediction)
                p.update(gain=asdf)
                p.update(correct=p.values('correct')[0]['correct']+1)
                Game.objects.filter(pk=pk).update(winner=0)
            if pmscore < 0 and h > v:#loose p vis
                asdf = float(p.values('loss')[0]['loss']) + float(.5) - float(prediction)
                p.update(loss=asdf)
                Game.objects.filter(pk=pk).update(winner=1)
            if pmscore >= 0 and h < v:#loose p home
                print('asdf')
                asdf = float(p.values('loss')[0]['loss']) + float(prediction) - float(.5)
                p.update(loss=asdf)
                Game.objects.filter(pk=pk).update(winner=0)
            print(Game.objects.filter(pk=pk).values('winner')[0]['winner'])
            p.update(predictions=p.values('predictions')[0]['predictions']+1)




        Game.objects.filter(pk=pk).update(finished=True)

    Game.objects.filter(pk=pk).update(home_score=h)
    Game.objects.filter(pk=pk).update(visitor_score=v)
    #print(pagenum)
    #x = redirect("home-predict")
    #return HttpResponsePermanentRedirect("https://nbadata.cloud/predict/?page="+str(pagenum))
    return redirect('home-predict')

def todaysGames(self):
    url = 'https://www.balldontlie.io/api/v1/games?dates[]='
    eastern = timezone('America/Los_Angeles')
    fmt = '%Y-%m-%d'
    loc_dt = datetime.now(eastern)
    #naive_dt = datetime.now()
    url+=loc_dt.strftime(fmt)
    print(url)
    r = req(url)
    games = []
    for game in range(len(r['data'])):
        habv = r['data'][game]['home_team']['abbreviation']
        hfn = r['data'][game]['home_team']['full_name']
        hscore = str(r['data'][game]['home_team_score'])
        vabv = r['data'][game]['visitor_team']['abbreviation']
        vfn = r['data'][game]['visitor_team']['full_name']
        vscore = str(r['data'][game]['visitor_team_score'])
        status = r['data'][game]['status']

        foo = {'habv':habv,'hfn':hfn,'hscore':hscore,'vabv':vabv,'vfn':vfn,'vscore':vscore,'status':status,'date':loc_dt.strftime(fmt)}
        games.append(foo)
    if len(games)==0:
        games.append('No Games Today')
    return games





class GameListView(ListView, LoginRequiredMixin):
    model = Game
    template_name = 'predict/home.html'
    ordering = ['-date_posted']
    paginate_by = 4
    context_object_name = 'games'
    context = 'games'

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(GameListView, self).get_context_data(**kwargs)
        x = todaysGames(self)
        context['today'] = x
        context['tc'] = TEAMCOLORS
        context['correct'] = Profile.objects.filter(user=user).values('correct')[0]['correct']
        context['numpred'] =  Profile.objects.filter(user=user).values('predictions')[0]['predictions']
        if Profile.objects.filter(user=user).values('predictions')[0]['predictions'] >= 1:
            context['pc'] = round(Profile.objects.filter(user=user).values('correct')[0]['correct']/Profile.objects.filter(user=user).values('predictions')[0]['predictions']*100,1)
        else:

            context['pc'] = '0'
        context['gain'] =  Profile.objects.filter(user=user).values('gain')[0]['gain']
        context['loss'] =  Profile.objects.filter(user=user).values('loss')[0]['loss']
        context['lg'] = Profile.objects.filter(user=user).values('gain')[0]['gain'] - Profile.objects.filter(user=user).values('loss')[0]['loss']
        #context['form'] = GameForm()
        context['ordering']= ['-date_posted']
        return context
    def get_queryset(self, **kwargs):
        user = self.request.user
        return Game.objects.filter(author=user).order_by('-date_posted')

    def form_valid(self, form):
        print('-------------------')
        form.instance.author = self.request.user
        season = '2022'

        path = 'csv/'+str(form.instance.pk)+'.csv'
        labels = ['ast','blk','dreb','fg3_pct','fg3a','fg3m','fga','fgm','fta','ftm','oreb','pf','pts','reb','stl', 'turnover', 'min']
        x = form.instance.gamedate
        y = form.instance.home.upper()
        z = form.instance.visitor.upper()
        date=x
        homeAbv=y
        visitorAbv=z
        found, gameid = futureGame(date, homeAbv,visitorAbv,path,season,labels)
        if found:
            form.instance.gameid = gameid
        else:
            form.instance.gameid = 'error'
        return super().form_valid(form)





def quickcreate(request,home,visitor,date):
    print('testing quick create---------------------')
    csvid = random.randint(1,100000)
    season = '2022'
    labels = ['ast','blk','dreb','fg3_pct','fg3a','fg3m','fga','fgm','fta','ftm','oreb','pf','pts','reb','stl', 'turnover', 'min']
    path = 'csv/'+str(request.user)+str(csvid)+'.csv'
    
    found, gameid, playerids = futureGame(date,home,visitor,path,season,labels)

    obj = Game.objects.create(author=request.user,home=home,visitor=visitor,gamedate=date,homecolor=TEAMCOLORS[home],visitorcolor=TEAMCOLORS[visitor],csvid=csvid,
        p0 = playerids[0], p1 = playerids[1], p2 = playerids[2], p3 = playerids[3], p4 = playerids[4], p5 = playerids[5],
        p6 = playerids[6], p7 = playerids[7], p8 = playerids[8], p9 = playerids[9], p10 = playerids[10], p11 = playerids[11],
        p12 = playerids[12], p13 = playerids[13], p14 = playerids[14], p15 = playerids[15], p16 = playerids[16], p17 = playerids[17]
        
        ,gameid=gameid)

    return redirect('edit-predict',obj.pk)
    #return redirect('home-predict')


class GameCreateView(LoginRequiredMixin, CreateView):
    model = Game
    template_name = 'predict/new.html'
    csvid = random.randint(1,10000000)
    fields = ['home', 'visitor','gamedate']
    
    def form_valid(self, form, **kwargs):
        csvid = random.randint(1,100000)
        form.instance.author = self.request.user
        season = '2022'
        form.instance.csvid = csvid#############fix here
        print(str(csvid),"csvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
        path = 'csv/'+str(self.request.user)+str(csvid)+'.csv'
        print(path)
        labels = ['ast','blk','dreb','fg3_pct','fg3a','fg3m','fga','fgm','fta','ftm','oreb','pf','pts','reb','stl', 'turnover', 'min']
        x = form.instance.gamedate
        y = form.instance.home.upper()
        z = form.instance.visitor.upper()
        date=x
        homeAbv=y
        visitorAbv=z
        form.instance.homecolor = TEAMCOLORS[y]
        form.instance.visitorcolor = TEAMCOLORS[z]


        found, gameid, playerids = futureGame(date, homeAbv,visitorAbv,path,season,labels)
        if found:

            form.instance.p0 = playerids[0]
            form.instance.p1 = playerids[1]
            form.instance.p2 = playerids[2]
            form.instance.p3 = playerids[3]
            form.instance.p4 = playerids[4]
            form.instance.p5 = playerids[5]
            form.instance.p6 = playerids[6]
            form.instance.p7 = playerids[7]
            form.instance.p8 = playerids[8]
            form.instance.p9 = playerids[9]
            form.instance.p10 = playerids[10]
            form.instance.p11 = playerids[11]
            form.instance.p12 = playerids[12]
            form.instance.p14 = playerids[14]
            form.instance.p15 = playerids[15]
            form.instance.p16 = playerids[16]
            form.instance.p17 = playerids[17]
            form.instance.p18 = playerids[18]
            LABEL_COLUMN = 'winner'
            LABELS = [0, 1]
            l = labels
            #p = predict(l, LABELS,LABEL_COLUMN,path)
            #form.instance.prediction = float(p[0])
            form.instance.gameid = gameid

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(GameCreateView, self).get_context_data(**kwargs)
        x = todaysGames(self)
        context['today'] = x
        #context['csvid'] = self.csvid
        #print(self.csvid,'---------------------------')
        return context


def futureGame(date,homeAbv,visitorAbv,path, season,labels):
    print(season)
    url = 'https://www.balldontlie.io/api/v1/games?dates[]='
    url+=date
    response = req(url)
    nOsTAtsYET = {}
    found = False
    gameid = 0
    playerids = []
    for game in range(len(response['data'])):
        ha = response['data'][game]['home_team']['abbreviation']
        va = response['data'][game]['visitor_team']['abbreviation']
            
        if ha==homeAbv and va==visitorAbv:
            print('found--------123-------')
            found = True
            gameid = response['data'][game]['id']
            data = nextGame(gameid)
            
            homeTeamID = str(response['data'][game]['home_team']['id'])
            visitorTeamID = str(response['data'][game]['visitor_team']['id'])
            
            data.update({'home_team_id':response['data'][game]['home_team']['id']})
            data.update({'visitor_team_id':response['data'][game]['visitor_team']['id']})
            data.update({'home_team_score' : response['data'][game]['home_team_score']})
            data.update({'visitor_team_score' : response['data'][game]['home_team_score']})
            
            playerIdByTeamID = load_obj('2022PlayerIdByTeamID')
            seasonAverages = load_obj('2022SeasonAverages')
 


            homePlayers = []
            for player in playerIdByTeamID[homeTeamID]:
                homePlayers.append(player)
            visitorPlayers = []
            for player in playerIdByTeamID[visitorTeamID]:
                visitorPlayers.append(player)
            print(homePlayers,visitorPlayers)



            homeTeam = []
            visitorTeam = []

            for id in homePlayers:
                homeTeam.append(seasonAverages[id])
            for id in visitorPlayers:
                visitorTeam.append(seasonAverages[id])



            bestH = []
            bestHomeIds =[]
            for i in range(0,playersPerTeam):
                b = getBestPlayer(homeTeam)
                min = homeTeam[int(b)][-1]
                min = min.split(':')[0]
                homeTeam[b][-1] = min
                bestH.append(homeTeam[b])
                bestHomeIds.append(homePlayers[b])
                homePlayers.pop(b)
                homeTeam.pop(b)

            bestV = []
            bestVisitorIds = []
            for i in range(0,playersPerTeam):
                b = getBestPlayer(visitorTeam)
                min = visitorTeam[int(b)][-1]
                min = min.split(':')[0]
                visitorTeam[b][-1] = min
                bestV.append(visitorTeam[b])
                bestVisitorIds.append(visitorPlayers[b])
                visitorTeam.pop(b)
                visitorPlayers.pop(b)


            print('visitor team:',len(bestV),bestVisitorIds) 
            print('home team:',len(bestH),bestHomeIds) 
            writeCSVHeader(labels, path)
            writeCSV(gameid,homeTeamID,visitorTeamID,bestH,bestV,path)

            #print('playerid by team-------------',playerIdByTeamID)

            #
            #playerids=writeCSV(data, path, labels)
            playerids = bestHomeIds+bestVisitorIds
    return found, gameid,playerids
#------------------------------------------------------------------------#

def writeCSV(game,homeId,visitorId,bestH,bestV,path):
    line = str(game)+','+str(homeId)+','+str(visitorId)
    for player in range(len(bestH)):
        for stat in range(len(bestH[player])):
            line += ','+str(bestH[player][stat])
    for player in range(len(bestV)):
        for stat in range(len(bestV[player])):
            line += ','+str(bestV[player][stat])


    
    csv = open(path,'a')
    csv.write(line+'\n')
    print(line)

def writeCSVHeader(labels, path,**kwargs):
    header = 'gameid,home_id,visitor_id'
    derp = ['home_', 'visitor_']
    for foo in derp:
        for i in range(0,playersPerTeam):
            for label in labels:
                header+=','+foo+str(i)+'_'+label
    csv = open(path,'w')
    csv.write(header+'\n')
    return header

#------------------------------------------------------------------------#
def getBestPlayer(team):
    best = ''
    topMin = 0
    for player in range(len(team)):

        if len(team[player]) == 0:
            continue
        min = team[player][-1]
        min = min.split(':')[0]
        #print(min,topMin)
        if int(min) > int(topMin):
            best = player
            topMin = min
    return best

#gets season average stats by player ids.....
def getPlayerAvg(data,season,**kwargs):
    url = 'https://www.balldontlie.io/api/v1/season_averages?season='
    url += season +'&player_ids[]='
    teams = ['home', 'visitor']
    playerStats = load_obj(season+'playerStats')
    print('loaded # player stats: ', len(playerStats))
    for team in teams:
        badPlayer = False
        badPlayerid = 0#gosh i hope there is only ever 1 of these on each team else smh nooo
        for playerid in data[team+'_team_players']:
            foundSaved = False
            #check if player has been saved
            for splayerid in playerStats:
                if playerid == splayerid:
                        data[team+'_team_players'].update({playerid : {}})#here it is again#soo anoying
                        for statName in playerStats[playerid]:
                            data[team+'_team_players'][playerid].update({statName :playerStats[playerid][statName]})
                        print('found saved -----------####-------------id: ', playerid)
                        foundSaved = True
                        break
            #get unsaved season averages
            if not foundSaved:
                uurl = url+str(playerid)
                response = req(uurl)
                data[team+'_team_players'].update({playerid : {}})
                print(len(response['data']))
                if len(response['data']) != 0:#
                    for statName in response['data'][0]:
                        data[team+'_team_players'][playerid].update({ statName: response['data'][0][statName]})
                    playerStats.update({playerid : {}})
                    for statName in data[team+'_team_players'][playerid]:
                        playerStats[playerid].update({statName : data[team+'_team_players'][playerid][statName]})
                    print('not saved -----------####-------------id: ', playerid)
                else:
                    badPlayer = True
                    badPlayerid = playerid
        if badPlayer:
            print('badplayer#--------', badPlayerid)
            data[team+'_team_players'].pop(badPlayerid, None)
            badPlayer=False

    save_obj(playerStats, season+'playerStats')
    return data

#------------------------------------------------------------------------#


#clears data of last game and gets ready for next
def nextGame(gameid):
    data = {}
    data.update({'gameid' : gameid})
    data.update({'home_team_players' : {}})
    data.update({'visitor_team_players' : {}})
    data.update({'home_good_players' : {}})
    data.update({'visitor_good_players' : {}})
    #data.update({'home_team_id' : 0})
    #data.update({'visitor_team_id' : 0})
    return data



#------------------------------------------------------------------------#
def req(url):
    proxy = load_obj('proxy')
    dict = {}
    p = random.randint(0,len(proxy)-1)
    dict.update({'http' : proxy[p]})
    r = requests.get(url)
    print('proxy: ', proxy[p], 'url: ', url, 'response: ', r)
    if str(r) != '<Response [200]>':#means we request too fast..fast af boi so like anything under 1 r/sec cause error at 60 seconds in....
        time.sleep(5)
        req(url)
    #time.sleep(.1)
    return r.json()
#------------------------------------------------------------------------#
def save_obj(obj, name):
    with open('updatedObj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open('updatedObj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)
#------------------------------------------------------------------------#TensorFlow Time lets get it####################

def predict(path):

    data = pd.read_csv(path)

    data.drop(['gameid'], axis=1, inplace=True)


    data = data.values
    data = data.astype(float)


    #x_train = tf.keras.utils.normalize(x_train, axis=1)
    #x_test = tf.keras.utils.normalize(x_test, axis=1)

    model = tf.keras.Sequential([

        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(64, activation='relu'),
        
        tf.keras.layers.Dense(2, activation='linear'),



    ])
    model.load_weights('./checkpoints/my_checkpoint')

    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])

    p = model.predict(data)
    return(p[0])





#------------------------------------------------------------------------#
def sortByPlayTime(data):
    derp = ['home', 'visitor']
    for foo in derp:
        for i in range(3):
            maxMin = 0
            id = ''
            for player in data[foo+'_team_players']:
                old = maxMin
                if 'min' in data[foo+'_team_players'][player]:
                    maxMin = max(maxMin, int(data[foo+'_team_players'][player]['min']))
                    if maxMin > old:#this line messed me up i had >= and could figure out why it wasnt working finally got it.
                        id = player
            try:
                data[foo+'_good_players'].update({id : data[foo+'_team_players'][id]})
                data[foo+'_team_players'].pop(int(id), None)
            except KeyError:
                print('key error')
    return data
#------------------------------------------------------------------------#
def minuteConversion(data):
    #chop seconds off...
    print(data)
    derp = ['home', 'visitor']
    for foo in derp:#iter home visitor
        for player in data[foo+'_team_players']:#iter players
            min = ''
            if data[foo+'_team_players'][player] != '' and data[foo+'_team_players'][player]:#takes care of non values
                print(data[foo+'_team_players'][player])
                time = data[foo+'_team_players'][player]['min']
                if str(type(time)) == "<class 'str'>":
                    for char in time:#iter charecters in time
                        if char != ':':
                            min += str(char)
                        else:
                            break
                    data[foo+'_team_players'][player].update({'min' : min})
                        #print(data[foo+'_team_players'][player]['min'])
    return data
#------------------------------------------------------------------------#