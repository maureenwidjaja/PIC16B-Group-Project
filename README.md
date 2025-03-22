# Book Recommendation System

In this project, we extracted specific data from UCSD's extracted Goodreads dataset. Then, we transferred

Initially, we used [BeautifulSoup](https://github.com/maureenwidjaja/PIC16B-Group-Project/tree/main/BeautifulSoup) to scrape the data from Open Library. However, after noticing that it parses the web at an extremely slow rate, we decided to use [Scrapy](https://github.com/maureenwidjaja/PIC16B-Group-Project/tree/78391161c60e94ca5244c0a87bc584f422f1fd29/openlibrary_project)  instead as it allows us to parse the web asynchronously. However, after encountering multiple issues, we decided to extract specific data from the dataset that UCSD had extracted from Goodreads in 2017. The issues with Scrapy were mainly due to too many requests being sent to the server, which led us to being blocked by the website, and due to the fact that Open Library is not a popular platform where people review books in general. Moreover, books that have 'ratings' are not guaranteed to have 'reviews'. The quantity of books that are rated is low, and the number of books that are reviewed is even smaller. Therefore, we changed our method and extracted data from Goodreads that were scraped by [UCSD](https://cseweb.ucsd.edu/~jmcauley/datasets/goodreads.html) in 2017.

## File Description

#### BeatifulSoup Folder

This was our initial folder that contains all the BeautifulSoup code with Concurrency. It recognizes that each subject has its sub-category so we ensured that we only covered book subject URLs that are more for entertainment purposes, such as "Romance", "Fantasy", "Historical Fiction", "Horror", "Humor", "Literature", "Mystery and Detective Stories", and "Science Fiction". Moreover, we ensured that the book URLs we gathered are unique and not duplicated in order to make our data cleaner. As the progress bar shows in the last few lines, our code parsed the library at an extremely slow rate.

#### book_spider.py inside the openlibrary_project Folder

This folder contains our Scrapy code to parse Open Library. It assumes that we start in the [Subject Page](https://openlibrary.org/subjects) and parses through each book under each subject from there. Although the code parsed the correct book links for the first 15 pages, it returned an error as we increased the number of pages to parse. Although we tried to debug and solve it, we deduced that there were existing settings or laws that do not allow us to bulk parse using Scrapy.

#### UCSD_method.ipynb

This [method](https://github.com/maureenwidjaja/PIC16B-Group-Project/blob/main/UCSD_method.ipynb) is another way of gathering data where we used Goodreads datasets [UCSD](https://cseweb.ucsd.edu/~jmcauley/datasets/goodreads.html) had already scraped in late 2017. In this file, we used the goodreads_books.json.gz metadata (about 2.3 million books), and took a randomized popular sample that was representative of the books (about 50,000) books. Then, we extracted the genres from the books and  hot encoded them into the dataframe, making the genres columns and the 1s and 0s values to see if they had the genre or not.

#### Scrapy_cleaned_output.ipynb

This is the [output](https://github.com/maureenwidjaja/PIC16B-Group-Project/blob/main/Scrapy_cleaned_output.ipynb) from the Scrapy code which only has 53 rows and 5 columns. After some cleaning, each column corresponds to the review description, e.g. "slow paced, fast paced, etc." and the numerical output represent how much the book corresponds to that description. By having numerical outputs, it will be easier for our model to process the data. However, since we are shifting our method to in the UCSD_method file, this file exists only to prove that our old method using Scrapy is not efficient as it is not outputting the thousands of book data that we intended.

#### ML_model.ipynb

This is the machine learning model which we created using Keras, Tensorflow, and Scikit-learn. 

#### Flask folder

So, once all our data was collected and trained using our NMF model, we created a Flask Application for users to use the system. The Application opens up to a Home page from our index.html, where users have the option to get started with book recommendations by clicking the “Start” button or navigating to another page from the navigation menu at the top of the page. Because the basic styling properties in Flask are a bit basic, we also implemented tools from Bootstrap. This allowed us to have more stylistic freedom with the application and add user-friendly tools such as the navigation menu.
