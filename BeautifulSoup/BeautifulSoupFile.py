#!/usr/bin/env python
# coding: utf-8

# # Scrape Books Using Open Library API using BeautifulSoup
# 

# In[67]:


import requests
import matplotlib.pyplot as plt
import seaborn as sns
import json
import pandas as pd
import numpy as np
import concurrent.futures
import csv
from tqdm.notebook import tqdm


# In[69]:


def get_books_by_subject(subject, limit=100, details=True, ebooks=False, published_in=None, offset=0):
    '''
    Args:
    details: if True, includes related subjects, prolific authors, and publishers.
    ebooks: if True,  filters for books with e-books.
    published_in: filters by publication year.
                  For example:
                  http://openlibrary.org/subjects/love.json?published_in=1500-1600
    limit: num of works to include in the response, controls pagination.
    offset: starting offset in the total works, controls pagination.
    '''
    # Creates the API endpoint URL using the subject provided.
    base_url = (f'https://openlibrary.org/subjects/{subject}.json?limit=1')


    # Sends an HTTP GET request to Open Library's API with the query parameters
    # stored in params.
    # The response is stored in response, which contains JSON data.
    response = requests.get(base_url)#, params=params)

    if response.status_code != 200:
        print(f"Error fetching books for {subject}")
        return []

    data = response.json()
    books = data.get("works", [])

    if not books:
        print(f"No books found for {subject}")
        return []

    book_list = []
    for book in books:
        title = book.get("title", "Unknown Title")
        author = book["authors"][0]["name"] if book.get("authors") else "Unknown Author"
        published_year = book.get("first_publish_year", "Unknown Year")

        # Other details we may need for
        subjects = ", ".join(book.get("subject", ["No subjects available"]))
        description = book.get("description", "No description available")
        ebook_available = book.get("ebook_count_i", 0) > 0
        publishers = ", ".join(book.get("publishers", ["Unknown Publisher"]))

        book_list.append({
            "title": title,
            "author": author,
            "published_year": published_year,
            "subjects": subjects,
            "description": description,
            "ebook_available": ebook_available,
            "publishers": publishers
        })

    return book_list  # Return the list of books


# # Combine into one genre
# 
# For instance, "sci-fi" subject and "science-fiction" subject returns different results. So, our next objective is to combine all of them into one genre "Science Fiction". The same goes for other genres like "Romance" or "Fantasy".
# 

# ### Function to combine sub-genres into a big genre:

# In[73]:


def combine_genre(subject):
    """
    Args:
    subject: book subject

    This function collects book lists under sub-genres and combines them into
    one main genre.

    Returns:
    List of all books under a specific genre.
    """

    if subject is None:
        raise ValueError("Please pass a subject name.")

    # Dictionary of genres and their corresponding lists with adjusted formatting
    genre_dict = {
        "romance": [
            "fiction_romance_general", "fiction_romance_historical_general",
            "romance", "man_woman_relationships", "fiction_romance_suspense",
            "fiction_romance_contemporary",
            "fiction_romance_erotica", "fiction_romance_erotic",
            "marriage_fiction", "fiction_erotica_general", "romance",
            "fiction_christian_romance_general", "fiction_romance_historical"
        ],
        "fantasy": [
            "fiction", "fantasy_fiction", "magic", "fiction_fantasy_general",
            "adventure_and_adventurers_fiction",
            "adventure_and_adventurers", "good_and_evil", "fairies", "dragons",
            "cartoons_and_comics", "witchcraft", "history", "wizards", "fairies_fiction"
        ],
        "historical_fiction": [
            "fiction", "historical_fiction", "history", "fiction_historical_general",
            "fiction_romance_historical_general", "fiction_historical", "fiction_general",
            "fiction_romance_historical", "world_war_1939_1945", "great_britain_fiction"
        ],
        "horror": [
            "fiction", "horror", "horror_stories", "horror_tales", "american_horror_tales",
            "horror_fiction", "detective_and_mystery_stories", "crime", "catalepsy", "murder",
            "burial_vaults"
        ],
        "humor": [
            "anecdotes", "humor_general", "american_wit_and_humor",
            "wit_and_humor", "humour", "humor", "funny"
        ],
        "literature": [
            "philosophy", "in_literature", "theory", "criticism", "criticism_and_interpretation",
            "english_literature", "modern_literature", "american_literature",
            "literature", "litterature"
        ],
        "mystery_thriller": [
            "detective_and_mystery_stories", "mystery_fiction", "murder", "mystery",
            "thriller", "detective", "fiction_thrillers_general",
            "suspense", "fiction_thrillers_suspense", "fiction_suspense",
            "mystery", "thriller", "murder",
            "fiction_thrillers_espionage", "police",
            "suspense_fiction", "fiction_general", "detective_and_mystery_stories",
            "crimes_against", "fiction_psychological", "investigation"
        ],
        "science_fiction": [
            "science_fiction", "fiction_science_fiction_general", "american_science_fiction",
            "extraterrestrial_beings", "life_on_other_planets", "extraterrestrial_beings_fiction",
            "time_travel", "sci_fi", "sci-fi", "science-fiction"
        ]
    }

    if subject not in genre_dict:
        raise ValueError("Invalid genre. Please choose from the predefined genres: \
        romance, fantasy, historical_fiction, horror, humor, literature, \
        mystery_thriller, science_fiction.")

    books_under_genre = []
    seen_books = set()  # To store unique books
    i = 1
    print(f"\nBooks under the genre '{subject}':\n")

    for sub_genre in genre_dict[subject]:
        books = get_books_by_subject(sub_genre)  # Get books for the sub-genre

        if books:
            for book in books:
                # Extract the book title and author for uniqueness check)
                title_author = book['author']
                if title_author is None:
                  print("no author")

                # Ensure no dupicates
                if title_author not in seen_books:
                    print(f"{i}. {book['title']} by {book['author']}")
                    books_under_genre.append(book)
                    seen_books.add(title_author)
                    i += 1

        else:
            print(f"No books found for sub-genre '{sub_genre}'")

    return books_under_genre


