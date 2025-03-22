# Book Recommendation System

In this project, we utilized ..... to scrape the data from .....

Initially, we used [BeautifulSoup](https://github.com/maureenwidjaja/PIC16B-Group-Project/blob/78391161c60e94ca5244c0a87bc584f422f1fd29/PIC16B_group_project_BeatifulSoup.ipynb) to scrape the data from Open Library. However, after noticing that it parses the web at an extremely slow rate, we decided to use [Scrapy](https://github.com/maureenwidjaja/PIC16B-Group-Project/tree/78391161c60e94ca5244c0a87bc584f422f1fd29/openlibrary_project) instead as it allows us to parse the web asychronously. However, after encountering multiple issues, we decided to use another method (insert new method here). The issues with Scrapy were mainly due to too many requests being sent to the server, which led us to being blocked by the website, and due to the fact that Open Library is not a popular platform where people review books in general. Moreover, books that have 'ratings' are not guarenteed to have 'reviews'. The quantity in which books are rated are low and books that are reviewed are even smaller in quantity. Therefore, we changed our method.

## File Description

### PIC16B_group_project_BeatifulSoup.ipynb

This was our initial file that contains the BeautifulSoup code. It recognizes that each subject has its sub-category so we ensured that we only covered book subject URLs that are more for entertainment purposes, such as "Romance", "Fantasy", "Historical Fiction", "Horror", "Humor", "Literature", "Mystery and Detective Stories", and "Science Fiction". Moreover, we ensured that the book URLs we gathered are unique and not duplicated in order to make our data cleaner. As the progress bar shows in the last few lines, our code parsed the library at an extremely slow rate.

### book_spider.py inside the openlibrary_project Folder

This folder contains our Scrapy code to parse Open Library. It assumes that we start in the [Subject Page](https://openlibrary.org/subjects) and parses through each book under each subject from there. Although the code parsed the correct book links for the first 15 pages, it returned an error as we increased the number of pages to parse. Although we tried to debug and solve it, we deduced that there were existing settings or laws that do not allow us to bulk parse using Scrapy.

