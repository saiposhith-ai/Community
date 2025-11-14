from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import re
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Configuration
DATA_DIR = 'data'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD_HASH = generate_password_hash('admin123')  # Change this password

# Ensure data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
# Initialize JSON files with default data
def init_data_files():
    default_data = {
        'services.json': {
            "services": [
                {
                    "id": 1,
                    "title": "Strategy & Research",
                    "description": "Mauris ut felis malesuada eros varius tristique a at orci. Nulla vulputate, leo sit amet rhoncus suscipit, enim ex venenatis ipsum, et porttitor.",
                    "icon": "telescope-outline"
                },
                {
                    "id": 2,
                    "title": "Web Development",
                    "description": "Mauris ut felis malesuada eros varius tristique a at orci. Nulla vulputate, leo sit amet rhoncus suscipit, enim ex venenatis ipsum, et porttitor.",
                    "icon": "desktop-outline"
                },
                {
                    "id": 3,
                    "title": "Web Solution",
                    "description": "Mauris ut felis malesuada eros varius tristique a at orci. Nulla vulputate, leo sit amet rhoncus suscipit, enim ex venenatis ipsum, et porttitor.",
                    "icon": "globe-outline"
                },
                {
                    "id": 4,
                    "title": "Digital Marketing",
                    "description": "Comprehensive digital marketing solutions to boost your online presence and reach your target audience effectively.",
                    "icon": "trending-up-outline"
                },
                {
                    "id": 5,
                    "title": "App Design",
                    "description": "Beautiful and functional mobile app designs that provide excellent user experience across all platforms.",
                    "icon": "phone-portrait-outline"
                }
            ]
        },
        'features.json': {
            "features": [
                {
                    "id": 1,
                    "title": "Idea & Analysis",
                    "description": "Praesent tincidunt congue est ut hendrerit. Pellentesque et eros sit amet ipsum venenatis.",
                    "icon": "bulb-outline"
                },
                {
                    "id": 2,
                    "title": "Designing",
                    "description": "Praesent tincidunt congue est ut hendrerit. Pellentesque et eros sit amet ipsum venenatis.",
                    "icon": "color-palette-outline"
                },
                {
                    "id": 3,
                    "title": "Development",
                    "description": "Praesent tincidunt congue est ut hendrerit. Pellentesque et eros sit amet ipsum venenatis.",
                    "icon": "code-slash-outline"
                },
                {
                    "id": 4,
                    "title": "Testing & Launching",
                    "description": "Praesent tincidunt congue est ut hendrerit. Pellentesque et eros sit amet ipsum venenatis.",
                    "icon": "rocket-outline"
                }
            ]
        },
        'blog.json': {
            "posts": [
                {
                    "id": 1,
                    "title": "Vestibulum massa arcu, consectetu pellentesque scelerisque",
                    "content": "Sed quis sagittis velit. Aliquam velit eros, bibendum ut massa et, consequat laoreet erat nam ac imperdiet.",
                    "date": "2024-03-07",
                    "image": "/static/images/blog-1.jpg",
                    "comments": [],
                    "shares": 0
                },
                {
                    "id": 2,
                    "title": "Quisque egestas iaculis felis eget placerat ut pulvinar mi",
                    "content": "Sed quis sagittis velit. Aliquam velit eros, bibendum ut massa et, consequat laoreet erat nam ac imperdiet.",
                    "date": "2024-03-07",
                    "image": "/static/images/blog-2.jpg",
                    "comments": [],
                    "shares": 0
                }
            ]
        },
        'contacts.json': {
            "contacts": []
        },
        'site_content.json': {
            "hero": {
                "subtitle": "We Are Product Designer From UK",
                "title": "We Design Interfaces That Users Love",
                "description": "Morbi sed lacus nec risus finibus feugiat et fermentum nibh. Pellentesque vitae ante at elit fringilla ac at purus."
            },
            "about": {
                "title": "Why Our Agency",
                "description1": "In dictum aliquam turpis lacinia iaculis. Fusce vel malesuada magna. Nulla vel maximus risus. Donec volutpat metus lacinia risus accumsan, ac bibendum libero efficitur.",
                "description2": "Praesent rhoncus commodo tortor, id pulvinar nisl blandit at. Nulla facilisi. Quisque turpis ante, vehicula condimentum arcu.",
                "stats": {
                    "clients": 9875,
                    "projects": 7894,
                    "years": 65
                }
            }
        },
        'pages.json': {
            "faq": {
                "title": "Frequently Asked Questions",
                "content": "Here are some frequently asked questions about our services."
            },
            "portfolio": {
                "title": "Our Portfolio",
                "content": "Explore our amazing portfolio of projects."
            },
            "privacy": {
                "title": "Privacy Policy",
                "content": "Your privacy is important to us. This policy explains how we handle your data."
            },
            "terms": {
                "title": "Terms & Conditions",
                "content": "By using our services, you agree to these terms and conditions."
            },
            "support": {
                "title": "Support",
                "content": "Need help? Contact our support team for assistance."
            }
        },
        'announcements.json': {
            "announcements": [
                {
                    "id": 1,
                    "message": "🎉 New service launched! Check out our Digital Marketing packages.",
                    "link": "/services/digital-marketing",
                    "link_text": "Learn More",
                    "type": "info",
                    "is_active": True,
                    "created_date": "2024-03-07",
                    "display_order": 1
                }
            ]
        }
    }

    for filename, data in default_data.items():
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            save_json_data(filename, data)
            