# # Scrape User Ratings & Reviews

# In[76]:


import requests
from bs4 import BeautifulSoup
import re
link = "https://openlibrary.org/subjects"
data = requests.get(link).text
response = requests.get(link)
soup = BeautifulSoup(response.text, 'html.parser')


# In[77]:


def link2soup(link):
    data = requests.get(link).text
    return BeautifulSoup(data, 'html.parser')


# In[78]:


def parse_to_books(link):
    '''
    Assume we start in "https://openlibrary.org/subjects" (base link) page,
    crawls to each chosen subject link and add it to the base link.
    '''
    # assume start in "https://openlibrary.org/subjects" page
    chosen_subjects = {
        "romance", "fantasy", "historical_fiction", "horror", "humor",
        "literature", "mystery_and_detective_stories", "science_fiction"
    }

    soup = link2soup(link)

    # Extract all subjects links
    all_links = [a['href'] for a in soup.select("div#subjectsPage ul li a") if 'href' in a.attrs]
    # print(all_links[:5])

    # Filter only the chosen subjects
    filtered_links = [
        link for link in all_links
        # ensure only parsing on wanted subjects
        if any(sub in link for sub in chosen_subjects) and "juvenile_literature" not in link]
    # print(filtered_links)

    # assume we wish to click the 'fantasy' (specific subject) page
    # crawling through links
    specific_subject_urls = []
    for i in range(len(filtered_links)):
        next_button = filtered_links[i].split('/')[2]
        specific_subject_url = link + "/" + next_button
        specific_subject_urls.append(specific_subject_url)

    return(specific_subject_urls)


# In[79]:


# assumes we want to go to the total "works" under each subject
def total_works_page(specific_subject_urls):
    '''assumes we want to go to the total "works" under each subject

    Returns: all urls to 'total works' under each subject
    '''
    base_link = "https://openlibrary.org"
    total_works_list = []

    for url in specific_subject_urls:
        soup = link2soup(url)

        # Extract total works link
        total_works_link = [a['href'].replace(" ", "%20") for a in soup.select("a[title='See all works']") if 'href' in a.attrs]

        # Print extracted links (if any)
        print(f"Total works links for {url}: {total_works_link}")

        # Append full URLs to list:
        for link in total_works_link:
            total_works_list.append(base_link + link)

    return total_works_list


# In[82]:


def get_book_hrefs(url):
    '''
    Args: 
        url: takes a URL or list of URLs that it loops through
    Returns: 
        endof_links: returns the hrefs of all the links on the page
    
    Notes:
        if you only pass the first page of results for each function, 
        it will only scrape books from page 1
    '''
    soup = link2soup(url)
    endof_links = [a['href'] for a in soup.select("div#searchResults li.searchResultItem.sri--w-main a.results")
                    if 'href' in a.attrs]
    return endof_links
    print(soup.prettify())

# tried this function, only got the first page of the fantasy, therefore we need an every_page function
# get_book_hrefs('https://openlibrary.org/search?subject=Fantasy')


# In[86]:


# Extracts the link to the next pages of "total works" under a specific subject
def every_page(subject_total_work_url):
    '''
    Assume we are in the first page of the 'total works' under each subject.
    Parse pages from the first page to the last under each subject.

    Return: URL of pages from 1 - n of 'total works' under each subject
    '''
    base_url = 'https://openlibrary.org'
    page_links = []

    for subject_url in subject_total_work_url:
        soup = link2soup(subject_url)

        # Find the last page number
        last_page = soup.select_one('a.ChoosePage[data-ol-link-track="Pager|LastPage"]')
        if last_page:
            last_page_number = int(last_page.get_text())
            # last_page_number = 3 for now for debugging
        else:
            last_page_number = 1  # If there's only one page

        # Generate all page links from 1 to last_page_number
        for page in range(1, last_page_number + 1):
            page_links.append(f'{subject_url}&page={page}')

    return page_links


# In[88]:


