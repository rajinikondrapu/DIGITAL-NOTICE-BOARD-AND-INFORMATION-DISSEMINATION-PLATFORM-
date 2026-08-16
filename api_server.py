"""
Digital Notice Board REST API Server
Provides endpoints for notice management, user management, and analytics
"""

from flask import Flask, request, jsonify
from datetime import datetime
import uuid
import json
from notice_board_system import (
    NoticeBoardSystem, User, Notice, UserRole, 
    NoticeCategory, NoticePriority
)

app = Flask(__name__)
system = NoticeBoardSystem()

# Error handling
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


# User Management Endpoints

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    users = [user.to_dict() for user in system.users.values()]
    return jsonify({"users": users, "count": len(users)}), 200


@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get specific user"""
    if user_id not in system.users:
        return jsonify({"error": "User not found"}), 404
    return jsonify(system.users[user_id].to_dict()), 200


@app.route('/api/users', methods=['POST'])
def create_user():
    """Create new user"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['name', 'email', 'role', 'department']):
        return jsonify({"error": "Missing required fields"}), 400
    
    user_id = str(uuid.uuid4())[:8]
    user = User(
        user_id=user_id,
        name=data['name'],
        email=data['email'],
        role=UserRole[data['role'].upper()],
        department=data['department'],
        academic_year=data.get('academic_year', 1)
    )
    
    if system.add_user(user):
        return jsonify({"user_id": user_id, "message": "User created successfully"}), 201
    return jsonify({"error": "Failed to create user"}), 500


@app.route('/api/users/<user_id>/preferences', methods=['PUT'])
def update_user_preferences(user_id):
    """Update user preferences"""
    if user_id not in system.users:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    user = system.users[user_id]
    
    if 'notification_channels' in data:
        user.notification_channels = data['notification_channels']
    
    if 'preferred_categories' in data:
        system.personalization_engine.user_preferences[user_id] = {
            "preferred_categories": data['preferred_categories']
        }
    
    return jsonify({"message": "Preferences updated"}), 200


# Notice Management Endpoints

@app.route('/api/notices', methods=['GET'])
def get_notices():
    """Get all notices"""
    category = request.args.get('category')
    priority = request.args.get('priority')
    
    notices = list(system.notices.values())
    
    if category:
        notices = [n for n in notices if n.category.value == category]
    if priority:
        notices = [n for n in notices if n.priority.value == int(priority)]
    
    return jsonify({
        "notices": [n.to_dict() for n in notices],
        "count": len(notices)
    }), 200


@app.route('/api/notices/<notice_id>', methods=['GET'])
def get_notice(notice_id):
    """Get specific notice"""
    if notice_id not in system.notices:
        return jsonify({"error": "Notice not found"}), 404
    return jsonify(system.notices[notice_id].to_dict()), 200


