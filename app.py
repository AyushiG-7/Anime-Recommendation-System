from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import pickle

anime = pickle.load(open('files/anime.pkl', 'rb'))

animes = pd.read_csv('files/clean_anime.csv')
ratings = pd.read_csv('files/rating.csv')

def find_similar_anime(animeId):
    similar_users = ratings[(ratings['anime_id'] == animeId) & (ratings['rating'] >= 7)]['user_id'].unique()
    similar_user_recs = ratings[(ratings['user_id'].isin(similar_users)) & (ratings['rating'] >= 7)]['anime_id']
    
    similar_user_recs = similar_user_recs.value_counts() / len(similar_users)
    similar_user_recs = similar_user_recs[similar_user_recs > .1]
    
    all_users = ratings[(ratings['anime_id'].isin(similar_user_recs.index)) & (ratings['rating'] >= 8)]
    all_users_recs = all_users['anime_id'].value_counts() / len(all_users['user_id'].unique())
    
    rec_percent = pd.concat([similar_user_recs, all_users_recs], axis = 1)
    rec_percent.columns = ['similar', 'all']
    
    rec_percent['score'] = rec_percent['similar'] / rec_percent['all']
    
    rec_percent = rec_percent.sort_values('score', ascending = False)
    rec_anime = rec_percent.merge(animes, left_index = True, right_on = 'Id')[['Title']].iloc[0:10]
    return rec_anime

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
def home():
    anime_list = anime['Title'].values
    status = False
    try:
        if request.method == 'POST':
            if request.form:
                title = request.form['title']
                status = True
                index = animes.index[animes['Title'] == title][0]
                animeId = animes.iloc[index, 0]
                rec_anime = find_similar_anime(animeId)
                print(animeId, index, title, status, rec_anime)
            return render_template('recommend.html', rec_anime = rec_anime, anime_list = anime_list, status = status)
    except Exception as e:
        error = {'error' : e}
    return render_template('index.html', anime_list = anime_list, status = status)

if __name__ == '__main__':
    app.run(debug = True)