def book_links(urls):
    # EDITED: book links really accepts a broad list of "search" style URLs
    # use ThreadPoolExecutor to run code concurrently: this means that multiple
    #   requests may go out and be pending at the same; max_workers is set to
    #   100, but there might be a better value to pick!
    # add tqdm as a progress bar
    # there is still a concern regarding rate limiting: subsequent requests may
    #   get slower and slower or just return with an error (HTTP 422)
    '''
    Assumes we are in the "total works" section of each subject and wish to parse over every book.
    This also includes parsing the next pages continuously until the end.

    Return: URL of every book under "total works" section of each subject
    '''

    base_url = "https://openlibrary.org"
    book_links = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=300) as executor:
        future_to_url = {executor.submit(get_book_hrefs, url): url for url in urls}
        print("SUBMITTED")
        with tqdm(total=len(urls)) as pbar:
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                    book_links.extend(map(lambda href: base_url + href, data))
                except Exception as exc:
                    print('%r generated an exception: %s' % (url, exc))
                finally:
                    pbar.update(1)

    return book_links


# # Using Concurrency

# In[91]:


import concurrent.futures

from tqdm import tqdm

def every_book(all_pages, subject_total_work_url):
    """
    Assume we are in the first page of every 'total works' under a subject
    and wish to parse through every book in every page under the 'total works'.

    Returns: A list of URLs for every book from pages 1 to n under 'total works' of each subject.
    """
    all_book_links = []

    # with tqdm(total=len(all_pages)) as pbar:
    #     with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    #         future_to_page = {executor.submit(book_links, [page]): page for page in all_pages}
    #         for future in concurrent.futures.as_completed(future_to_page):
    #             page = future_to_page[future]
    #             try:
    #                 data = future.result()
    #                 all_book_links.extend(data)
    #             except Exception as exc:
    #                 print('%r generated an exception: %s' % (page, exc))
    #             finally:
    #                 pbar.update(1)

    return all_book_links



# In[93]:


def extract_book_reviews(file):
    '''
    Args:
        Accepts the 'all_book_links.csv', which has a column of all the book links of Open Library. 
    Returns:
        Returns a csv file with all reviews in their columns.
    Notes:
        Extracts book reviews by categories (columns), paired with a percentage value. Returns a dataframe of books and
    '''
    subject_link = f'https://openlibrary.org/search?subject={subject}'
    response = requests.get(subject_link)
    soup = BeautifulSoup(response.text, 'html.parser')

    # extract book titles
    book_titles = every_book(subject) # make sure that the every_book function works

    # extract community reviews
    community_reviews = [x.get_text() for x in soup.select("span.reviews__value")]
    community_data = [re.search(r'\s*(\w[\w\s]*)',x).group(1).strip() for x in community_reviews]

    # extract percentages
    review_percentage = [x.get_text() for x in soup.select("span.percentage")]
    percentage_data = [re.search(r'\s*(\w[\w\s]*)',x).group(1).strip() for x in review_percentage]

    # ensure that community reviews and percentages (lists) are the same length
    if len(community_data) != len(percentage_data):
        print("The reviews and percentages do not match.")

    # find number of reviews
    number_of_reviews = [x.get_text() for x in soup.select("h2.observation-title")]
    number_of_reviews = [re.search(r'\((\d+)\)',x).group(1).strip() for x in number_of_reviews]

    # create an empty dict
    book_dict = {}

    # convert the community reviews and percentages into a dictionary
    for i in range(len(book_titles)): #loop through books
        review_dict = {'Title' : book_titles[i]}

        for j in range(len(community_data)):
            categories = community_data[j]
            percentage_value = review_percentage[j]

            review_dict[categories] = percentage_value

        book_dict.append(review_dict)

    # convert the dictionary into dataframe
    df = pd.Dataframe(book_dict)

    # return the dataframe
    return df


# # What to do next:
# 1. Build ML model
#   - training data: csv file containing books in a specific genre?
#   - testing data: our prediction now?
# 
# 2. Approaches to consider:
#   - Collaborative Filtering (based on user ratings, user reviews e.g. Goodreads)
#   - Content-Based Filtering (based on genre, content description, etc.)
#   - Combination of both Filtering Methods
# 
# 3. Define Training Data
#   - What should the csv file include?
#     1. Book Information: Book ID, Title, Author, Genres, Description
#     2. User Ratings: User ID, Book ID, Rating, User Reviews
# 
# 4. Machine Learning Models to consider:
#   - Content-Based Filtering: Book descriptions and genres
#       - TF-IDF (Term Frequency-Inverse Document Frequency): evaluates the importance of a word in a document : https://www.geeksforgeeks.org/understanding-tf-idf-term-frequency-inverse-document-frequency/
#       - Sci-Kit Learn: classifiers, feature-extraction
#   - Collaborative Filtering: User ratings and reviews
#       - Single Value Decomposition (SVD): can decompose a matrix into 3 matrices, good for ratings: https://www.geeksforgeeks.org/singular-value-decomposition-svd/
#   - From surprise: https://surpriselib.com/
# 
# 
# 5. Hybrid model
#   - Step 1: Get the top books for the user through collaborative filtering
#   - Step 2: Find the most similar books through content based filtering
#   - Step 3: Return the list of recommended books
# 
# 