def load_json_data(filename):
    try:
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_json_data(filename, data):
    try:
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving {filename}: {e}")
        return False

# Profanity filter
VULGAR_WORDS = [
    'spam', 'hate', 'abuse', 'offensive', 'inappropriate',
    # Add more words as needed
]

def contains_vulgar_content(text):
    text_lower = text.lower()
    for word in VULGAR_WORDS:
        if word in text_lower:
            return True
    return False

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please log in to access the admin panel.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Initialize data files
init_data_files()

@app.route('/')
def index():
    services = load_json_data('services.json').get('services', [])[:3]
    features = load_json_data('features.json').get('features', [])
    blog_posts = load_json_data('blog.json').get('posts', [])[:4]
    site_content = load_json_data('site_content.json')
    
    # Get active announcements
    announcements_data = load_json_data('announcements.json')
    active_announcements = [
        a for a in announcements_data.get('announcements', [])
        if a.get('is_active', False)
    ]
    # Sort by display_order
    active_announcements.sort(key=lambda x: x.get('display_order', 999))

    return render_template('index.html',
                         services=services,
                         features=features,
                         blog_posts=blog_posts,
                         site_content=site_content,
                         announcements=active_announcements)

@app.route('/admin/announcements')
@login_required
def admin_announcements():
    announcements = load_json_data('announcements.json').get('announcements', [])
    return render_template('admin/announcements.html', announcements=announcements)

@app.route('/admin/announcements/add', methods=['GET', 'POST'])
@login_required
def admin_add_announcement():
    if request.method == 'POST':
        message = request.form.get('message')
        link = request.form.get('link', '')
        link_text = request.form.get('link_text', 'Learn More')
        announcement_type = request.form.get('type', 'info')
        is_active = request.form.get('is_active') == 'on'
        display_order = int(request.form.get('display_order', 999))

        if not message:
            flash('Message is required.', 'error')
            return redirect(url_for('admin_add_announcement'))

        announcements_data = load_json_data('announcements.json')
        if 'announcements' not in announcements_data:
            announcements_data['announcements'] = []

        new_announcement = {
            'id': max([a.get('id', 0) for a in announcements_data['announcements']], default=0) + 1,
            'message': message,
            'link': link,
            'link_text': link_text,
            'type': announcement_type,
            'is_active': is_active,
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'display_order': display_order
        }

        announcements_data['announcements'].append(new_announcement)
        if save_json_data('announcements.json', announcements_data):
            flash('Announcement added successfully!', 'success')
            return redirect(url_for('admin_announcements'))
        else:
            flash('Error saving announcement.', 'error')

    return render_template('admin/add_announcement.html')

