from django.shortcuts import render
import pickle
from django.conf import settings
import pandas as pd
import requests
import plotly
import plotly.express as px
from .analysisview import *
import bz2file as bz2

csp = str(settings.BASE_DIR)
movies_dict = pickle.load(open(csp+'/recommend/models/movies.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

data = bz2.BZ2File(csp+'/recommend/models/bz2file_similarity.pbz2', 'rb')
similarity = pickle.load(data)

analysis = pickle.load(open(csp+'/recommend/models/analysisdata.pkl', 'rb'))
analysisdata = pd.DataFrame(analysis)

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    listmovies=[]
    reco_movie_list=[]
    movie_poster=[]
    for i in movie_list:
        movie_id=movies.iloc[i[0]].movie_id
        reco_movie_list.append(movies.iloc[i[0]].title)
        movie_poster.append(fetch_poster(movie_id))
        listmovies.append({'movie':movies.iloc[i[0]].title,'poster':fetch_poster(movie_id)})
    #return reco_movie_list,movie_poster,li
    return listmovies

def home(request):
    
    #fig = px.bar(x=["a", "b", "c"], y=[1, 3, 2])
    # revenuebyyear = RevenueByYear(analysisdata)
    revenuebyyear = plotly.offline.plot(RevenueByYear(analysisdata), auto_open = False, output_type="div")
    revenuebutgetyear = plotly.offline.plot(RevenueButgetYear(analysisdata), auto_open = False, output_type="div")

    
    titles=movies.title
    context = {
                'data': titles,
                'revenuebyyear':revenuebyyear,
                'revenuebutgetyear': revenuebutgetyear,
            }
    if request.method=="POST":    
        selected_movie_name=request.POST["titles"]
        listmovies=recommend(selected_movie_name)
        data = {
                'listmovies':listmovies,
            }
        print(selected_movie_name)
        return render(request,'recommend/suggestedmovie.html',data)
    else:
        #names,poster,listmovies=recommend(selected_movie_name)
        return render(request,'recommend/home.html',context)

def moviedetail(request,movie):
    # print(movie)
    id=movies[movies['title']==movie]['movie_id'].values[0]
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(id)
    data = requests.get(url)
    data = data.json()
    context={
        'data':data
    }
    return render(request,'recommend/movieinfo.html',context) 