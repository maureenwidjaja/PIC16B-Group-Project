from flask import Flask, render_template, request, url_for
import pandas as pd
import re
import os


app = Flask(__name__)


new_V = pd.read_csv('ex.csv', delimiter=',', index_col='Title')

stopwords = {"the", "a", "and", "of", "in", "on", "at", "by", "with", "for"}
books_pic = os.path.join('static', 'books')
app.config['books_pic'] = books_pic

def clean_title(book):
    title = re.findall(r'\b\w+\b', book.lower())
    cleaned = [word for word in title if word not in stopwords]
    cleaned_title = ' '.join(cleaned)
    cleaned_title = re.sub(r'\s+', ' ', cleaned_title)
    return cleaned_title


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
	book_image = url_for('static', filename='books.png')

	return render_template("index.html", book_pic = book_image)

@app.route("/input")
def input():
	book_image = url_for('static', filename='books.png')

	return render_template("input.html", book_pic = book_image)


@app.route("/recommend", methods = ["POST"])
def recommend():
	book = request.form.get("book")
	book_image = url_for('static', filename='books.png')

	

	if book not in new_V.index:
		book = clean_title(book)
		possible_matches = [title for title in new_V.index if book in title.lower()]
		if possible_matches:
			book = possible_matches[0]
		else:
			return render_template("error.html", error=f"  '{book}' not found in our library. Try again with another title!", book_pic = book_image)

		recs = recommendations(book, new_V)
		return render_template("recommendation.html", book=book, recommendations=recs, book_pic = book_image)
		
	recs = recommendations(book, new_V)

	return render_template("recommendation.html", book=book, recommendations=recs, book_pic = book_image)

@app.route("/error")
def error():
	book_image = url_for('static', filename='books.png')

	return render_template("error.html", book_pic = book_image)

@app.route("/library")
def library():
	book_image = url_for('static', filename='books.png')

	books = new_V.index.tolist()

	return render_template("library.html", books=books, book_pic = book_image)



if __name__ == '__main__':
	app.run(debug=True)