@app.route('/admin/announcements/edit/<int:announcement_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_announcement(announcement_id):
    announcements_data = load_json_data('announcements.json')
    announcement = next((a for a in announcements_data.get('announcements', []) 
                        if a['id'] == announcement_id), None)

    if not announcement:
        flash('Announcement not found.', 'error')
        return redirect(url_for('admin_announcements'))

    if request.method == 'POST':
        announcement['message'] = request.form.get('message')
        announcement['link'] = request.form.get('link', '')
        announcement['link_text'] = request.form.get('link_text', 'Learn More')
        announcement['type'] = request.form.get('type', 'info')
        announcement['is_active'] = request.form.get('is_active') == 'on'
        announcement['display_order'] = int(request.form.get('display_order', 999))

        if save_json_data('announcements.json', announcements_data):
            flash('Announcement updated successfully!', 'success')
            return redirect(url_for('admin_announcements'))
        else:
            flash('Error updating announcement.', 'error')

    return render_template('admin/edit_announcement.html', announcement=announcement)

@app.route('/admin/announcements/delete/<int:announcement_id>')
@login_required
def admin_delete_announcement(announcement_id):
    announcements_data = load_json_data('announcements.json')
    announcements_data['announcements'] = [
        a for a in announcements_data.get('announcements', []) 
        if a['id'] != announcement_id
    ]

    if save_json_data('announcements.json', announcements_data):
        flash('Announcement deleted successfully!', 'success')
    else:
        flash('Error deleting announcement.', 'error')

    return redirect(url_for('admin_announcements'))

@app.route('/admin/announcements/toggle/<int:announcement_id>')
@login_required
def admin_toggle_announcement(announcement_id):
    announcements_data = load_json_data('announcements.json')
    announcement = next((a for a in announcements_data.get('announcements', []) 
                        if a['id'] == announcement_id), None)

    if announcement:
        announcement['is_active'] = not announcement.get('is_active', False)
        if save_json_data('announcements.json', announcements_data):
            status = "activated" if announcement['is_active'] else "deactivated"
            flash(f'Announcement {status} successfully!', 'success')
        else:
            flash('Error updating announcement.', 'error')
    else:
        flash('Announcement not found.', 'error')

    return redirect(url_for('admin_announcements'))

@app.route('/services')
@app.route('/services/<service_name>')
def services(service_name=None):
    services_data = load_json_data('services.json').get('services', [])
    if service_name:
        service = next(
            (s for s in services_data
             if s['title'].lower().replace(' ', '-').replace('&', '') == service_name.lower()),
            None
        )
        if service:
            return render_template('service_detail.html',
                                   service=service,
                                   services=services_data)
        flash('Service not found.', 'error')
        return redirect(url_for('services'))
    return render_template('services.html', services=services_data)


@app.route('/blog')
@app.route('/blog/<int:post_id>')
def blog(post_id=None):
    blog_data = load_json_data('blog.json')
    posts = blog_data.get('posts', [])
    services_list = load_json_data('services.json').get('services', [])  # add
    if post_id:
        post = next((p for p in posts if p['id'] == post_id), None)
        if post:
            return render_template('blog_detail.html', post=post, services=services_list)  # add services
        flash('Blog post not found.', 'error')
        return redirect(url_for('blog'))
    return render_template('blog.html', posts=posts, services=services_list)  # add services

@app.route('/faq')
def faq():
    page_data = load_json_data('pages.json').get('faq', {})
    services_list = load_json_data('services.json').get('services', [])  # add
    return render_template('page.html', page=page_data, page_type='faq', services=services_list)  # add services

@app.route('/portfolio')
def portfolio():
    page_data = load_json_data('pages.json').get('portfolio', {})
    services_list = load_json_data('services.json').get('services', [])  # add
    return render_template('page.html', page=page_data, page_type='portfolio', services=services_list)

@app.route('/privacy')
def privacy():
    page_data = load_json_data('pages.json').get('privacy', {})
    services_list = load_json_data('services.json').get('services', [])
    return render_template('page.html', page=page_data, page_type='privacy', services=services_list)

@app.route('/terms')
def terms():
    page_data = load_json_data('pages.json').get('terms', {})
    services_list = load_json_data('services.json').get('services', [])
    return render_template('page.html', page=page_data, page_type='terms', services=services_list)

@app.route('/support')
def support():
    page_data = load_json_data('pages.json').get('support', {})
    services_list = load_json_data('services.json').get('services', [])
    return render_template('page.html', page=page_data, page_type='support', services=services_list)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        if not all([name, email, subject, message]):
            flash('All fields are required.', 'error')
            return redirect(url_for('contact'))

        if contains_vulgar_content(f"{name} {subject} {message}"):
            flash('Your message contains inappropriate content and cannot be submitted.', 'error')
            return redirect(url_for('contact'))

        # Save contact
        contacts_data = load_json_data('contacts.json')
        new_contact = {
            'id': len(contacts_data.get('contacts', [])) + 1,
            'name': name,
            'email': email,
            'subject': subject,
            'message': message,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'new'
        }

        if 'contacts' not in contacts_data:
            contacts_data['contacts'] = []

        contacts_data['contacts'].append(new_contact)
        save_json_data('contacts.json', contacts_data)

        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    services_list = load_json_data('services.json').get('services', [])  # add
    return render_template('contact.html', services=services_list)

# Blog interaction routes
@app.route('/blog/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    name = request.form.get('name')
    comment_text = request.form.get('comment')

    if not all([name, comment_text]):
        flash('Name and comment are required.', 'error')
        return redirect(url_for('blog', post_id=post_id))

    if contains_vulgar_content(f"{name} {comment_text}"):
        flash('Your comment contains inappropriate content and cannot be posted.', 'error')
        return redirect(url_for('blog', post_id=post_id))

    blog_data = load_json_data('blog.json')
    posts = blog_data.get('posts', [])

    post = next((p for p in posts if p['id'] == post_id), None)
    if post:
        if 'comments' not in post:
            post['comments'] = []

        new_comment = {
            'id': len(post['comments']) + 1,
            'name': name,
            'comment': comment_text,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        post['comments'].append(new_comment)
        save_json_data('blog.json', blog_data)
        flash('Comment added successfully!', 'success')
    else:
        flash('Blog post not found.', 'error')

    return redirect(url_for('blog', post_id=post_id))

@app.route('/blog/<int:post_id>/share', methods=['POST'])
def share_post(post_id):
    blog_data = load_json_data('blog.json')
    posts = blog_data.get('posts', [])

    post = next((p for p in posts if p['id'] == post_id), None)
    if post:
        if 'shares' not in post:
            post['shares'] = 0
        post['shares'] += 1
        save_json_data('blog.json', blog_data)
        return jsonify({'success': True, 'shares': post['shares']})

    return jsonify({'success': False, 'error': 'Post not found'})

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin_logged_in'] = True
            flash('Successfully logged in!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Successfully logged out!', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin')
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    services_count = len(load_json_data('services.json').get('services', []))
    features_count = len(load_json_data('features.json').get('features', []))
    blog_posts_count = len(load_json_data('blog.json').get('posts', []))
    contacts_count = len(load_json_data('contacts.json').get('contacts', []))
    announcements_count = len(load_json_data('announcements.json').get('announcements', []))

    contacts_data = load_json_data('contacts.json')
    recent_contacts = sorted(
        contacts_data.get('contacts', []),
        key=lambda x: x.get('date', ''),
        reverse=True
    )[:5]

    stats = {
        'services': services_count,
        'features': features_count,
        'blog_posts': blog_posts_count,
        'contacts': contacts_count,
        'announcements': announcements_count
    }

    return render_template('admin/dashboard.html', stats=stats, recent_contacts=recent_contacts)

@app.route('/admin/services')
@login_required
def admin_services():
    services = load_json_data('services.json').get('services', [])
    return render_template('admin/services.html', services=services)

@app.route('/admin/services/add', methods=['GET', 'POST'])
@login_required
def admin_add_service():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        icon = request.form.get('icon')

        if not all([title, description, icon]):
            flash('All fields are required.', 'error')
            return redirect(url_for('admin_add_service'))

        services_data = load_json_data('services.json')
        if 'services' not in services_data:
            services_data['services'] = []

        new_service = {
            'id': max([s.get('id', 0) for s in services_data['services']], default=0) + 1,
            'title': title,
            'description': description,
            'icon': icon
        }

        services_data['services'].append(new_service)
        if save_json_data('services.json', services_data):
            flash('Service added successfully!', 'success')
            return redirect(url_for('admin_services'))
        else:
            flash('Error saving service.', 'error')

    return render_template('admin/add_service.html')

@app.route('/admin/services/edit/<int:service_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_service(service_id):
    services_data = load_json_data('services.json')
    service = next((s for s in services_data.get('services', []) if s['id'] == service_id), None)

    if not service:
        flash('Service not found.', 'error')
        return redirect(url_for('admin_services'))

    if request.method == 'POST':
        service['title'] = request.form.get('title')
        service['description'] = request.form.get('description')
        service['icon'] = request.form.get('icon')

        if save_json_data('services.json', services_data):
            flash('Service updated successfully!', 'success')
            return redirect(url_for('admin_services'))
        else:
            flash('Error updating service.', 'error')

    return render_template('admin/edit_service.html', service=service)

@app.route('/admin/services/delete/<int:service_id>')
@login_required
def admin_delete_service(service_id):
    services_data = load_json_data('services.json')
    services_data['services'] = [s for s in services_data.get('services', []) if s['id'] != service_id]

    if save_json_data('services.json', services_data):
        flash('Service deleted successfully!', 'success')
    else:
        flash('Error deleting service.', 'error')

    return redirect(url_for('admin_services'))

@app.route('/admin/features')
@login_required
def admin_features():
    features = load_json_data('features.json').get('features', [])
    return render_template('admin/features.html', features=features)

@app.route('/admin/features/add', methods=['GET', 'POST'])
@login_required
def admin_add_feature():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        icon = request.form.get('icon')

        if not all([title, description, icon]):
            flash('All fields are required.', 'error')
            return redirect(url_for('admin_add_feature'))

        features_data = load_json_data('features.json')
        if 'features' not in features_data:
            features_data['features'] = []

        new_feature = {
            'id': max([f.get('id', 0) for f in features_data['features']], default=0) + 1,
            'title': title,
            'description': description,
            'icon': icon
        }

        features_data['features'].append(new_feature)
        if save_json_data('features.json', features_data):
            flash('Feature added successfully!', 'success')
            return redirect(url_for('admin_features'))
        else:
            flash('Error saving feature.', 'error')

    return render_template('admin/add_feature.html')

@app.route('/admin/features/edit/<int:feature_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_feature(feature_id):
    features_data = load_json_data('features.json')
    feature = next((f for f in features_data.get('features', []) if f['id'] == feature_id), None)

    if not feature:
        flash('Feature not found.', 'error')
        return redirect(url_for('admin_features'))

    if request.method == 'POST':
        feature['title'] = request.form.get('title')
        feature['description'] = request.form.get('description')
        feature['icon'] = request.form.get('icon')

        if save_json_data('features.json', features_data):
            flash('Feature updated successfully!', 'success')
            return redirect(url_for('admin_features'))
        else:
            flash('Error updating feature.', 'error')

    return render_template('admin/edit_feature.html', feature=feature)

@app.route('/admin/features/delete/<int:feature_id>')
@login_required
def admin_delete_feature(feature_id):
    features_data = load_json_data('features.json')
    features_data['features'] = [f for f in features_data.get('features', []) if f['id'] != feature_id]

    if save_json_data('features.json', features_data):
        flash('Feature deleted successfully!', 'success')
    else:
        flash('Error deleting feature.', 'error')

    return redirect(url_for('admin_features'))

@app.route('/admin/blog')
@login_required
def admin_blog():
    posts = load_json_data('blog.json').get('posts', [])
    return render_template('admin/blog.html', posts=posts)

@app.route('/admin/blog/add', methods=['GET', 'POST'])
@login_required
def admin_add_blog():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        image = request.form.get('image', '/static/images/default-blog.jpg')

        if not all([title, content]):
            flash('Title and content are required.', 'error')
            return redirect(url_for('admin_add_blog'))

        blog_data = load_json_data('blog.json')
        if 'posts' not in blog_data:
            blog_data['posts'] = []

        new_post = {
            'id': max([p.get('id', 0) for p in blog_data['posts']], default=0) + 1,
            'title': title,
            'content': content,
            'image': image,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'comments': [],
            'shares': 0
        }

        blog_data['posts'].append(new_post)
        if save_json_data('blog.json', blog_data):
            flash('Blog post added successfully!', 'success')
            return redirect(url_for('admin_blog'))
        else:
            flash('Error saving blog post.', 'error')

    return render_template('admin/add_blog.html')

@app.route('/admin/blog/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_blog(post_id):
    blog_data = load_json_data('blog.json')
    post = next((p for p in blog_data.get('posts', []) if p['id'] == post_id), None)

    if not post:
        flash('Blog post not found.', 'error')
        return redirect(url_for('admin_blog'))

    if request.method == 'POST':
        post['title'] = request.form.get('title')
        post['content'] = request.form.get('content')
        post['image'] = request.form.get('image', post.get('image', '/static/images/default-blog.jpg'))

        if save_json_data('blog.json', blog_data):
            flash('Blog post updated successfully!', 'success')
            return redirect(url_for('admin_blog'))
        else:
            flash('Error updating blog post.', 'error')

    return render_template('admin/edit_blog.html', post=post)

@app.route('/admin/blog/delete/<int:post_id>')
@login_required
def admin_delete_blog(post_id):
    blog_data = load_json_data('blog.json')
    blog_data['posts'] = [p for p in blog_data.get('posts', []) if p['id'] != post_id]

    if save_json_data('blog.json', blog_data):
        flash('Blog post deleted successfully!', 'success')
    else:
        flash('Error deleting blog post.', 'error')

    return redirect(url_for('admin_blog'))

@app.route('/admin/contacts')
@login_required
def admin_contacts():
    contacts = load_json_data('contacts.json').get('contacts', [])
    services_list = load_json_data('services.json').get('services', [])  # fix
    return render_template('admin/contacts.html', contacts=contacts, services=services_list)  # fix

@app.route('/admin/contacts/mark-read/<int:contact_id>')
@login_required
def admin_mark_contact_read(contact_id):
    contacts_data = load_json_data('contacts.json')
    contact = next((c for c in contacts_data.get('contacts', []) if c['id'] == contact_id), None)

    if contact:
        contact['status'] = 'read'
        if save_json_data('contacts.json', contacts_data):
            flash('Contact marked as read!', 'success')
        else:
            flash('Error updating contact status.', 'error')
    else:
        flash('Contact not found.', 'error')

    return redirect(url_for('admin_contacts'))

@app.route('/admin/contacts/delete/<int:contact_id>')
@login_required
def admin_delete_contact(contact_id):
    contacts_data = load_json_data('contacts.json')
    contacts_data['contacts'] = [c for c in contacts_data.get('contacts', []) if c['id'] != contact_id]

    if save_json_data('contacts.json', contacts_data):
        flash('Contact deleted successfully!', 'success')
    else:
        flash('Error deleting contact.', 'error')

    return redirect(url_for('admin_contacts'))

@app.route('/admin/pages')
@login_required
def admin_pages():
    pages = load_json_data('pages.json')
    return render_template('admin/pages.html', pages=pages)

@app.route('/admin/pages/edit/<page_name>', methods=['GET', 'POST'])
@login_required
def admin_edit_page(page_name):
    pages_data = load_json_data('pages.json')
    page = pages_data.get(page_name)

    if not page:
        flash('Page not found.', 'error')
        return redirect(url_for('admin_pages'))

    if request.method == 'POST':
        page['title'] = request.form.get('title')
        page['content'] = request.form.get('content')

        if save_json_data('pages.json', pages_data):
            flash('Page updated successfully!', 'success')
            return redirect(url_for('admin_pages'))
        else:
            flash('Error updating page.', 'error')

    return render_template('admin/edit_page.html', page=page, page_name=page_name)

@app.route('/admin/site-content', methods=['GET', 'POST'])
@login_required
def admin_site_content():
    site_content = load_json_data('site_content.json')

    if request.method == 'POST':
        # Update hero section
        site_content['hero']['subtitle'] = request.form.get('hero_subtitle')
        site_content['hero']['title'] = request.form.get('hero_title')
        site_content['hero']['description'] = request.form.get('hero_description')

        # Update about section
        site_content['about']['title'] = request.form.get('about_title')
        site_content['about']['description1'] = request.form.get('about_description1')
        site_content['about']['description2'] = request.form.get('about_description2')
        site_content['about']['stats']['clients'] = int(request.form.get('stats_clients', 0))
        site_content['about']['stats']['projects'] = int(request.form.get('stats_projects', 0))
        site_content['about']['stats']['years'] = int(request.form.get('stats_years', 0))

        if save_json_data('site_content.json', site_content):
            flash('Site content updated successfully!', 'success')
            return redirect(url_for('admin_site_content'))
        else:
            flash('Error updating site content.', 'error')

    return render_template('admin/site_content.html', site_content=site_content)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)