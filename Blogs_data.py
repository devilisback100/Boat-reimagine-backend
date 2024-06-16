from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
import requests
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# Create a SQLite database connection
conn = sqlite3.connect('blogs.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS blogs
    (title TEXT, link TEXT, image TEXT, published_at TEXT, min_read TEXT)
''')


@app.route('/get_blogs', methods=['GET'])
def get_blogs():
    # Create a new SQLite connection and cursor for each request
    conn = sqlite3.connect('blogs.db', check_same_thread=False)
    c = conn.cursor()

    # Check if data already exists in the database
    c.execute("SELECT * FROM blogs")
    data = c.fetchall()
    if data:
        return jsonify(data)
    else:

        url = 'https://www.boat-lifestyle.com/blogs/blog'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        blogs = soup.find_all('div', class_='article--item scroller__inner')
        blog_data = []
        for blog in blogs:
            title = blog.find('p', class_='article--title').text.strip()
            link = blog.find('a')['href']
            image = blog.find('img', class_='article-item__image')['src']
            published_at = blog.find(
                'span', class_='a_published-at').text.strip()
            min_read = blog.find('span', class_='min-read').text.strip()
            blog_data.append((title, link, image, published_at, min_read))

        # Insert the data into the database
        c.executemany("INSERT INTO blogs VALUES (?,?,?,?,?)", blog_data)
        conn.commit()
        conn.close()


        return jsonify(blog_data)



@app.route('/get_code/<path:url>', methods=['GET'])
def get_code(url):
    url = f"{url}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find elements with class 'rte'
    elements = soup.find_all(class_='rte')
    html_data = [element.prettify() for element in elements]
    
    return jsonify(html_data)


if __name__ == '__main__':
    app.run(debug=True)