@app.route('/api/notices', methods=['POST'])
def create_notice():
    """Create new notice"""
    data = request.get_json()
    
    required_fields = ['title', 'content', 'category', 'priority', 'created_by']
    if not data or not all(k in data for k in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    notice_id = str(uuid.uuid4())[:8]
    notice = Notice(
        notice_id=notice_id,
        title=data['title'],
        content=data['content'],
        category=NoticeCategory[data['category'].upper()],
        priority=NoticePriority[data['priority'].upper()],
        created_by=data['created_by']
    )
    
    if system.publish_notice(notice):
        return jsonify({
            "notice_id": notice_id,
            "message": "Notice published successfully"
        }), 201
    return jsonify({"error": "Failed to publish notice"}), 500


@app.route('/api/notices/<notice_id>/targeting', methods=['PUT'])
def set_notice_targeting(notice_id):
    """Set targeting for a notice"""
    if notice_id not in system.notices:
        return jsonify({"error": "Notice not found"}), 404
    
    data = request.get_json()
    
    system.set_notice_targeting(
        notice_id,
        departments=data.get('departments'),
        academic_years=data.get('academic_years'),
        roles=data.get('roles')
    )
    
    return jsonify({"message": "Targeting updated"}), 200


@app.route('/api/notices/<notice_id>/distribute', methods=['POST'])
def distribute_notice(notice_id):
    """Distribute notice to eligible users"""
    if notice_id not in system.notices:
        return jsonify({"error": "Notice not found"}), 404
    
    result = system.distribute_notice(notice_id)
    return jsonify(result), 200


@app.route('/api/notices/<notice_id>/view', methods=['POST'])
def record_notice_view(notice_id):
    """Record notice view"""
    data = request.get_json()
    
    if not data or 'user_id' not in data:
        return jsonify({"error": "Missing user_id"}), 400
    
    if system.record_user_view(data['user_id'], notice_id):
        return jsonify({"message": "View recorded"}), 200
    return jsonify({"error": "Failed to record view"}), 500


@app.route('/api/notices/<notice_id>/click', methods=['POST'])
def record_notice_click(notice_id):
    """Record notice click"""
    data = request.get_json()
    
    if not data or 'user_id' not in data:
        return jsonify({"error": "Missing user_id"}), 400
    
    if system.record_user_click(data['user_id'], notice_id):
        return jsonify({"message": "Click recorded"}), 200
    return jsonify({"error": "Failed to record click"}), 500


# Category Endpoints

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all notice categories"""
    categories = [cat.value for cat in NoticeCategory]
    return jsonify({"categories": categories}), 200


# Analytics Endpoints

@app.route('/api/analytics/system', methods=['GET'])
def get_system_analytics():
    """Get system-wide analytics"""
    stats = system.get_system_statistics()
    return jsonify(stats), 200


@app.route('/api/analytics/notice/<notice_id>', methods=['GET'])
def get_notice_analytics(notice_id):
    """Get analytics for specific notice"""
    if notice_id not in system.notices:
        return jsonify({"error": "Notice not found"}), 404
    
    analytics = system.get_notice_analytics(notice_id)
    return jsonify(analytics), 200


@app.route('/api/analytics/engagement', methods=['GET'])
def get_engagement_analytics():
    """Get engagement analytics"""
    total_views = sum(system.engagement_tracker.view_counts.values())
    total_clicks = sum(system.engagement_tracker.click_counts.values())
    
    avg_engagement_rate = 0.0
    if total_views > 0:
        avg_engagement_rate = (total_clicks / total_views) * 100
    
    return jsonify({
        "total_views": total_views,
        "total_clicks": total_clicks,
        "average_engagement_rate": avg_engagement_rate
    }), 200


@app.route('/api/analytics/notifications', methods=['GET'])
def get_notification_analytics():
    """Get notification delivery analytics"""
    return jsonify({
        "notifications_sent": system.notification_engine.notifications_sent,
        "notifications_failed": system.notification_engine.notifications_failed,
        "delivery_success_rate": system.notification_engine.get_delivery_success_rate(),
        "average_delivery_time_ms": system.notification_engine.get_average_delivery_time() * 1000
    }), 200


# Health Check Endpoint

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "users": len(system.users),
        "notices": len(system.notices)
    }), 200


# Statistics Endpoint

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get comprehensive statistics"""
    stats = system.get_system_statistics()
    
    # Add category distribution
    category_distribution = {}
    for notice in system.notices.values():
        cat = notice.category.value
        category_distribution[cat] = category_distribution.get(cat, 0) + 1
    
    # Add priority distribution
    priority_distribution = {}
    for notice in system.notices.values():
        pri = notice.priority.value
        priority_distribution[str(pri)] = priority_distribution.get(str(pri), 0) + 1
    
    # Add user role distribution
    role_distribution = {}
    for user in system.users.values():
        role = user.role.value
        role_distribution[role] = role_distribution.get(role, 0) + 1
    
    stats.update({
        "category_distribution": category_distribution,
        "priority_distribution": priority_distribution,
        "role_distribution": role_distribution
    })
    
    return jsonify(stats), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
