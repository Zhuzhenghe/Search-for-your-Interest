from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = 'change-this-secret'

# Load sample items
with open(os.path.join('data', 'items.json'), 'r') as f:
    ITEMS = json.load(f)

# Simple search by keyword

def search_items(query):
    query_lower = query.lower()
    results = []
    for item in ITEMS:
        if query_lower in item['title'].lower() or any(query_lower in t for t in item['tags']):
            results.append(item)
    return results

# Update user interest based on clicked item type and tags

def update_interest(item):
    interests = session.get('interests', {})
    for tag in item.get('tags', []):
        interests[tag] = interests.get(tag, 0) + 1
    session['interests'] = interests

# Recommend items based on interests

def recommend_items():
    interests = session.get('interests', {})
    if not interests:
        # return popular items (first 3) as default
        return ITEMS[:3]
    # sort interests by weight
    sorted_tags = sorted(interests.items(), key=lambda x: x[1], reverse=True)
    top_tag = sorted_tags[0][0]
    results = [item for item in ITEMS if top_tag in item['tags']]
    if not results:
        results = ITEMS[:3]
    return results[:3]

@app.route('/', methods=['GET'])
def index():
    rec_items = recommend_items()
    return render_template('index.html', recommendations=rec_items)

@app.route('/search')
def search():
    q = request.args.get('q', '')
    results = search_items(q) if q else []
    return render_template('search.html', query=q, results=results)

@app.route('/item/<int:item_id>')
def item_detail(item_id):
    item = next((i for i in ITEMS if i['id'] == item_id), None)
    if not item:
        return redirect(url_for('index'))
    update_interest(item)
    return render_template('item.html', item=item)

if __name__ == '__main__':
    app.run(debug=True)
