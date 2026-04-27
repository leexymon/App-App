import os
import pandas as pd
from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import mysql.connector

app = Flask(__name__)
app.secret_key = "cine3d_secret_2024"

# ─────────────────────────────────────────────
#  DB CONNECTION
# ─────────────────────────────────────────────
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="flask_db"
    )

# ─────────────────────────────────────────────
#  RECOMMENDATION ENGINE  (CSV-based)
# ─────────────────────────────────────────────
CSV_PATH = os.path.join(os.path.dirname(__file__), 'movie_dataset.csv')

def load_csv_data():
    df = pd.read_csv(CSV_PATH)
    for col in ['genres', 'keywords', 'cast', 'director', 'tagline', 'overview']:
        df[col] = df[col].fillna('')
    def combine(row):
        return f"{row['genres']} {row['keywords']} {row['cast']} {row['director']}"
    df['combined'] = df.apply(combine, axis=1)
    return df

print("🎬  Loading movie dataset…")
csv_df = load_csv_data()
tfidf   = TfidfVectorizer(stop_words='english')
tfidf_m = tfidf.fit_transform(csv_df['combined'])
cos_sim  = cosine_similarity(tfidf_m, tfidf_m)
print(f"✅  {len(csv_df)} movies loaded & similarity matrix ready.")

def recommend(title, n=12):
    try:
        matches = csv_df[csv_df['title'].str.lower() == title.lower()]
        if matches.empty:
            return []
        idx = matches.index[0]
        scores = sorted(enumerate(cos_sim[idx]), key=lambda x: x[1], reverse=True)[1:n+1]
        return csv_df.iloc[[i for i, _ in scores]].fillna('').to_dict('records')
    except Exception as e:
        print(f"Recommend error: {e}")
        return []

# ─────────────────────────────────────────────
#  PAGE ROUTES
# ─────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("movie_3d.html")

# ─────────────────────────────────────────────
#  CSV / RECOMMENDATION API
# ─────────────────────────────────────────────
@app.route("/api/movies")
def api_movies():
    top = csv_df.sort_values('popularity', ascending=False).head(50)
    return jsonify(top.fillna('').to_dict('records'))

@app.route("/api/search")
def api_search():
    q = request.args.get('q', '')
    if len(q) < 2:
        return jsonify([])
    res = csv_df[csv_df['title'].str.contains(q, case=False)].head(10)
    return jsonify(res.fillna('').to_dict('records'))

@app.route("/api/recommend/<title>")
def api_recommend(title):
    return jsonify(recommend(title))

# ─────────────────────────────────────────────
#  CRUD  — /api/saved_movies
# ─────────────────────────────────────────────
@app.route("/api/saved_movies", methods=["GET"])
def list_saved():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM movies ORDER BY created_at DESC")
    data = cur.fetchall()
    db.close()
    return jsonify(data)

@app.route("/api/saved_movies", methods=["POST"])
def create_movie():
    body = request.get_json()
    db = get_db(); cur = db.cursor()
    sql = """INSERT INTO movies
             (title, genres, overview, director, cast, release_date, vote_average, popularity, runtime, tagline)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    vals = (
        body.get('title',''), body.get('genres',''), body.get('overview',''),
        body.get('director',''), body.get('cast',''), body.get('release_date',''),
        body.get('vote_average', 0), body.get('popularity', 0),
        body.get('runtime', 0), body.get('tagline','')
    )
    cur.execute(sql, vals)
    db.commit()
    new_id = cur.lastrowid
    db.close()
    return jsonify({"id": new_id, "message": "Movie saved!"}), 201

@app.route("/api/saved_movies/<int:mid>", methods=["GET"])
def get_movie(mid):
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM movies WHERE id=%s", (mid,))
    row = cur.fetchone()
    db.close()
    return jsonify(row) if row else (jsonify({"error": "Not found"}), 404)

@app.route("/api/saved_movies/<int:mid>", methods=["PUT"])
def update_movie(mid):
    body = request.get_json()
    db = get_db(); cur = db.cursor()
    sql = """UPDATE movies SET title=%s, genres=%s, overview=%s, director=%s,
             cast=%s, release_date=%s, vote_average=%s, popularity=%s,
             runtime=%s, tagline=%s WHERE id=%s"""
    vals = (
        body.get('title',''), body.get('genres',''), body.get('overview',''),
        body.get('director',''), body.get('cast',''), body.get('release_date',''),
        body.get('vote_average',0), body.get('popularity',0),
        body.get('runtime',0), body.get('tagline',''), mid
    )
    cur.execute(sql, vals)
    db.commit()
    db.close()
    return jsonify({"message": "Updated!"})

@app.route("/api/saved_movies/<int:mid>", methods=["DELETE"])
def delete_movie(mid):
    db = get_db(); cur = db.cursor()
    cur.execute("DELETE FROM movies WHERE id=%s", (mid,))
    db.commit()
    db.close()
    return jsonify({"message": "Deleted!"})

if __name__ == "__main__":
    app.run(debug=True)