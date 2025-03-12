from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)


new_V = pd.read_csv('ex.csv', delimiter=',', index_col='Title')



def recommendations(book, df):
	top_val = df.loc[book].max()  # Largest value in the row
	top_col = df.loc[book].idxmax()  # Column of the largest value

	# Find the five largest values in that column
	top_5_vals = df[top_col].nlargest(6)

	# Find the corresponding row names
	top_5_rows = top_5_vals.index

	recs = [i for i in top_5_rows if i != book]
	return recs


@app.route("/")
def index():
	return render_template("index.html")


@app.route("/recommend", methods = ["POST"])
def recommend():
	book = request.form.get("book")

	if book not in new_V.index:
		return render_template("error.html", error=f"{book} not found. Try again!")

	recs = recommendations(book, new_V)

	return render_template("recommendation.html", book=book, recommendations=recs)

@app.route("/error")
def error():
	return render_template("error.html")



if __name__ == '__main__':
	app.run(debug=True)