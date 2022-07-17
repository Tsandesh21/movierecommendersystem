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
    topmovierating = TopMovieRating(analysisdata)
    popularmovies = PopularMovies(analysisdata)
    topmoviebyrevenue=TopMoviesByRevenue(analysisdata)
    
    
    titles=movies.title
    context = {
                'data': titles,
                'revenuebyyear':revenuebyyear,
                'revenuebutgetyear': revenuebutgetyear,
                'topmovierating':topmovierating,
                'popularmovies':popularmovies,
                'topmoviebyrevenue':topmoviebyrevenue
            }
    if request.method=="POST":    
        selected_movie_name=request.POST["titles"]
        listmovies=recommend(selected_movie_name)
        data = {
                'listmovies':listmovies,
                'selected_movie_name':selected_movie_name
            }
        print(selected_movie_name)
        return render(request,'recommend/suggestedmovie.html',data)
    else:
        #names,poster,listmovies=recommend(selected_movie_name)
        return render(request,'recommend/home.html',context)

def moviedetail(request,movie):
    # print(movie)
    id=movies[movies['title'].str.replace("/","")==movie]['movie_id'].values[0]
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(id)
    data = requests.get(url)
    data = data.json()
    context={
        'data':data
    }
    return render(request,'recommend/movieinfo.html',context) 

def getgenres(genrecode):
    genrelist=['Action', 'Adventure', 'Fantasy', 'Science Fiction', 'Crime',
       'Drama', 'Thriller', 'Animation', 'Family', 'Western', 'Comedy',
       'Romance', 'Horror', 'Mystery', 'History', 'War', 'Music',
       'Documentary', 'Foreign', 'TV Movie']
    l=[]
    for i in range(1,21):
        if genrecode[i-1]=="1":
            l.append(genrelist[i-1])
    return l

def MovieByGenre(request):
    query=""
    cnt=0
    genrelist=['Action', 'Adventure', 'Fantasy', 'Science Fiction', 'Crime',
       'Drama', 'Thriller', 'Animation', 'Family', 'Western', 'Comedy',
       'Romance', 'Horror', 'Mystery', 'History', 'War', 'Music',
       'Documentary', 'Foreign', 'TV Movie']
    selectedgenres=[]
    if request.method=="POST":         
        for i in range(1,21):
            genre="genre"+str(i)
            if request.POST.get(genre):
                selectedgenres.append(genrelist[i-1])
                if cnt==0:
                    query+="genrecode.str.get("+str(i-1)+")=='1'"
                    cnt+=1
                else:
                    query+=" & "
                    query+="genrecode.str.get("+str(i-1)+")=='1'"
        topmovies=analysisdata.query(query)[['title','vote_average','vote_count','release_date','revenue','runtime','original_language','genrecode']].sort_values(by='vote_average',ascending=False)
        topmovies['title_updated']=analysisdata.title.str.replace("/","")
        topmovies['genres']=topmovies.genrecode.apply(getgenres)
        topmovies['release_date'] = topmovies['release_date'].dt.strftime('%Y-%m-%d')
        json_records = topmovies.reset_index().to_json(orient ='records') 
        data = [] 
        data = json.loads(json_records)
        context={
        'data':data,
        'selectedgenres':selectedgenres
        }
    return render(request,'recommend/moviesbygenre.html',context)